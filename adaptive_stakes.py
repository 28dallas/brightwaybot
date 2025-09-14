#!/usr/bin/env python3
"""ADAPTIVE STAKES - $5 for perfect conditions, $1 for good conditions"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque

class AdaptiveStakes:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.digits = deque(maxlen=30)
        self.prices = deque(maxlen=30)
        
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
                
            print("🚀 ADAPTIVE STAKES SYSTEM CONNECTED")
            
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance
            print(f"💰 Starting Balance: ${self.balance}")
            print(f"🎯 ADAPTIVE STAKES: $1-$5 based on conditions")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def analyze_market_conditions(self):
        """Analyze market favorability"""
        if len(self.prices) < 20:
            return False
        
        recent_prices = list(self.prices)[-20:]
        volatility = np.std(recent_prices)
        
        # Favorable conditions: low volatility (stable market)
        return volatility < 0.5
    
    def calculate_optimal_stake(self):
        """Calculate stake based on digit frequency and market conditions"""
        if len(self.digits) < 20:
            return None, 0
        
        recent = list(self.digits)[-20:]
        counts = {}
        for d in recent:
            counts[d] = counts.get(d, 0) + 1
        
        most_frequent = max(counts, key=counts.get)
        frequency = counts[most_frequent]
        
        # Skip digit 0
        if most_frequent == 0:
            return None, 0
        
        # Check market conditions
        market_favorable = self.analyze_market_conditions()
        
        # PERFECT CONDITIONS: 8+ occurrences + favorable market = $100 stake
        if frequency >= 8 and market_favorable:
            return most_frequent, 100.0
        
        # VERY GOOD CONDITIONS: 7+ occurrences = $50 stake
        elif frequency >= 7:
            return most_frequent, 50.0
        
        # GOOD CONDITIONS: 6+ occurrences = $25 stake
        elif frequency >= 6:
            return most_frequent, 25.0
        
        return None, 0
    
    async def place_adaptive_trade(self, digit, stake):
        """Place trade with adaptive stake"""
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
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
                if stake == 100.0:
                    print(f"🚀 MAXIMUM TRADE: DIFFERS on digit {digit} - STAKE: ${stake}")
                    print(f"💰 PERFECT CONDITIONS! Expected profit: ~$85")
                elif stake == 50.0:
                    print(f"🚀 BIG TRADE: DIFFERS on digit {digit} - STAKE: ${stake}")
                    print(f"💰 VERY GOOD CONDITIONS! Expected profit: ~$42.50")
                else:
                    print(f"🚀 STANDARD TRADE: DIFFERS on digit {digit} - STAKE: ${stake}")
                    print(f"💰 GOOD CONDITIONS! Expected profit: ~$21.25")
                return True
            else:
                print(f"❌ Trade failed: {result.get('error', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return False
    
    async def run_system(self):
        """Run adaptive stakes system"""
        print("🚀 STARTING ADAPTIVE STAKES SYSTEM")
        print("🎯 HIGH STAKES SELECTION:")
        print("   💎 8+ occurrences + favorable market = $100 stake")
        print("   🔥 7+ occurrences = $50 stake")
        print("   ✅ 6+ occurrences = $25 stake")
        
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        last_trade_tick = 0
        
        while self.is_trading and self.wins < 10 and self.losses < 2:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.digits.append(current_digit)
                    self.prices.append(price)
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    if tick_count - last_trade_tick >= 8:
                        target_digit, optimal_stake = self.calculate_optimal_stake()
                        
                        if target_digit and optimal_stake > 0:
                            self.trades_made += 1
                            last_trade_tick = tick_count
                            
                            market_status = "FAVORABLE" if self.analyze_market_conditions() else "NORMAL"
                            print(f"🎯 OPPORTUNITY DETECTED!")
                            print(f"   Digit {target_digit} frequency: {list(self.digits)[-20:].count(target_digit)}/20")
                            print(f"   Market: {market_status}")
                            print(f"   Selected Stake: ${optimal_stake}")
                            
                            success = await self.place_adaptive_trade(target_digit, optimal_stake)
                            
                            if success:
                                await asyncio.sleep(2)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                            
                            if self.wins >= 10:
                                print("🚀 10 WINS - MAXIMUM SUCCESS!")
                                self.is_trading = False
                        else:
                            self.losses += 1
                            print(f"💔 LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f}")
                            
                            if self.losses >= 2:
                                print("🛡️ 2 LOSSES - STOPPING (High stakes protection)")
                                self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Analyzing market conditions...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 ADAPTIVE STAKES COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit > 0:
            print("🚀 ADAPTIVE STRATEGY SUCCESS! 💰")

async def main():
    print("🎯 ADAPTIVE STAKES SYSTEM")
    print("=" * 50)
    print("🧠 HIGH STAKES SELECTION:")
    print("   💎 PERFECT (8+ freq + favorable market) → $100 stake")
    print("   🔥 VERY GOOD (7+ frequency) → $50 stake")
    print("   ✅ GOOD (6+ frequency) → $25 stake")
    print("📊 Strategy: DIFFERS on frequent digits")
    print("🎯 Target: 10 wins")
    print("🛡️ Stop: 2 losses (high stakes protection)")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = AdaptiveStakes(api_token)
    
    if await trader.connect():
        await trader.run_system()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())