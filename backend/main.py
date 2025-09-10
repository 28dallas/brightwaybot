from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import asyncio
import json
import sqlite3
from datetime import datetime
from collections import deque, Counter
import numpy as np
import os
from dotenv import load_dotenv
import websockets
import logging


load_dotenv()
logging.basicConfig(level=logging.INFO)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



class TradingConfig(BaseModel):
    stake: float = 1.0
    duration: int = 5
    strategy: str = 'matches'  # 'matches' or 'differs'
    selected_number: int = 5  # User selected number 0-9
    stop_loss: float = 10.0
    take_profit: float = 20.0
    confidence_threshold: float = 60.0  # Only trade if confidence > this

class DerivAPIClient:
    def __init__(self, api_token=None, app_id=1089):
        self.api_token = api_token or os.getenv('DERIV_API_TOKEN')
        self.app_id = app_id
        self.ws = None
        self.is_connected = False
        self.balance = 0.0
        
    async def connect(self):
        if not self.api_token:
            logging.warning("No Deriv API token provided - using simulation mode")
            return False
            
        try:
            self.ws = await websockets.connect(f"wss://ws.binaryws.com/websockets/v3?app_id={self.app_id}")
            
            # Authorize
            auth_request = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_request))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if auth_data.get('authorize'):
                self.is_connected = True
                self.balance = auth_data['authorize']['balance']
                logging.info("Connected to Deriv API successfully")
                return True
            else:
                logging.error(f"Deriv API authorization failed: {auth_data}")
                return False
                
        except Exception as e:
            logging.error(f"Failed to connect to Deriv API: {e}")
            return False

class VolatilityTracker:
    def __init__(self, max_ticks=500):
        self.max_ticks = max_ticks
        self.digits = deque(maxlen=max_ticks)
        self.prices = deque(maxlen=max_ticks)
        self.timestamps = deque(maxlen=max_ticks)
        self.connected_clients = set()
        
    def add_tick(self, price, timestamp):
        last_digit = int(str(price).replace('.', '')[-1])
        self.digits.append(last_digit)
        self.prices.append(price)
        self.timestamps.append(timestamp)
        
    def get_frequency_analysis(self):
        if not self.digits:
            return {}
            
        counter = Counter(self.digits)
        total = len(self.digits)
        
        frequencies = {str(i): counter.get(i, 0) for i in range(10)}
        percentages = {k: (v/total)*100 if total > 0 else 0 for k, v in frequencies.items()}
        
        most_frequent = max(frequencies.items(), key=lambda x: x[1])
        least_frequent = min(frequencies.items(), key=lambda x: x[1])
        
        return {
            'frequencies': frequencies,
            'percentages': percentages,
            'most_frequent': {'digit': most_frequent[0], 'count': most_frequent[1]},
            'least_frequent': {'digit': least_frequent[0], 'count': least_frequent[1]},
            'total_ticks': total,
            'prediction': self.get_prediction()
        }
    
    def get_prediction(self):
        if len(self.digits) < 10:
            return {'matches': '5', 'differs': '5', 'confidence': 0}
            
        recent_digits = list(self.digits)[-50:]
        counter = Counter(recent_digits)
        
        most_likely = max(counter.items(), key=lambda x: x[1])[0]
        least_likely = min(counter.items(), key=lambda x: x[1])[0]
        
        confidence = (max(counter.values()) - min(counter.values())) / len(recent_digits) * 100
        
        return {
            'matches': str(most_likely),
            'differs': str(least_likely),
            'confidence': round(confidence, 2)
        }

class TradingBot:
    def __init__(self):
        self.config = TradingConfig()
        self.client = DerivAPIClient()
        self.running = False
        self.pnl = 0.0
        self.trades = []

    def should_trade(self, analysis, current_digit):
        # Only trade if confidence is above threshold and digit matches selected number
        if self.pnl <= -self.config.stop_loss or self.pnl >= self.config.take_profit:
            self.running = False
            return False
        return (
            analysis["confidence"] >= self.config.confidence_threshold
            and analysis["digit"] == self.config.selected_number
        )

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
        return result

tracker = VolatilityTracker()
trading_bot = TradingBot()

def init_db():
    conn = sqlite3.connect('volatility_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            price REAL,
            last_digit INTEGER
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME,
            strategy TEXT,
            prediction TEXT,
            stake REAL,
            result TEXT,
            profit REAL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    tracker.connected_clients.add(websocket)
    
    try:
        while True:
            # Generate realistic volatility data
            base_price = 1000 + np.random.normal(0, 50)
            price = round(base_price + np.random.normal(0, 10), 5)
            timestamp = datetime.now().isoformat()
            current_digit = int(str(price).replace('.', '')[-1])
            
            tracker.add_tick(price, timestamp)
            
            conn = sqlite3.connect('volatility_data.db')
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO ticks (timestamp, price, last_digit) VALUES (?, ?, ?)",
                (timestamp, price, current_digit)
            )
            conn.commit()
            conn.close()
            
            analysis = tracker.get_frequency_analysis()
            
            data = {
                'type': 'tick',
                'price': price,
                'timestamp': timestamp,
                'last_digit': current_digit,
                'analysis': analysis,
                'trading_status': trading_bot.is_trading,
                'balance': trading_bot.balance,
                'total_profit': trading_bot.total_profit,
                'selected_number': trading_bot.config.selected_number,
                'strategy': trading_bot.config.strategy,
                'trades_today': trading_bot.trades_today,
                'wins': trading_bot.wins,
                'losses': trading_bot.losses
            }
            
            # Auto-trade if enabled
            if trading_bot.is_trading:
                trade_result = await trading_bot.place_trade(analysis, current_digit)
                if trade_result:
                    data['trade_executed'] = trade_result
                    logging.info(f"Trade notification sent to frontend: {trade_result}")
            
            # Send to all connected clients
            disconnected = set()
            for client in tracker.connected_clients:
                try:
                    await client.send_text(json.dumps(data))
                except:
                    disconnected.add(client)
            
            tracker.connected_clients -= disconnected
            await asyncio.sleep(1)  # 1 second interval
            
    except WebSocketDisconnect:
        tracker.connected_clients.discard(websocket)

@app.post("/api/trading/config")
async def update_trading_config(config: dict):
    # Validate selected_number
    if 'selected_number' in config:
        if not isinstance(config['selected_number'], int) or not (0 <= config['selected_number'] <= 9):
            return {"status": "error", "message": "selected_number must be between 0-9"}
    
    # Update config
    for key, value in config.items():
        if hasattr(trading_bot.config, key):
            setattr(trading_bot.config, key, value)
    
    logging.info(f"Trading config updated: {trading_bot.config.dict()}")
    return {"status": "success", "config": trading_bot.config.dict()}

@app.post("/api/trading/start")
async def start_trading():
    # Try to connect to Deriv API
    await trading_bot.connect_to_deriv()
    trading_bot.is_trading = True
    
    mode = "Live Trading" if trading_bot.deriv_client.is_connected else "Simulation Mode"
    logging.info(f"Trading started in {mode}")
    return {"status": "success", "message": f"Trading started in {mode}"}

@app.post("/api/trading/stop")
async def stop_trading():
    trading_bot.is_trading = False
    logging.info("Trading stopped")
    return {"status": "success", "message": "Trading stopped"}

@app.get("/api/history")
async def get_history():
    conn = sqlite3.connect('volatility_data.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ticks ORDER BY timestamp DESC LIMIT 1000")
    ticks = cursor.fetchall()
    cursor.execute("SELECT * FROM trades ORDER BY timestamp DESC LIMIT 100")
    trades = cursor.fetchall()
    conn.close()
    
    return {
        "ticks": [{"id": t[0], "timestamp": t[1], "price": t[2], "last_digit": t[3]} for t in ticks],
        "trades": [{"id": t[0], "timestamp": t[1], "strategy": t[2], "prediction": t[3], 
                   "stake": t[4], "result": t[5], "profit": t[6]} for t in trades]
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)