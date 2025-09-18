#!/usr/bin/env python3
"""INSTANT TRADER - Trades immediately on common digits"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter

class InstantTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.digits = deque(maxlen=20)
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
                
            print("⚡ INSTANT TRADER READY")
            
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
    
    def get_hot_digit(self):
        """Get the most frequent digit from recent data"""
        if len(self.digits) < 10:
            return 5  # Default to 5 (statistically common)
        
        counter = Counter(self.digits)
        most_common = counter.most_common(1)[0][0]
        return most_common
    
    async def place_instant_trade(self, digit):
        """Place trade immediately"""
        stake = 0.50
        
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
        
        await self.ws.send(json.dumps(trade_msg))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def run_instant_trading(self):
        """Trade on every 5th tick"""
        print("⚡ STARTING INSTANT TRADING")
        print("🎯 Trades on most frequent digit")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        
        while self.is_trading and self.trades_made < 6:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.digits.append(current_digit)
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Trade every 5th tick after we have 10 data points
                    if len(self.digits) >= 10 and tick_count % 5 == 0:
                        hot_digit = self.get_hot_digit()
                        self.trades_made += 1
                        
                        print(f"🔥 INSTANT TRADE #{self.trades_made}: $0.50 on HOT digit {hot_digit}")
                        print(f"   Recent digits: {list(self.digits)[-10:]}")
                        
                        result = await self.place_instant_trade(hot_digit)
                        
                        if "buy" in result:
                            print(f"✅ TRADE PLACED: {result['buy']['contract_id']}")
                        elif "error" in result:
                            print(f"❌ Error: {result['error']['message']}")
                        else:
                            print(f"❌ Unknown response: {result}")
                
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
                    if self.wins >= 3:
                        print("🎉 3 WINS - MISSION ACCOMPLISHED!")
                        self.is_trading = False
                    elif total_profit <= -2.0:
                        print("⚠️ $2 LOSS LIMIT - STOPPING")
                        self.is_trading = False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 INSTANT TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit > 0:
            print("🎉 PROFIT ACHIEVED! 💰")
        else:
            print("📈 Learning experience - try again!")

async def main():
    print("⚡ INSTANT TRADER - GUARANTEED ACTION")
    print("=" * 40)
    print("🔥 Trades on HOT digits (most frequent)")
    print("⏰ Every 5th tick")
    print("🎯 Target: 3 wins")
    print("🛑 Stop: $2 loss")
    print("=" * 40)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = InstantTrader(api_token)
    
    if await trader.connect():
        await trader.run_instant_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())