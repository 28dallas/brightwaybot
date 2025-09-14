#!/usr/bin/env python3
"""CAPITAL PRESERVATION - Ultra-conservative system"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter

class CapitalPreservation:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.recent_digits = deque(maxlen=30)
        
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
                
            print("🛡️ CAPITAL PRESERVATION CONNECTED")
            
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
    
    def find_ultra_safe_trade(self):
        """Find the safest possible trade"""
        if len(self.recent_digits) < 25:
            return None, "Need 25+ data points"
        
        counter = Counter(self.recent_digits)
        
        # Find digit that appeared MOST (5+ times) and is currently hot
        hot_digits = [(digit, count) for digit, count in counter.items() if count >= 5]
        
        if not hot_digits:
            return None, "No digit appeared 5+ times"
        
        # Get the hottest digit
        hottest_digit = max(hot_digits, key=lambda x: x[1])
        digit, count = hottest_digit
        
        # Check if it appeared in last 5 ticks (trending)
        last_5 = list(self.recent_digits)[-5:]
        if digit not in last_5:
            return None, f"Hottest digit {digit} not in last 5 ticks"
        
        # Check if it appeared at least twice in last 5 ticks
        recent_count = last_5.count(digit)
        if recent_count < 2:
            return None, f"Digit {digit} only appeared {recent_count} times in last 5"
        
        # ULTRA SAFE: Only trade if digit appeared 6+ times total
        if count < 6:
            return None, f"Digit {digit} only appeared {count} times (need 6+)"
        
        return digit, f"ULTRA SAFE: Digit {digit} appeared {count} times, {recent_count} in last 5"
    
    async def place_ultra_safe_trade(self, digit):
        """Place ultra-safe trade with minimum stake"""
        stake = 0.35  # Absolute minimum
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "DIGITDIFF",  # Bet it won't repeat (safer)
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
                print(f"🛡️ ULTRA SAFE TRADE: Contract {contract_id} - DIFFERS on digit {digit}")
                return result
            elif "balance" in result:
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_capital_preservation(self):
        """Ultra-conservative capital preservation"""
        print("🛡️ STARTING CAPITAL PRESERVATION")
        print("📊 Ultra-conservative: Only trades on 99% safe setups")
        
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
                    
                    # Look for ultra-safe trade
                    safe_digit, reason = self.find_ultra_safe_trade()
                    
                    if safe_digit is not None:
                        self.trades_made += 1
                        
                        print(f"🛡️ ULTRA SAFE TRADE #{self.trades_made}: $0.35 DIFFERS on digit {safe_digit}")
                        print(f"   {reason}")
                        print(f"   Recent: {list(self.recent_digits)[-10:]}")
                        
                        await self.place_ultra_safe_trade(safe_digit)
                        
                        # Wait much longer between trades (ultra-conservative)
                        await asyncio.sleep(10)
                    else:
                        if tick_count % 10 == 0:  # Show reason every 10 ticks
                            print(f"   🛡️ Waiting for ultra-safe setup: {reason}")
                
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
                        
                        # Ultra-conservative stops
                        if self.wins >= 2:
                            print("🎉 2 WINS - PRESERVING CAPITAL!")
                            self.is_trading = False
                        elif self.losses >= 1:
                            print("🛡️ 1 LOSS - PRESERVING CAPITAL!")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 CAPITAL PRESERVATION COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit >= 0:
            print("🛡️ CAPITAL PRESERVED! 💰")
        
        # Calculate win rate
        if self.trades_made > 0:
            win_rate = (self.wins / self.trades_made) * 100
            print(f"📊 Win Rate: {win_rate:.1f}%")

async def main():
    print("🛡️ CAPITAL PRESERVATION - ULTRA CONSERVATIVE")
    print("=" * 50)
    print("📊 Only trades when digit:")
    print("   ✅ Appeared 6+ times (ultra-hot)")
    print("   ✅ Trending (2+ times in last 5 ticks)")
    print("   ✅ Currently active")
    print("💰 Stakes: $0.35 (absolute minimum)")
    print("🎯 Target: 2 wins")
    print("🛑 Stop: 1 loss (preserve capital)")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = CapitalPreservation(api_token)
    
    if await trader.connect():
        await trader.run_capital_preservation()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())