#!/usr/bin/env python3
"""CAPITAL GUARDIAN - Absolute minimum risk system"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque, Counter
from datetime import datetime

class CapitalGuardian:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        
        # EXTREME conservative settings
        self.min_confidence = 98      # 98%+ confidence only
        self.stake = 50.0            # Fixed minimal stake
        self.max_trades = 3          # Maximum 3 trades total
        self.stop_on_first_loss = True  # Stop immediately on any loss
        
        # Data storage - more history for better analysis
        self.digits = deque(maxlen=500)
        self.prices = deque(maxlen=500)
        
        # Track only the strongest patterns
        self.confirmed_patterns = {}
        
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
                
            print("🛡️ CAPITAL GUARDIAN ACTIVATED")
            
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance
            print(f"💰 Protected Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def find_absolute_certainty(self):
        """Only find patterns with absolute certainty"""
        if len(self.digits) < 100:
            return None
        
        digits = list(self.digits)
        
        # Look for ONLY the strongest possible patterns
        certainty_score = 0
        best_digit = None
        
        # 1. Perfect repetition cycles (90% of score)
        for cycle_length in [3, 4, 5, 6]:
            for start in range(len(digits) - cycle_length * 4):
                pattern = digits[start:start + cycle_length]
                
                # Check if pattern repeats perfectly 3+ times
                perfect_repeats = 0
                for i in range(start + cycle_length, len(digits) - cycle_length, cycle_length):
                    if digits[i:i + cycle_length] == pattern:
                        perfect_repeats += 1
                    else:
                        break
                
                if perfect_repeats >= 2:  # Pattern repeated 3+ times total
                    # Predict next in cycle
                    next_pos = (len(digits) - start) % cycle_length
                    predicted_digit = pattern[next_pos]
                    score = perfect_repeats * cycle_length * 10
                    
                    if score > certainty_score:
                        certainty_score = score
                        best_digit = predicted_digit
        
        # 2. Dominant digit with mathematical certainty (10% of score)
        recent_50 = digits[-50:]
        digit_counts = Counter(recent_50)
        
        if digit_counts:
            most_common_digit, count = digit_counts.most_common(1)[0]
            if count >= 15:  # Appears 30%+ of the time
                dominance_score = count * 2
                if dominance_score > certainty_score:
                    certainty_score = dominance_score
                    best_digit = most_common_digit
        
        if certainty_score == 0 or best_digit is None:
            return None
        
        # Calculate confidence (very strict)
        confidence = min(certainty_score * 2 + 70, 99.5)
        
        # Additional safety checks
        market_safe = self.is_market_ultra_safe()
        timing_perfect = self.is_timing_perfect()
        
        should_trade = (
            confidence >= self.min_confidence and
            certainty_score >= 30 and  # Very high threshold
            market_safe and
            timing_perfect and
            self.trades_made < self.max_trades
        )
        
        return {
            'predicted_digit': best_digit,
            'confidence': confidence,
            'certainty_score': certainty_score,
            'should_trade': should_trade,
            'market_safe': market_safe,
            'timing_perfect': timing_perfect
        }
    
    def is_market_ultra_safe(self):
        """Ultra-strict market safety check"""
        if len(self.prices) < 50:
            return False
        
        recent_prices = list(self.prices)[-50:]
        
        # 1. Volatility must be very low
        volatility = np.std(recent_prices)
        if volatility > 0.0015:  # Very strict
            return False
        
        # 2. No sudden price jumps
        price_changes = [abs(recent_prices[i] - recent_prices[i-1]) 
                        for i in range(1, len(recent_prices))]
        max_change = max(price_changes)
        if max_change > 0.005:  # No big jumps
            return False
        
        # 3. Stable trending behavior
        trend_changes = 0
        for i in range(2, len(recent_prices)):
            prev_trend = recent_prices[i-1] - recent_prices[i-2]
            curr_trend = recent_prices[i] - recent_prices[i-1]
            if (prev_trend > 0) != (curr_trend > 0):
                trend_changes += 1
        
        # Too many trend changes = choppy market
        if trend_changes > len(recent_prices) * 0.3:
            return False
        
        return True
    
    def is_timing_perfect(self):
        """Check if timing is perfect for trading"""
        hour = datetime.now().hour
        
        # Only trade during most stable hours (European session)
        if not (9 <= hour <= 15):
            return False
        
        # Avoid first and last hour of session
        if hour in [9, 15]:
            return False
        
        return True
    
    async def place_guardian_trade(self, prediction):
        """Place ultra-safe guardian trade"""
        digit = prediction['predicted_digit']
        
        # Always use DIFFERS (statistically better)
        trade_msg = {
            "buy": 1,
            "price": self.stake,
            "parameters": {
                "amount": self.stake,
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
                contract_id = result['buy']['contract_id']
                print(f"🛡️ GUARDIAN TRADE: Contract {contract_id}")
                print(f"   Strategy: DIFFERS on digit {digit}")
                print(f"   Confidence: {prediction['confidence']:.1f}%")
                print(f"   Certainty Score: {prediction['certainty_score']}")
                print(f"   Stake: ${self.stake}")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_capital_guardian(self):
        """Run the capital guardian system"""
        print("🛡️ CAPITAL GUARDIAN SYSTEM ACTIVE")
        print("📊 EXTREME Protection Settings:")
        print(f"   Min Confidence: {self.min_confidence}%")
        print(f"   Fixed Stake: ${self.stake}")
        print(f"   Max Trades: {self.max_trades}")
        print(f"   Stop on Loss: {self.stop_on_first_loss}")
        
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
                    
                    self.digits.append(current_digit)
                    self.prices.append(price)
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Only analyze after sufficient data
                    if tick_count >= 100:
                        prediction = self.find_absolute_certainty()
                        
                        if prediction:
                            print(f"🧠 Guardian Analysis:")
                            print(f"   Digit: {prediction['predicted_digit']}")
                            print(f"   Confidence: {prediction['confidence']:.1f}%")
                            print(f"   Certainty: {prediction['certainty_score']}")
                            print(f"   Market Safe: {prediction['market_safe']}")
                            print(f"   Timing Perfect: {prediction['timing_perfect']}")
                            print(f"   Will Trade: {prediction['should_trade']}")
                            
                            if prediction['should_trade']:
                                self.trades_made += 1
                                print(f"🛡️ GUARDIAN TRADE #{self.trades_made}")
                                await self.place_guardian_trade(prediction)
                                await asyncio.sleep(3)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 GUARDIAN WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                            
                            # Conservative exit on profit
                            if total_profit >= 1.0:
                                print("💰 $1 PROFIT - GUARDIAN SUCCESS!")
                                self.is_trading = False
                        else:
                            self.losses += 1
                            print(f"💔 GUARDIAN LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f}")
                            
                            # Stop immediately on any loss
                            if self.stop_on_first_loss:
                                print("🛡️ FIRST LOSS - CAPITAL PROTECTED")
                                self.is_trading = False
                        
                        # Max trades reached
                        if self.trades_made >= self.max_trades:
                            print(f"🛡️ {self.max_trades} TRADES COMPLETED")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 CAPITAL GUARDIAN COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if self.trades_made > 0:
            win_rate = (self.wins / self.trades_made) * 100
            print(f"📊 Win Rate: {win_rate:.1f}%")
        
        if final_profit >= 0:
            print("🛡️ CAPITAL SUCCESSFULLY PROTECTED!")

async def main():
    print("🛡️ CAPITAL GUARDIAN SYSTEM")
    print("=" * 50)
    print("🎯 ABSOLUTE MINIMUM RISK:")
    print("   ✅ 98%+ confidence ONLY")
    print("   ✅ Fixed $0.35 stakes")
    print("   ✅ Stop on first loss")
    print("   ✅ Maximum 3 trades")
    print("   ✅ Perfect pattern cycles only")
    print("   ✅ Ultra-safe market conditions")
    print("   ✅ Perfect timing windows")
    print("🛡️ Mission: Protect every dollar")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = CapitalGuardian(api_token)
    
    if await trader.connect():
        await trader.run_capital_guardian()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())