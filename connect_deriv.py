#!/usr/bin/env python3
"""Direct connection to Deriv API for live trading"""

import asyncio
import websockets
import json
import sys
sys.path.append('./backend')

from ai_predictor_simple import EnhancedPredictor
from collections import deque

class DerivLiveTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.ai = EnhancedPredictor()
        self.digits = deque(maxlen=100)
        self.prices = deque(maxlen=100)
        self.balance = 0
        self.is_trading = True
        
    async def connect(self):
        """Connect to Deriv WebSocket"""
        try:
            self.ws = await websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")
            
            # Authorize
            auth_msg = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_msg))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if "error" in auth_data:
                print(f"❌ Authorization failed: {auth_data['error']}")
                return False
                
            print("✅ Connected to Deriv API")
            print(f"👤 Account: {auth_data.get('authorize', {}).get('email', 'Demo')}")
            
            # Get balance
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            print(f"💰 Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def subscribe_ticks(self):
        """Subscribe to R_100 ticks"""
        tick_msg = {"ticks": "R_100", "subscribe": 1}
        await self.ws.send(json.dumps(tick_msg))
        print("📊 Subscribed to Volatility 100 ticks")
    
    async def place_trade(self, digit, contract_type, stake):
        """Place a digit trade"""
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": contract_type,
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": str(digit)
            }
        }
        
        await self.ws.send(json.dumps(trade_msg))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def run_trading(self):
        """Main trading loop"""
        print("🎯 Starting AI trading...")
        
        while self.is_trading:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                # Handle tick data
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.prices.append(price)
                    self.digits.append(current_digit)
                    
                    print(f"📈 Tick: {price:.5f} | Digit: {current_digit}")
                    
                    # Get AI prediction (need at least 20 data points)
                    if len(self.digits) >= 20:
                        prediction = self.ai.get_comprehensive_prediction(
                            list(self.digits), 
                            list(self.prices), 
                            self.balance, 
                            1.0
                        )
                        
                        print(f"🧠 AI: Digit={prediction['predicted_digit']}, "
                              f"Conf={prediction['final_confidence']:.1f}%, "
                              f"Trade={prediction['should_trade']}")
                        
                        # Trade if conditions met
                        if (prediction['should_trade'] and 
                            prediction['final_confidence'] >= 70 and
                            current_digit == prediction['predicted_digit']):
                            
                            stake = min(prediction['optimal_stake'], 2.0)
                            if stake > 0:
                                print(f"🎯 PLACING TRADE: ${stake} on digit {prediction['predicted_digit']}")
                                
                                result = await self.place_trade(
                                    prediction['predicted_digit'],
                                    "DIGITMATCH",
                                    stake
                                )
                                
                                if "buy" in result:
                                    print(f"✅ Trade placed: {result['buy']['contract_id']}")
                                else:
                                    print(f"❌ Trade failed: {result}")
                
                # Handle balance updates
                elif "balance" in data:
                    self.balance = data["balance"]["balance"]
                    print(f"💰 Balance updated: ${self.balance}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break

async def main():
    print("🚀 Deriv Live Trading Connection")
    print("=" * 40)
    
    # Get API token
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found in .env file")
        return
    
    trader = DerivLiveTrader(api_token)
    
    if await trader.connect():
        await trader.subscribe_ticks()
        await trader.run_trading()
    else:
        print("❌ Failed to connect to Deriv")

if __name__ == "__main__":
    asyncio.run(main())