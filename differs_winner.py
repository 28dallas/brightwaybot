#!/usr/bin/env python3
"""DIFFERS WINNER - Uses DIFFERS strategy (9/10 win probability)"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter

class DiffersWinner:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.recent_digits = deque(maxlen=15)
        
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
                
            print("🎯 DIFFERS WINNER CONNECTED")
            
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
    
    def get_differs_digit(self):
        """Get digit to bet AGAINST (DIFFERS strategy)"""
        if len(self.recent_digits) < 8:
            return None
        
        # Count frequency of recent digits
        counter = Counter(self.recent_digits)
        
        # Strategy: Bet AGAINST the most frequent digit
        # If digit 3 appears most, bet DIFFERS on 3 (win if next digit is NOT 3)
        most_common = counter.most_common(1)[0]
        hot_digit = most_common[0]
        hot_count = most_common[1]
        
        # Only bet if digit appeared 3+ times (strong pattern)
        if hot_count >= 3:
            return hot_digit
        
        # Alternative: bet against digit that just appeared twice in a row
        if len(self.recent_digits) >= 2:
            if self.recent_digits[-1] == self.recent_digits[-2]:
                return self.recent_digits[-1]
        
        return None
    
    async def place_differs_trade(self, digit):
        """Place DIFFERS trade (win if next digit is NOT this digit)"""
        stake = 1.00  # Increased stake for higher profits
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "DIGITDIFF",  # DIFFERS contract
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
                print(f"✅ DIFFERS TRADE: Contract {contract_id} - WIN if next digit ≠ {digit}")
                return result
            elif "balance" in result:
                print(f"📊 Balance update received")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_differs_trading(self):
        """DIFFERS trading - higher win probability"""
        print("🎯 STARTING DIFFERS TRADING")
        print("📊 DIFFERS = Win if next digit is DIFFERENT")
        print("🎲 Win probability: 9/10 (90%)")
        
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
                    
                    # Get digit to bet AGAINST
                    differs_digit = self.get_differs_digit()
                    
                    if differs_digit is not None and len(self.recent_digits) >= 10:
                        digit_count = self.recent_digits.count(differs_digit)
                        
                        # Only trade if digit appeared frequently
                        if digit_count >= 3:
                            self.trades_made += 1
                            
                            print(f"🎯 DIFFERS TRADE #{self.trades_made}: $1.00 AGAINST digit {differs_digit}")
                            print(f"   Strategy: WIN if next digit ≠ {differs_digit} (90% chance)")
                            print(f"   Reason: Digit {differs_digit} appeared {digit_count} times")
                            
                            await self.place_differs_trade(differs_digit)
                            
                            # Wait between trades
                            await asyncio.sleep(3)
                
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
        print(f"\n📊 DIFFERS TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit > 0:
            print("🎉 DIFFERS STRATEGY SUCCESSFUL! 💰")

async def main():
    print("🎯 DIFFERS WINNER - 90% WIN PROBABILITY")
    print("=" * 45)
    print("📊 DIFFERS = Win if next digit is DIFFERENT")
    print("🎲 Win chance: 9/10 digits (90%)")
    print("💰 Stakes: $1.00 (higher profits)")
    print("🎯 Target: 10 wins")
    print("🛑 Stop: 3 losses")
    print("=" * 45)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = DiffersWinner(api_token)
    
    if await trader.connect():
        await trader.run_differs_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())