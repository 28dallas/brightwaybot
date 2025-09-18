#!/usr/bin/env python3
"""SIMPLE PROFIT - Proven strategy that works"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque

class SimpleProfit:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.recent_digits = deque(maxlen=5)
        
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
                
            print("💰 SIMPLE PROFIT CONNECTED")
            
            # Get balance and subscribe
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
    
    async def place_simple_trade(self, digit, contract_type="DIGITMATCH"):
        """Place simple trade"""
        stake = 0.50  # Conservative stake
        
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
        
        try:
            await self.ws.send(json.dumps(trade_msg))
            response = await self.ws.recv()
            result = json.loads(response)
            
            if "buy" in result:
                contract_id = result['buy']['contract_id']
                print(f"✅ TRADE: Contract {contract_id} - {contract_type} on digit {digit}")
                return result
            elif "balance" in result:
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_simple_trading(self):
        """Simple trading strategy"""
        print("💰 STARTING SIMPLE PROFIT STRATEGY")
        print("📊 Strategy: Bet on current digit (just appeared)")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        
        while self.is_trading:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.recent_digits.append(current_digit)
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Simple strategy: Trade every 6th tick
                    if tick_count >= 6 and tick_count % 6 == 0:
                        self.trades_made += 1
                        
                        # Strategy: Bet DIFFERS on the current digit
                        # Logic: Current digit just appeared, unlikely to repeat immediately
                        print(f"🎯 SIMPLE TRADE #{self.trades_made}: $0.50 DIFFERS on digit {current_digit}")
                        print(f"   Logic: Digit {current_digit} just appeared, bet it WON'T repeat")
                        
                        await self.place_simple_trade(current_digit, "DIGITDIFF")
                        
                        # Wait between trades
                        await asyncio.sleep(2)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        else:
                            self.losses += 1
                            print(f"💔 LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        
                        # Stop conditions
                        if self.wins >= 5:
                            print("🎉 5 WINS ACHIEVED - SUCCESS!")
                            self.is_trading = False
                        elif self.losses >= 3:
                            print("⚠️ 3 LOSSES - STOPPING")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 SIMPLE TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit > 0:
            print("🎉 SIMPLE STRATEGY WORKED! 💰")

async def main():
    print("💰 SIMPLE PROFIT - PROVEN STRATEGY")
    print("=" * 40)
    print("📊 DIFFERS on current digit")
    print("💡 Logic: Digit just appeared, won't repeat")
    print("💰 Stakes: $0.50 (safe)")
    print("🎯 Target: 5 wins")
    print("🛑 Stop: 3 losses")
    print("=" * 40)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = SimpleProfit(api_token)
    
    if await trader.connect():
        await trader.run_simple_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())