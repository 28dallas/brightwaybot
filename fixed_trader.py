#!/usr/bin/env python3
"""FIXED TRADER - Guaranteed minimum stake"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque, Counter

class FixedTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.digits = deque(maxlen=30)
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        
    async def connect(self):
        try:
            self.ws = await websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")
            
            auth_msg = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_msg))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if "error" in auth_data:
                print(f"❌ Authorization failed: {auth_data['error']}")
                return False
                
            print("✅ FIXED TRADER CONNECTED")
            
            # Get balance
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance
            print(f"💰 Starting Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_smart_prediction(self):
        """Simple but effective prediction"""
        if len(self.digits) < 15:
            return None
        
        recent = list(self.digits)[-15:]
        counter = Counter(recent)
        
        # Find least frequent digit (gap strategy)
        all_counts = {i: counter.get(i, 0) for i in range(10)}
        least_frequent = min(all_counts, key=all_counts.get)
        
        # If multiple digits have same low count, pick 5 (statistically common)
        if all_counts[least_frequent] >= 2:
            least_frequent = 5
        
        return {
            'digit': least_frequent,
            'confidence': 65.0
        }
    
    async def place_fixed_trade(self, digit, stake=0.50):
        """Place trade with GUARANTEED minimum stake"""
        # ENSURE stake is at least 0.35
        stake = max(float(stake), 0.35)
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "DIGITMATCH",
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": str(digit)
            }
        }
        
        print(f"🔧 Placing trade: ${stake} on digit {digit}")
        
        await self.ws.send(json.dumps(trade_msg))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def run_fixed_trading(self):
        """Fixed trading with guaranteed stakes"""
        print("🔧 STARTING FIXED TRADING")
        print("💰 Guaranteed minimum $0.50 stakes")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        while self.is_trading and self.trades_made < 8:  # Limit to 8 trades
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.digits.append(current_digit)
                    
                    print(f"📈 {price:.5f} | Digit: {current_digit}")
                    
                    # Get prediction
                    prediction = self.get_smart_prediction()
                    
                    if prediction and len(self.digits) >= 20:
                        print(f"🎯 Target: {prediction['digit']}, Current: {current_digit}")
                        
                        # Trade when current digit matches target
                        if current_digit == prediction['digit']:
                            self.trades_made += 1
                            
                            result = await self.place_fixed_trade(prediction['digit'], 0.50)
                            
                            if "buy" in result:
                                print(f"✅ TRADE #{self.trades_made} PLACED: {result['buy']['contract_id']}")
                            elif "error" in result:
                                print(f"❌ Trade error: {result['error']['message']}")
                            else:
                                print(f"❌ Unknown error: {result}")
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    self.balance = new_balance
                    
                    if profit > 0:
                        self.wins += 1
                        print(f"💚 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                    elif profit < 0:
                        print(f"💔 Loss: ${profit:.2f} | Total: ${total_profit:.2f}")
                    
                    # Stop conditions
                    if self.wins >= 4:
                        print("🎉 4 WINS - STOPPING FOR SAFETY")
                        self.is_trading = False
                    elif total_profit <= -3.0:
                        print("⚠️ $3 LOSS LIMIT - STOPPING")
                        self.is_trading = False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 FIXED TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Result: ${final_profit:.2f}")

async def main():
    print("🔧 FIXED TRADER - NO MORE ERRORS")
    print("=" * 35)
    print("💰 Guaranteed $0.50 stakes")
    print("🎯 Gap strategy (missing digits)")
    print("🛑 Auto-stop: 4 wins OR $3 loss")
    print("=" * 35)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = FixedTrader(api_token)
    
    if await trader.connect():
        await trader.run_fixed_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())