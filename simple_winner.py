#!/usr/bin/env python3
"""SIMPLE WINNER - Focus on reliable profits"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque

class SimpleWinner:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.digits = deque(maxlen=30)
        
    async def connect(self):
        try:
            self.ws = await websockets.connect(
                "wss://ws.derivws.com/websockets/v3?app_id=1089",
                ping_interval=20,
                ping_timeout=10
            )
            
            auth_msg = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_msg))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if "error" in auth_data:
                print(f"❌ Authorization failed: {auth_data['error']}")
                return False
                
            print("🚀 SIMPLE WINNER CONNECTED")
            
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
    
    def should_trade(self):
        """Simple logic: trade when digit appears 5+ times in last 15 ticks"""
        if len(self.digits) < 15:
            return None
        
        recent = list(self.digits)[-15:]
        counts = {}
        for d in recent:
            counts[d] = counts.get(d, 0) + 1
        
        # Find most frequent digit
        most_frequent = max(counts, key=counts.get)
        frequency = counts[most_frequent]
        
        # Trade if digit appears 5+ times (33%+ frequency)
        if frequency >= 5 and most_frequent != 0:
            return most_frequent
        
        return None
    
    async def place_trade(self, digit):
        """Place DIFFERS trade"""
        trade_msg = {
            "buy": 1,
            "price": 0.35,
            "parameters": {
                "amount": 0.35,
                "basis": "stake",
                "contract_type": "DIGITDIFF",
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": str(digit)
            }
        }
        
        try:
            await self.ws.send(json.dumps(trade_msg))
            response = await self.ws.recv()
            result = json.loads(response)
            
            if "buy" in result:
                print(f"🚀 TRADE: DIFFERS on digit {digit} (appeared 5+ times)")
                return True
            else:
                print(f"❌ Trade failed: {result.get('error', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return False
    
    async def run_system(self):
        """Run simple winning system"""
        print("🚀 STARTING SIMPLE WINNER")
        print("🎯 Strategy: DIFFERS on frequent digits")
        print("📊 Logic: Trade when digit appears 5+ times in 15 ticks")
        
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        last_trade_tick = 0
        
        while self.is_trading and self.wins < 2:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.digits.append(current_digit)
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Check if we should trade (wait 5 ticks between trades)
                    if tick_count - last_trade_tick >= 5:
                        target_digit = self.should_trade()
                        
                        if target_digit:
                            self.trades_made += 1
                            last_trade_tick = tick_count
                            
                            print(f"🎯 TRADING OPPORTUNITY: Digit {target_digit} is frequent")
                            success = await self.place_trade(target_digit)
                            
                            if success:
                                await asyncio.sleep(2)  # Wait for result
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                            
                            if self.wins >= 2:
                                print("🎉 2 WINS - SUCCESS!")
                                self.is_trading = False
                        else:
                            print(f"💔 LOSS: ${profit:.2f} | Total: ${total_profit:.2f}")
                            if total_profit <= -1.0:
                                print("🛡️ STOPPING - Loss limit reached")
                                self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Waiting for opportunities...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 SIMPLE WINNER COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Result: ${final_profit:.2f}")

async def main():
    print("🎯 SIMPLE WINNER SYSTEM")
    print("=" * 30)
    print("📊 Strategy: DIFFERS on frequent digits")
    print("🎯 Target: 2 wins")
    print("🛡️ Stop: -$1.00 loss")
    print("=" * 30)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = SimpleWinner(api_token)
    
    if await trader.connect():
        await trader.run_system()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())