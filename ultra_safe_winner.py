#!/usr/bin/env python3
"""ULTRA SAFE WINNER - Maximum win rate with advanced filters"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque
from datetime import datetime

class UltraSafeWinner:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.digits = deque(maxlen=50)
        self.prices = deque(maxlen=50)
        self.recent_results = deque(maxlen=10)  # Track recent wins/losses
        
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
                
            print("🚀 ULTRA SAFE WINNER CONNECTED")
            
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance
            print(f"💰 Starting Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def analyze_market_timing(self):
        """Best trading hours analysis"""
        hour = datetime.utcnow().hour
        # European session (8-16 UTC) typically more stable
        return 8 <= hour <= 16
    
    def analyze_volatility(self):
        """Advanced volatility analysis"""
        if len(self.prices) < 30:
            return False
        
        recent = list(self.prices)[-30:]
        volatility = np.std(recent)
        mean_price = np.mean(recent)
        
        # Sweet spot: low volatility, stable prices
        return volatility < 0.3 and 1300 < mean_price < 1500
    
    def analyze_digit_patterns(self):
        """Advanced pattern analysis with multiple filters"""
        if len(self.digits) < 30:
            return None, 0, 0
        
        recent = list(self.digits)[-30:]
        counts = {}
        for d in recent:
            counts[d] = counts.get(d, 0) + 1
        
        # Find most frequent digit
        most_frequent = max(counts, key=counts.get)
        frequency = counts[most_frequent]
        
        # Skip digit 0 (rare in Volatility 100)
        if most_frequent == 0:
            return None, 0, 0
        
        # Calculate confidence based on multiple factors
        confidence = 0
        
        # Factor 1: Frequency (higher = better)
        if frequency >= 10:  # Very high frequency
            confidence += 40
        elif frequency >= 8:
            confidence += 30
        elif frequency >= 6:
            confidence += 20
        
        # Factor 2: Recent streak analysis
        last_10 = recent[-10:]
        if last_10.count(most_frequent) >= 4:
            confidence += 20
        
        # Factor 3: Avoid recently appeared digits in last 3 ticks
        last_3 = recent[-3:]
        if most_frequent not in last_3:
            confidence += 15
        
        # Factor 4: Pattern consistency
        first_half = recent[:15].count(most_frequent)
        second_half = recent[15:].count(most_frequent)
        if abs(first_half - second_half) <= 1:  # Consistent pattern
            confidence += 10
        
        return most_frequent, frequency, confidence
    
    def calculate_ultra_safe_stake(self, confidence, frequency):
        """Ultra conservative stake calculation"""
        # Only trade on very high confidence
        if confidence < 70:
            return 0
        
        # Recent performance adjustment
        recent_wins = sum(1 for r in self.recent_results if r == 'win')
        recent_losses = sum(1 for r in self.recent_results if r == 'loss')
        
        # Reduce stakes after losses
        if recent_losses >= 2:
            base_multiplier = 0.5
        elif recent_losses >= 1:
            base_multiplier = 0.7
        else:
            base_multiplier = 1.0
        
        # Confidence-based stakes
        if confidence >= 90 and frequency >= 10:
            return 100.0 * base_multiplier
        elif confidence >= 80 and frequency >= 8:
            return 50.0 * base_multiplier
        elif confidence >= 70 and frequency >= 6:
            return 25.0 * base_multiplier
        
        return 0
    
    def should_trade_now(self):
        """Multiple safety checks before trading"""
        # Check 1: Market timing
        if not self.analyze_market_timing():
            return False, "Outside optimal trading hours"
        
        # Check 2: Volatility
        if not self.analyze_volatility():
            return False, "High volatility detected"
        
        # Check 3: Recent performance
        if len(self.recent_results) >= 3:
            recent_losses = sum(1 for r in self.recent_results[-3:] if r == 'loss')
            if recent_losses >= 2:
                return False, "Too many recent losses"
        
        # Check 4: Pattern analysis
        digit, frequency, confidence = self.analyze_digit_patterns()
        if not digit or confidence < 70:
            return False, f"Low confidence: {confidence}%"
        
        # Check 5: Stake calculation
        stake = self.calculate_ultra_safe_stake(confidence, frequency)
        if stake == 0:
            return False, "No suitable stake calculated"
        
        return True, {
            'digit': digit,
            'frequency': frequency,
            'confidence': confidence,
            'stake': stake
        }
    
    async def place_ultra_safe_trade(self, trade_info):
        """Place trade with maximum safety"""
        digit = trade_info['digit']
        stake = trade_info['stake']
        
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
                print(f"🚀 ULTRA SAFE TRADE: DIFFERS on digit {digit}")
                print(f"   Frequency: {trade_info['frequency']}/30 times")
                print(f"   Confidence: {trade_info['confidence']}%")
                print(f"   Stake: ${stake}")
                return True
            else:
                print(f"❌ Trade failed: {result.get('error', {}).get('message', 'Unknown error')}")
                return False
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return False
    
    async def run_ultra_safe_system(self):
        """Run ultra safe trading system"""
        print("🚀 STARTING ULTRA SAFE WINNER")
        print("🛡️ MAXIMUM SAFETY FILTERS:")
        print("   ⏰ Optimal trading hours only")
        print("   📊 Low volatility requirement")
        print("   🎯 70%+ confidence minimum")
        print("   📈 Advanced pattern analysis")
        print("   💰 Adaptive stake sizing")
        
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
                    
                    # Wait longer between trades for better analysis
                    if tick_count - last_trade_tick >= 15:
                        can_trade, result = self.should_trade_now()
                        
                        if can_trade:
                            self.trades_made += 1
                            last_trade_tick = tick_count
                            
                            print(f"🎯 ULTRA SAFE OPPORTUNITY!")
                            success = await self.place_ultra_safe_trade(result)
                            
                            if success:
                                await asyncio.sleep(3)
                        else:
                            print(f"🛡️ SAFETY CHECK: {result}")
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            self.recent_results.append('win')
                            print(f"🎉 SAFE WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                            
                            if self.wins >= 10:
                                print("🚀 10 WINS - ULTRA SAFE SUCCESS!")
                                self.is_trading = False
                        else:
                            self.losses += 1
                            self.recent_results.append('loss')
                            print(f"💔 LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f}")
                            
                            if self.losses >= 2:
                                print("🛡️ 2 LOSSES - ULTRA SAFE STOP")
                                self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Analyzing market conditions...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        win_rate = (self.wins / self.trades_made * 100) if self.trades_made > 0 else 0
        
        print(f"\n📊 ULTRA SAFE WINNER COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Win Rate: {win_rate:.1f}%")
        print(f"Final Result: ${final_profit:.2f}")

async def main():
    print("🛡️ ULTRA SAFE WINNER SYSTEM")
    print("=" * 50)
    print("🎯 MAXIMUM SAFETY FEATURES:")
    print("   ⏰ Optimal trading hours (8-16 UTC)")
    print("   📊 Low volatility requirement")
    print("   🎯 70%+ confidence minimum")
    print("   📈 Advanced pattern analysis")
    print("   💰 Adaptive stake sizing")
    print("   🛡️ Recent performance tracking")
    print("🎯 Target: 10 wins | Stop: 2 losses")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = UltraSafeWinner(api_token)
    
    if await trader.connect():
        await trader.run_ultra_safe_system()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())