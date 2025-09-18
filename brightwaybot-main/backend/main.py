# main.py - Deriv live-ticks + digit matches/differs bot
import asyncio
import json
import logging
import os
import sqlite3
import random
from collections import Counter, deque
from datetime import datetime
from typing import Optional

import numpy as np
import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ai_predictor_simple import EnhancedPredictor
from advanced_ai import UltraAdvancedPredictor

load_dotenv()
logging.basicConfig(level=logging.INFO)

# -----------------------
# Constants / Settings
# -----------------------
DERIV_WS_URL = "wss://ws.binaryws.com/websockets/v3"
APP_ID = 1089
SYMBOL = "R_100"  # Volatility 100 index symbol
TICKS_HISTORY = 500

# -----------------------
# FastAPI app
# -----------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------
# Models
# -----------------------
class TradingConfig(BaseModel):
    stake: float = 1.0
    duration: int = 1  # ticks (1 means bet next tick)
    strategy: str = "matches"  # 'matches' or 'differs'
    selected_number: int = 5  # user's chosen digit (0-9)
    stop_loss: float = 10.0
    take_profit: float = 20.0
    confidence_threshold: float = 60.0  # percent bias (0-100)
    min_bias_count: int = 6  # minimum occurrences in recent window to act
    use_ai_prediction: bool = True  # Use AI prediction instead of selected number
    auto_stake_sizing: bool = True  # Use Kelly criterion for stake sizing


# -----------------------
# Database init
# -----------------------
def init_db():
    conn = sqlite3.connect("volatility_data.db")
    cursor = conn.cursor()
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            price REAL,
            last_digit INTEGER
        )
    """
    )
    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            strategy TEXT,
            chosen_digit INTEGER,
            stake REAL,
            duration INTEGER,
            result TEXT,
            profit REAL
        )
    """
    )
    conn.commit()
    conn.close()


init_db()


# -----------------------
# Volatility tracker (local)
# -----------------------
class VolatilityTracker:
    def __init__(self, max_ticks=TICKS_HISTORY):
        self.max_ticks = max_ticks
        self.digits = deque(maxlen=max_ticks)
        self.prices = deque(maxlen=max_ticks)
        self.timestamps = deque(maxlen=max_ticks)
        self.clients = set()

    def add_tick(self, price: float, timestamp: str):
        last_digit = int(str(price).replace(".", "")[-1])
        self.digits.append(last_digit)
        self.prices.append(price)
        self.timestamps.append(timestamp)
        # persist
        conn = sqlite3.connect("volatility_data.db")
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ticks (timestamp, price, last_digit) VALUES (?, ?, ?)",
            (timestamp, price, last_digit),
        )
        conn.commit()
        conn.close()

    def get_frequency_analysis(self, recent_window=50):
        if not self.digits:
            return {}

        total = len(self.digits)
        counter_all = Counter(self.digits)
        frequencies = {str(i): counter_all.get(i, 0) for i in range(10)}
        percentages = {k: (v / total) * 100 if total > 0 else 0 for k, v in frequencies.items()}

        # Recent window bias
        recent_digits = list(self.digits)[-recent_window:] if total >= 1 else list(self.digits)
        counter_recent = Counter(recent_digits) if recent_digits else Counter()
        if counter_recent:
            most_likely, most_count = max(counter_recent.items(), key=lambda x: x[1])
            least_likely, least_count = min(counter_recent.items(), key=lambda x: x[1])
            confidence = (most_count - least_count) / max(1, len(recent_digits)) * 100
        else:
            most_likely, most_count, least_likely, least_count, confidence = 5, 0, 5, 0, 0

        return {
            "frequencies": frequencies,
            "percentages": percentages,
            "most_frequent": {"digit": most_likely, "count": most_count},
            "least_frequent": {"digit": least_likely, "count": least_count},
            "total_ticks": total,
            "confidence": round(confidence, 2),
            "recent_window": len(recent_digits),
            "recent_counts": dict(counter_recent),
        }


tracker = VolatilityTracker()
ai_predictor = EnhancedPredictor()
ultra_ai = UltraAdvancedPredictor()


# -----------------------
# Deriv API client
# -----------------------
class DerivAPIClient:
    def __init__(self, api_token=None, app_id=1089):
        self.api_token = api_token or os.getenv('DERIV_API_TOKEN')
        self.app_id = app_id
        self.ws = None
        self.is_connected = False
        self.balance = 0.0

    async def connect(self):
        if not self.api_token:
            logging.error("No API token provided for Deriv connection.")
            return False
        try:
            self.ws = await websockets.connect(f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}")
            await self.ws.send(json.dumps({"authorize": self.api_token}))
            response = await self.ws.recv()
            data = json.loads(response)
            if "error" in data:
                logging.error(f"Authorization error: {data['error']}")
                return False
            self.is_connected = True
            logging.info("Connected to Deriv API successfully.")
            return True
        except Exception as e:
            logging.error(f"Failed to connect to Deriv API: {e}")
            return False

    async def get_ticks(self, symbol="R_100"):
        if not self.is_connected:
            await self.connect()
        try:
            await self.ws.send(json.dumps({"ticks": symbol, "subscribe": 1}))
            while True:
                response = await self.ws.recv()
                data = json.loads(response)
                if "tick" in data:
                    yield data["tick"]
        except Exception as e:
            logging.error(f"Error getting ticks: {e}")

    async def place_digits_trade(self, digit, contract_type, stake, duration):
        if not self.is_connected:
            await self.connect()
        proposal = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": contract_type.upper(),  # "DIGITMATCH"
                "currency": "USD",
                "duration": duration,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": str(digit)
            }
        }
        try:
            await self.ws.send(json.dumps(proposal))
            response = await self.ws.recv()
            data = json.loads(response)
            if "error" in data:
                logging.error(f"Trade error: {data['error']}")
                return None
            return data
        except Exception as e:
            logging.error(f"Error placing trade: {e}")
            return None

    async def get_balance(self):
        if not self.is_connected:
            await self.connect()
        await self.ws.send(json.dumps({"balance": 1, "subscribe": 0}))
        response = await self.ws.recv()
        data = json.loads(response)
        if "balance" in data:
            return data["balance"]["balance"]
        return None

    async def refresh_balance_once(self):
        """Get current balance without subscription"""
        try:
            return await self.get_balance()
        except:
            return self.balance

    async def connect_and_subscribe_ticks(self):
        """Connect to Deriv API and start tick subscription"""
        if await self.connect():
            # Start background task to process ticks
            asyncio.create_task(self._process_ticks())
            return True
        return False

    async def _process_ticks(self):
        """Background task to process incoming ticks"""
        async for tick_data in self.get_ticks():
            price = float(tick_data.get("quote", 0))
            timestamp = tick_data.get("epoch")
            if price and timestamp:
                # Add to tracker
                tracker.add_tick(price, datetime.fromtimestamp(timestamp).isoformat())
                # Check for trading opportunity
                last_digit = int(str(price).replace(".", "")[-1])
                await decide_and_maybe_trade(price, timestamp, last_digit)


deriv_client = DerivAPIClient()


# -----------------------
# Trading Bot logic & state
# -----------------------
class TradingBot:
    def __init__(self):
        self.config = TradingConfig()
        self.is_trading = False
        self.pnl = 0.0
        self.total_trades = 0
        self.wins = 0
        self.losses = 0

    def check_risk_limits(self):
        if self.pnl <= -self.config.stop_loss or self.pnl >= self.config.take_profit:
            self.is_trading = False
            return False
        return True

    def get_contract_type(self):
        """
        Get contract type based on strategy.
        """
        if self.config.strategy.lower() == "matches":
            return "DIGITMATCH"
        else:
            return "DIGITDIFF"

    def should_trade(self, ai_prediction, current_digit):
        """
        Check if we should trade based on AI prediction or selected number.
        """
        if self.config.use_ai_prediction:
            # Use AI prediction
            predicted_digit = ai_prediction['predicted_digit']
            confidence = ai_prediction['final_confidence']
            should_trade_ai = ai_prediction['should_trade']
            
            return (current_digit == predicted_digit and 
                   confidence >= self.config.confidence_threshold and 
                   should_trade_ai)
        else:
            # Use selected number (original logic)
            return current_digit == self.config.selected_number
    
    def get_trade_stake(self, ai_prediction):
        """
        Get optimal stake size based on AI or fixed amount.
        """
        if self.config.auto_stake_sizing and ai_prediction.get('optimal_stake', 0) > 0:
            return min(ai_prediction['optimal_stake'], self.config.stake * 3)
        return self.config.stake


trading_bot = TradingBot()


# -----------------------
# Decision & trading helper (called after each tick)
# -----------------------
async def decide_and_maybe_trade(price, ts, current_digit):
    """
    Called on each tick. Uses AI prediction or selected number logic.
    """
    if not trading_bot.is_trading:
        return
        
    # Get current balance for AI calculations
    current_balance = await deriv_client.get_balance() or 1000  # Default for demo
    
    # Get AI prediction
    ai_prediction = ai_predictor.get_comprehensive_prediction(
        list(tracker.digits), 
        list(tracker.prices), 
        current_balance, 
        trading_bot.config.stake
    )
    
    # Get ultra-advanced prediction
    ultra_prediction = ultra_ai.ensemble_prediction(list(tracker.digits), list(tracker.prices))
    
    # Combine predictions for maximum accuracy
    if ultra_prediction['confidence'] > ai_prediction['final_confidence']:
        ai_prediction['predicted_digit'] = ultra_prediction['predicted_digit']
        ai_prediction['final_confidence'] = ultra_ai.adaptive_confidence_adjustment(ultra_prediction['confidence'])
        ai_prediction['optimal_stake'] = ultra_ai.kelly_criterion_advanced(
            ai_prediction['final_confidence'], current_balance, []
        )

    # Risk check
    if not trading_bot.check_risk_limits():
        logging.info("Risk limits hit: trading stopped.")
        return

    # Check if we should trade based on AI or selected number
    if not trading_bot.should_trade(ai_prediction, current_digit):
        return

    # Determine trade parameters
    if trading_bot.config.use_ai_prediction:
        chosen_digit = ai_prediction['predicted_digit']
        stake = trading_bot.get_trade_stake(ai_prediction)
    else:
        chosen_digit = trading_bot.config.selected_number
        stake = trading_bot.config.stake
    
    contract_type = trading_bot.get_contract_type()

    # Don't trade if stake is 0 (AI says no trade)
    if stake <= 0:
        return

    # Place trade
    result = await deriv_client.place_digits_trade(chosen_digit, contract_type, stake, trading_bot.config.duration)
    if not result:
        logging.warning("Trade request failed or returned no response.")
        return

    # Parse result to compute profit/loss
    profit = 0.0
    win = False
    try:
        if result.get("simulated"):
            buy = result.get("buy", {})
            profit = float(buy.get("payout", 0.0)) - float(buy.get("ask_price", stake))
            win = bool(buy.get("win", False))
        else:
            buy = result.get("buy") or result
            payout = float(buy.get("payout", 0.0)) if buy.get("payout") else 0.0
            ask_price = float(buy.get("ask_price", stake)) if buy.get("ask_price") else stake
            profit = payout - ask_price
            win = profit > 0
    except Exception as e:
        logging.error(f"Error parsing trade result: {e}")

    # Update bot stats
    trading_bot.pnl += profit
    trading_bot.total_trades += 1
    if win:
        trading_bot.wins += 1
    else:
        trading_bot.losses += 1

    # Persist trade with AI data
    conn = sqlite3.connect("volatility_data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trades (timestamp, strategy, chosen_digit, stake, duration, result, profit) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow(), trading_bot.config.strategy, chosen_digit, stake, trading_bot.config.duration, json.dumps({**result, 'ai_prediction': ai_prediction}), profit),
    )
    conn.commit()
    conn.close()

    logging.info(f"Trade placed. Digit: {chosen_digit}, contract: {contract_type}, stake: {stake}, confidence: {ai_prediction.get('final_confidence', 0):.1f}%, profit: {profit}, pnl: {trading_bot.pnl}")


# -----------------------
# WebSocket endpoint for frontend (broadcast ticks, analysis, balance, pnl)
# -----------------------
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    tracker.clients.add(websocket)
    logging.info("Frontend connected to WS")
    try:
        while True:
            # Build payload from latest tick & analysis
            # use latest values in tracker
            last_price = tracker.prices[-1] if tracker.prices else None
            last_ts = tracker.timestamps[-1] if tracker.timestamps else None
            last_digit = tracker.digits[-1] if tracker.digits else None
            analysis = tracker.get_frequency_analysis(recent_window=50)

            # refresh balance (non-blocking call but await here to provide latest)
            try:
                balance = await deriv_client.refresh_balance_once() if deriv_client.api_token else deriv_client.balance
            except:
                balance = deriv_client.balance

            # Get AI prediction for frontend
            ai_prediction = None
            if tracker.digits and tracker.prices and len(tracker.digits) > 0:
                try:
                    ai_prediction = ai_predictor.get_comprehensive_prediction(
                        list(tracker.digits), 
                        list(tracker.prices), 
                        balance or 1000, 
                        trading_bot.config.stake
                    )
                except Exception as e:
                    logging.error(f"AI prediction error: {e}")
                    ai_prediction = None
            
            payload = {
                "type": "update",
                "price": last_price or 1206.59000,
                "timestamp": last_ts or datetime.now().isoformat(),
                "last_digit": last_digit if last_digit is not None else 0,
                "analysis": analysis or {},
                "ai_prediction": ai_prediction or {"predicted_digit": 0, "final_confidence": 0.0},
                "is_trading": trading_bot.is_trading,
                "balance": balance or 1322.55,
                "pnl": trading_bot.pnl,
                "total_trades": trading_bot.total_trades,
                "wins": trading_bot.wins,
                "losses": trading_bot.losses,
                "config": trading_bot.config.dict(),
            }

            try:
                await websocket.send_text(json.dumps(payload, default=str))
            except:
                # client likely disconnected
                break

            await asyncio.sleep(1)

    except WebSocketDisconnect:
        pass
    finally:
        try:
            tracker.clients.discard(websocket)
        except:
            pass
        logging.info("Frontend disconnected from WS")


# -----------------------
# REST endpoints
# -----------------------
@app.post("/api/trading/config")
async def update_trading_config(conf: dict):
    # validate and update
    for k, v in conf.items():
        if hasattr(trading_bot.config, k):
            setattr(trading_bot.config, k, v)
    logging.info(f"Config updated: {trading_bot.config.dict()}")
    return {"status": "success", "config": trading_bot.config.dict()}


@app.post("/api/trading/start")
async def start_trading():
    # connect and subscribe to live ticks (if token provided)
    await deriv_client.connect_and_subscribe_ticks()
    trading_bot.is_trading = True
    logging.info(f"Trading started. Live mode: {deriv_client.is_connected}")
    return {"status": "success", "mode": "live" if deriv_client.is_connected else "simulation"}


@app.post("/api/trading/stop")
async def stop_trading():
    trading_bot.is_trading = False
    logging.info("Trading stopped by API")
    return {"status": "success"}


@app.post("/api/trading/demo")
async def start_demo_mode():
    """Start demo mode with simulated ticks"""
    trading_bot.is_trading = True
    # Start background task to generate fake ticks
    asyncio.create_task(generate_demo_ticks())
    logging.info("Demo mode started with simulated ticks")
    return {"status": "success", "mode": "demo"}


async def generate_demo_ticks():
    """Generate fake ticks for demo mode"""
    import random
    base_price = 1206.59000
    
    while trading_bot.is_trading:
        # Generate realistic price movement
        price_change = random.uniform(-0.5, 0.5)
        base_price += price_change
        price = round(base_price, 5)
        
        # Add tick to tracker
        timestamp = datetime.now().isoformat()
        tracker.add_tick(price, timestamp)
        
        # Check for trading opportunity
        last_digit = int(str(price).replace(".", "")[-1])
        await decide_and_maybe_trade_demo(price, timestamp, last_digit)
        
        await asyncio.sleep(1)  # 1 tick per second


async def decide_and_maybe_trade_demo(price, ts, current_digit):
    """Demo version of trading logic"""
    if not trading_bot.is_trading:
        return
        
    # Simple demo logic - trade every 10th tick
    if trading_bot.total_trades % 10 == 0 and len(tracker.digits) > 10:
        # Simulate a trade
        chosen_digit = trading_bot.config.selected_number
        stake = trading_bot.config.stake
        
        # Simulate win/loss (60% win rate)
        win = random.random() < 0.6
        profit = stake * 0.8 if win else -stake
        
        # Update bot stats
        trading_bot.pnl += profit
        trading_bot.total_trades += 1
        if win:
            trading_bot.wins += 1
        else:
            trading_bot.losses += 1
        
        # Log the simulated trade
        logging.info(f"Demo trade: Digit {chosen_digit}, Stake ${stake}, {'WIN' if win else 'LOSS'}, Profit: ${profit:.2f}")


@app.post("/api/ai/train")
async def train_ai_model():
    """Train the AI model with historical data"""
    if len(tracker.digits) < 100:
        return {"status": "error", "message": "Need at least 100 ticks to train model"}
    
    success = ai_predictor.train_model(list(tracker.digits))
    if success:
        return {"status": "success", "message": "AI model trained successfully"}
    else:
        return {"status": "error", "message": "Failed to train AI model"}


@app.get("/api/ai/status")
async def get_ai_status():
    """Get AI model status and accuracy"""
    return {
        "is_trained": ai_predictor.digit_predictor.is_trained,
        "prediction_accuracy": ai_predictor.get_prediction_accuracy(),
        "total_predictions": len(ai_predictor.prediction_history),
        "data_points": len(tracker.digits)
    }


@app.get("/api/history")
async def get_history():
    conn = sqlite3.connect("volatility_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id, timestamp, price, last_digit FROM ticks ORDER BY timestamp DESC LIMIT 1000")
    ticks = cursor.fetchall()
    cursor.execute("SELECT id, timestamp, strategy, chosen_digit, stake, duration, result, profit FROM trades ORDER BY timestamp DESC LIMIT 200")
    trades = cursor.fetchall()
    conn.close()
    return {
        "ticks": [{"id": t[0], "timestamp": t[1], "price": t[2], "last_digit": t[3]} for t in ticks],
        "trades": [
            {"id": tr[0], "timestamp": tr[1], "strategy": tr[2], "chosen_digit": tr[3], "stake": tr[4], "duration": tr[5], "result": tr[6], "profit": tr[7]}
            for tr in trades
        ],
    }


# -----------------------
# App startup: optionally start ephemeral tasks
# -----------------------
@app.on_event("startup")
async def startup_event():
    # Auto-train AI model if we have enough historical data
    conn = sqlite3.connect("volatility_data.db")
    cursor = conn.cursor()
    cursor.execute("SELECT last_digit FROM ticks ORDER BY timestamp DESC LIMIT 1000")
    historical_digits = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    if len(historical_digits) >= 100:
        logging.info(f"Training AI model with {len(historical_digits)} historical data points...")
        ai_predictor.train_model(historical_digits)
    
    logging.info("API server started. Call /api/trading/start to begin live ticks & trading.")


# -----------------------
# Run locally
# -----------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
