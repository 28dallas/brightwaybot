#!/usr/bin/env python3
"""ULTIMATE AI SYSTEM - Every possible framework combined"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque, Counter
import math
from datetime import datetime

class UltimateAI:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        
        # Data storage
        self.digits = deque(maxlen=100)
        self.prices = deque(maxlen=100)
        self.timestamps = deque(maxlen=100)
        
        # AI Models
        self.pattern_memory = {}
        self.success_patterns = []
        self.failure_patterns = []
        
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
                
            print("🚀 ULTIMATE AI SYSTEM CONNECTED")
            
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
    
    def fibonacci_analysis(self, digits):
        """Fibonacci sequence detection"""
        if len(digits) < 10:
            return {}
        
        scores = {i: 0 for i in range(10)}
        
        for i in range(len(digits) - 3):
            a, b = digits[i], digits[i+1]
            fib_next = (a + b) % 10
            
            if i+2 < len(digits) and digits[i+2] == fib_next:
                scores[fib_next] += 3
                
        return scores
    
    def prime_pattern_analysis(self, digits):
        """Prime number pattern analysis"""
        primes = [2, 3, 5, 7]
        scores = {i: 0 for i in range(10)}
        
        recent = digits[-15:] if len(digits) >= 15 else digits
        prime_count = sum(1 for d in recent if d in primes)
        non_prime_count = len(recent) - prime_count
        
        if prime_count > non_prime_count * 1.3:
            for prime in primes:
                scores[prime] += 4
        elif non_prime_count > prime_count * 1.3:
            for digit in [0, 1, 4, 6, 8, 9]:
                scores[digit] += 4
                
        return scores
    
    def momentum_analysis(self, prices):
        """Price momentum analysis"""
        if len(prices) < 10:
            return 0
        
        recent = prices[-10:]
        momentum = 0
        
        for i in range(1, len(recent)):
            if recent[i] > recent[i-1]:
                momentum += 1
            else:
                momentum -= 1
                
        return momentum / len(recent)
    
    def volatility_analysis(self, prices):
        """Market volatility analysis"""
        if len(prices) < 15:
            return {'favorable': False, 'score': 0}
        
        recent = prices[-15:]
        volatility = np.std(recent)
        avg_volatility = np.mean([np.std(prices[i:i+10]) for i in range(len(prices)-10)])
        
        # Sweet spot volatility
        favorable = 0.0003 < volatility < 0.0015
        score = volatility / avg_volatility if avg_volatility > 0 else 1
        
        return {'favorable': favorable, 'score': score}
    
    def pattern_recognition(self, digits):
        """Advanced pattern recognition"""
        if len(digits) < 20:
            return {}
        
        scores = {i: 0 for i in range(10)}
        
        # Look for repeating patterns
        for pattern_len in [2, 3, 4]:
            for i in range(len(digits) - pattern_len * 2):
                pattern = digits[i:i+pattern_len]
                
                # Check if pattern repeats
                for j in range(i+pattern_len, len(digits)-pattern_len+1):
                    if digits[j:j+pattern_len] == pattern:
                        # Pattern found, predict next
                        if j+pattern_len < len(digits):
                            next_digit = digits[j+pattern_len]
                            scores[next_digit] += pattern_len
        
        return scores
    
    def ensemble_prediction(self, current_digit):
        """Combine all AI methods"""
        if len(self.digits) < 25:
            return None
        
        # Get all analysis results
        fib_scores = self.fibonacci_analysis(list(self.digits))
        prime_scores = self.prime_pattern_analysis(list(self.digits))
        pattern_scores = self.pattern_recognition(list(self.digits))
        
        momentum = self.momentum_analysis(list(self.prices))
        volatility = self.volatility_analysis(list(self.prices))
        
        # Market timing
        hour = datetime.utcnow().hour
        session_multiplier = 1.2 if 8 <= hour <= 16 else 1.0  # European session
        
        # Combine all scores
        final_scores = {}
        for digit in range(10):
            score = 0
            score += fib_scores.get(digit, 0) * 0.25
            score += prime_scores.get(digit, 0) * 0.25
            score += pattern_scores.get(digit, 0) * 0.3
            
            # Momentum boost
            if abs(momentum) > 0.3:
                score += 2
            
            # Volatility boost
            if volatility['favorable']:
                score += 3
            
            # Session boost
            score *= session_multiplier
            
            final_scores[digit] = score
        
        # Get best prediction
        best_digit = max(final_scores, key=final_scores.get)
        confidence = min(final_scores[best_digit] * 6 + 30, 95)
        
        # Trade on high confidence - simplified conditions
        should_trade = (
            confidence >= 85 and
            final_scores[best_digit] >= 5
        )
        
        return {
            'predicted_digit': best_digit,
            'confidence': confidence,
            'should_trade': should_trade,
            'momentum': momentum,
            'volatility': volatility,
            'scores': final_scores
        }
    
    def adaptive_stake_calculation(self, confidence, consecutive_wins):
        """Adaptive stake based on confidence and streak"""
        base_stake = 0.35
        
        # Confidence multiplier
        conf_multiplier = min(confidence / 70, 1.5)
        
        # Winning streak multiplier (compound wins)
        streak_multiplier = min(1 + (consecutive_wins * 0.1), 1.3)
        
        # Calculate stake
        stake = base_stake * conf_multiplier * streak_multiplier
        
        # Cap at reasonable maximum and round to 2 decimal places
        return round(min(stake, 1.0), 2)
    
    async def place_ultimate_trade(self, prediction, stake):
        """Place trade with ultimate strategy"""
        # Use DIFFERS strategy (90% win probability)
        digit = prediction['predicted_digit']
        
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
                contract_id = result['buy']['contract_id']
                print(f"🚀 ULTIMATE TRADE: Contract {contract_id} - DIFFERS on digit {digit}")
                print(f"   Confidence: {prediction['confidence']:.1f}%")
                print(f"   Stake: ${stake:.2f}")
                return result
            elif "balance" in result:
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_ultimate_system(self):
        """Run the ultimate AI trading system"""
        print("🚀 STARTING ULTIMATE AI SYSTEM")
        print("🧠 Combining ALL AI frameworks for maximum accuracy")
        
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        consecutive_wins = 0
        
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
                    self.timestamps.append(datetime.utcnow())
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Get ultimate prediction
                    prediction = self.ensemble_prediction(current_digit)
                    
                    if prediction:
                        print(f"🧠 AI Analysis: Digit={prediction['predicted_digit']}, "
                              f"Conf={prediction['confidence']:.1f}%, "
                              f"Trade={prediction['should_trade']}")
                        
                        if prediction['should_trade']:
                            self.trades_made += 1
                            stake = self.adaptive_stake_calculation(
                                prediction['confidence'], consecutive_wins
                            )
                            
                            print(f"🚀 ULTIMATE TRADE #{self.trades_made}")
                            print(f"   Strategy: DIFFERS (90% win probability)")
                            print(f"   Target: Digit {prediction['predicted_digit']}")
                            print(f"   Momentum: {prediction['momentum']:.3f}")
                            print(f"   Volatility: {'Favorable' if prediction['volatility']['favorable'] else 'Unfavorable'}")
                            
                            await self.place_ultimate_trade(prediction, stake)
                            await asyncio.sleep(3)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            consecutive_wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                            print(f"   Consecutive wins: {consecutive_wins}")
                        else:
                            self.losses += 1
                            consecutive_wins = 0
                            print(f"💔 LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f}")
                        
                        # Dynamic stop conditions
                        if self.wins >= 5:
                            print("🎉 5 WINS - ULTIMATE SUCCESS!")
                            self.is_trading = False
                        elif self.losses >= 2:
                            print("🛡️ 2 LOSSES - PRESERVING CAPITAL")
                            self.is_trading = False
                        elif total_profit >= 3.0:
                            print("💰 $3 PROFIT TARGET REACHED!")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 ULTIMATE AI SYSTEM COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if self.trades_made > 0:
            win_rate = (self.wins / self.trades_made) * 100
            print(f"📊 Win Rate: {win_rate:.1f}%")
        
        if final_profit > 0:
            print("🚀 ULTIMATE AI SUCCESS! 💰")

async def main():
    print("🚀 ULTIMATE AI TRADING SYSTEM")
    print("=" * 50)
    print("🧠 COMBINING ALL AI FRAMEWORKS:")
    print("   ✅ Fibonacci Analysis")
    print("   ✅ Prime Pattern Recognition")
    print("   ✅ Advanced Pattern Detection")
    print("   ✅ Momentum Analysis")
    print("   ✅ Volatility Analysis")
    print("   ✅ Market Session Timing")
    print("   ✅ Adaptive Stake Sizing")
    print("   ✅ DIFFERS Strategy (90% win rate)")
    print("💰 Ultra-conservative: 85%+ confidence only")
    print("🎯 Target: 5 wins OR $3 profit")
    print("🛡️ Stop: 2 losses")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = UltimateAI(api_token)
    
    if await trader.connect():
        await trader.run_ultimate_system()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())