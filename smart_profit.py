#!/usr/bin/env python3
"""SMART PROFIT - Only trades when conditions are perfect"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter

class SmartProfit:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.recent_digits = deque(maxlen=20)
        
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
                
            print("🎯 SMART PROFIT CONNECTED")
            
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
    
    def should_trade(self, current_digit):
        """Only trade when conditions are PERFECT"""
        if len(self.recent_digits) < 15:
            return False, "Need more data"
        
        # Condition 1: Current digit appeared 3+ times in last 15 ticks
        recent_count = self.recent_digits.count(current_digit)
        if recent_count < 3:
            return False, f"Digit {current_digit} only appeared {recent_count} times"
        
        # Condition 2: Current digit appeared in last 3 ticks
        last_3 = list(self.recent_digits)[-3:]
        if current_digit not in last_3:
            return False, f"Digit {current_digit} not in last 3 ticks"
        
        # Condition 3: Current digit is "hot" (most frequent in recent data)
        counter = Counter(self.recent_digits)
        most_common = counter.most_common(1)[0]
        if current_digit != most_common[0]:
            return False, f"Digit {current_digit} not the hottest (hottest: {most_common[0]})"
        
        return True, f"PERFECT! Digit {current_digit} is hot ({recent_count} times) and trending"
    
    async def place_smart_trade(self, digit):
        """Place DIFFERS trade on hot digit"""
        stake = 0.35  # Minimum stake to reduce losses
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "DIGITDIFF",  # Bet it WON'T repeat
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
                print(f"✅ SMART TRADE: Contract {contract_id} - DIFFERS on digit {digit}")
                return result
            elif "balance" in result:
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_smart_trading(self):
        """Smart trading - only perfect conditions"""
        print("🎯 STARTING SMART PROFIT STRATEGY")
        print("📊 Only trades when conditions are PERFECT")
        
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
                    
                    # Check if we should trade
                    should_trade, reason = self.should_trade(current_digit)
                    
                    if should_trade:
                        self.trades_made += 1
                        
                        print(f"🎯 SMART TRADE #{self.trades_made}: $0.35 DIFFERS on digit {current_digit}")
                        print(f"   Reason: {reason}")
                        print(f"   Recent: {list(self.recent_digits)[-10:]}")
                        
                        await self.place_smart_trade(current_digit)
                        
                        # Wait longer between trades for better conditions
                        await asyncio.sleep(5)
                    else:
                        if tick_count % 5 == 0:  # Show reason every 5 ticks
                            print(f"   ⏳ Waiting: {reason}")
                
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
                        if self.wins >= 3:
                            print("🎉 3 WINS ACHIEVED - SUCCESS!")
                            self.is_trading = False
                        elif self.losses >= 2:
                            print("⚠️ 2 LOSSES - STOPPING (Conservative)")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 SMART TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit > 0:
            print("🎉 SMART STRATEGY WORKED! 💰")
        
        # Calculate win rate
        if self.trades_made > 0:
            win_rate = (self.wins / self.trades_made) * 100
            print(f"📊 Win Rate: {win_rate:.1f}%")

async def main():
    print("🎯 SMART PROFIT - PERFECT CONDITIONS ONLY")
    print("=" * 45)
    print("📊 Only trades when digit is:")
    print("   ✅ Hot (most frequent)")
    print("   ✅ Trending (appeared 3+ times)")
    print("   ✅ Recent (in last 3 ticks)")
    print("💰 Stakes: $0.35 (minimum)")
    print("🎯 Target: 3 wins")
    print("🛑 Stop: 2 losses")
    print("=" * 45)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = SmartProfit(api_token)
    
    if await trader.connect():
        await trader.run_smart_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())