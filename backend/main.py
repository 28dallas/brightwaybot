# main.py - Deriv live-ticks + digit matches/differs bot
import asyncio
import json
import logging
import os
import sqlite3
from collections import Counter, deque
from datetime import datetime
from typing import Optional

import numpy as np
import websockets
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

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
    stop_loss: float = 10.0
    take_profit: float = 20.0
    confidence_threshold: float = 20.0  # percent bias (0-100)
    min_bias_count: int = 6  # minimum occurrences in recent window to act


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

    def decide_digit(self, analysis):
        """
        Decide which digit to target based on strategy.
        Returns (chosen_digit:int, contract_type:str)
        """
        if self.config.strategy.lower() == "matches":
            chosen = int(analysis["most_frequent"]["digit"])
            contract_type = "DIGITMATCH"
        else:
            chosen = int(analysis["least_frequent"]["digit"])
            contract_type = "DIGITDIFF"
        return chosen, contract_type

    async def place_trade(self, analysis, current_digit):
        if not self.should_trade(analysis, current_digit):
            return None
        contract_type = "DIGITMATCH"  # Only use DIGITMATCH
        result = await self.client.place_digits_trade(
            self.config.selected_number,
            contract_type,
            self.config.stake,
            self.config.duration
        )
        # Calculate profit/loss from result (update this logic based on your actual API response)
        profit = 0.0
        if result and "buy" in result and "payout" in result["buy"] and "ask_price" in result["buy"]:
            profit = float(result["buy"]["payout"]) - float(result["buy"]["ask_price"])
        self.pnl += profit
        # Save trade to DB
        conn = sqlite3.connect('volatility_data.db')
        cursor = conn.cursor()
        now = datetime.utcnow()
        cursor.execute(
            "INSERT INTO trades (timestamp, strategy, prediction, stake, result, profit) VALUES (?, ?, ?, ?, ?, ?)",
            (now, self.config.strategy, json.dumps(analysis), self.config.stake, json.dumps(result), profit)
        )
        conn.commit()
        conn.close()
        # Stop trading if stop loss or take profit is reached
        if self.pnl <= -self.config.stop_loss or self.pnl >= self.config.take_profit:
            self.running = False
        # Fetch real balance from Deriv
        real_balance = await self.client.get_balance()
        return {"trade_result": result, "real_balance": real_balance}


trading_bot = TradingBot()


# -----------------------
# Decision & trading helper (called after each tick)
# -----------------------
async def decide_and_maybe_trade(price, ts, current_digit):
    """
    Called on each tick (from Deriv listener). Decides whether to trade and executes.
    Behavior per your request:
      - When strategy 'matches' -> choose most frequent digit.
      - If the current tick's last digit equals chosen digit -> place DIGITMATCH (bets next tick will match).
      - Use confidence thresholds and min_bias_count to avoid weak edges.
    """
    # Broadcast will be handled by WS endpoint; here we run decision & trade
    analysis = tracker.get_frequency_analysis(recent_window=50)
    if not analysis:
        return

    # Risk check
    if not trading_bot.check_risk_limits():
        logging.info("Risk limits hit: trading stopped.")
        return

    # Determine chosen digit & contract type
    chosen_digit, contract_type = trading_bot.decide_digit(analysis)

    # Confidence and bias checks
    confidence = analysis.get("confidence", 0)
    recent_counts = analysis.get("recent_counts", {})
    chosen_count = recent_counts.get(chosen_digit, 0) if isinstance(recent_counts, dict) else 0

    # Only trade when confidence above threshold AND chosen digit appears at least min_bias_count times in window
    if confidence < trading_bot.config.confidence_threshold or chosen_count < trading_bot.config.min_bias_count:
        return

    # Per your rule: trade only when the current tick's last digit equals chosen_digit
    if current_digit != chosen_digit:
        return

    # Place trade (ephemeral ws)
    result = await deriv_client.place_digits_trade(chosen_digit, contract_type, trading_bot.config.stake, trading_bot.config.duration)
    if not result:
        logging.warning("Trade request failed or returned no response.")
        return

    # Parse result to compute profit/loss (structure varies between simulated & real responses)
    profit = 0.0
    win = False
    try:
        if result.get("simulated"):
            buy = result.get("buy", {})
            profit = float(buy.get("payout", 0.0)) - float(buy.get("ask_price", trading_bot.config.stake))
            win = bool(buy.get("win", False))
        else:
            # derive from buy object
            buy = result.get("buy") or result
            payout = float(buy.get("payout", 0.0)) if buy.get("payout") else 0.0
            ask_price = float(buy.get("ask_price", trading_bot.config.stake)) if buy.get("ask_price") else trading_bot.config.stake
            profit = payout - ask_price
            win = profit > 0
    except Exception as e:
        logging.error(f"Error parsing trade result: {e}")

    # update bot stats
    trading_bot.pnl += profit
    trading_bot.total_trades += 1
    if win:
        trading_bot.wins += 1
    else:
        trading_bot.losses += 1

    # persist trade
    conn = sqlite3.connect("volatility_data.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO trades (timestamp, strategy, chosen_digit, stake, duration, result, profit) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (datetime.utcnow(), trading_bot.config.strategy, chosen_digit, trading_bot.config.stake, trading_bot.config.duration, json.dumps(result), profit),
    )
    conn.commit()
    conn.close()

    logging.info(f"Trade placed. Digit: {chosen_digit}, contract: {contract_type}, profit: {profit}, pnl: {trading_bot.pnl}")


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
            balance = await deriv_client.refresh_balance_once() if deriv_client.api_token else deriv_client.balance

            payload = {
                "type": "update",
                "price": last_price,
                "timestamp": last_ts,
                "last_digit": last_digit,
                "analysis": analysis,
                "is_trading": trading_bot.is_trading,
                "balance": balance,
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
    # Nothing automatic here. We'll connect on start_trading endpoint to avoid auto-live on backend boot.
    logging.info("API server started. Call /api/trading/start to begin live ticks & trading.")


# -----------------------
# Run locally
# -----------------------
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
