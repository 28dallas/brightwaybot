#!/usr/bin/env python3
"""SMART WINNER - Only bets on digits that are actually appearing"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter

class SmartWinner:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.recent_digits = deque(maxlen=10)
        
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
                
            print("🧠 SMART WINNER CONNECTED")
            
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
    
    def get_smart_digit(self, current_digit):
        """Get the smartest digit to bet on"""
        if len(self.recent_digits) < 5:
            return None
        
        # Count frequency of recent digits
        counter = Counter(self.recent_digits)
        
        # Strategy 1: Bet on the MOST frequent digit from recent data
        most_common = counter.most_common(1)[0]
        hot_digit = most_common[0]
        hot_count = most_common[1]
        
        # Strategy 2: If current digit appeared recently, bet on it
        if current_digit in self.recent_digits:
            return current_digit
        
        # Strategy 3: If hot digit appeared 3+ times, bet on it
        if hot_count >= 3:
            return hot_digit
        
        # Strategy 4: Bet on current digit (it just appeared, might repeat)
        return current_digit
    
    async def place_smart_trade(self, digit):
        """Place trade on smart digit"""
        stake = 0.35  # Minimum stake to reduce losses
        
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
        
        try:
            await self.ws.send(json.dumps(trade_msg))
            response = await self.ws.recv()
            result = json.loads(response)
            
            if "buy" in result:
                contract_id = result['buy']['contract_id']
                print(f"✅ SMART TRADE: Contract {contract_id} on digit {digit}")
                return result
            elif "balance" in result:
                # This is just a balance update, not a trade failure
                print(f"📊 Balance update received")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_smart_trading(self):
        """Smart trading that avoids losses"""
        print("🧠 STARTING SMART TRADING")
        print("📊 Only bets on digits that are appearing")
        
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
                    print(f"   Recent: {list(self.recent_digits)}")
                    
                    # Get smart digit to bet on
                    smart_digit = self.get_smart_digit(current_digit)
                    
                    if smart_digit is not None and len(self.recent_digits) >= 8:
                        # Only trade if we see a pattern
                        digit_count = self.recent_digits.count(smart_digit)
                        
                        if digit_count >= 2:  # Digit appeared at least twice
                            self.trades_made += 1
                            
                            print(f"🎯 SMART TRADE #{self.trades_made}: $0.35 on digit {smart_digit}")
                            print(f"   Reason: Digit {smart_digit} appeared {digit_count} times recently")
                            
                            await self.place_smart_trade(smart_digit)
                            
                            # Wait a bit between trades
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
                        if self.wins >= 10:
                            print("🎉 10 WINS ACHIEVED - MISSION ACCOMPLISHED!")
                            self.is_trading = False
                        elif self.losses >= 3:
                            print("⚠️ 3 LOSSES - STOPPING FOR SAFETY")
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

async def main():
    print("🧠 SMART WINNER - AVOID LOSSES")
    print("=" * 35)
    print("📊 Only bets on appearing digits")
    print("💰 Minimum stakes ($0.35)")
    print("🎯 Target: 10 wins")
    print("🛑 Stop: 3 losses")
    print("=" * 35)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = SmartWinner(api_token)
    
    if await trader.connect():
        await trader.run_smart_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())