#!/usr/bin/env python3
"""PRACTICAL GUARDIAN - Balanced risk system that actually trades"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque, Counter
from datetime import datetime

class PracticalGuardian:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        
        # Practical settings that will actually trade
        self.min_confidence = 90      # 90%+ confidence (more realistic)
        self.stake = 50.0            # Fixed stake
        self.max_trades = 5          # Maximum 5 trades
        self.max_losses = 1          # Stop after 1 loss
        
        # Data storage
        self.digits = deque(maxlen=200)
        self.prices = deque(maxlen=200)
        
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
                
            print("🛡️ PRACTICAL GUARDIAN ACTIVATED")
            
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
    
    def find_strong_pattern(self):
        """Find strong patterns that will actually trigger trades"""
        if len(self.digits) < 50:
            return None
        
        digits = list(self.digits)
        best_score = 0
        best_digit = None
        
        # 1. Recent dominance pattern
        recent_30 = digits[-30:]
        digit_counts = Counter(recent_30)
        
        if digit_counts:
            most_common_digit, count = digit_counts.most_common(1)[0]
            if count >= 8:  # Appears 8+ times in last 30 (26%+)
                dominance_score = count * 3
                if dominance_score > best_score:
                    best_score = dominance_score
                    best_digit = most_common_digit
        
        # 2. Repeating patterns
        for pattern_len in [2, 3]:
            for i in range(len(digits) - pattern_len * 3):
                pattern = digits[i:i+pattern_len]
                
                # Count how many times this pattern appears
                pattern_count = 0
                for j in range(i, len(digits) - pattern_len + 1):
                    if digits[j:j+pattern_len] == pattern:
                        pattern_count += 1
                
                if pattern_count >= 3:  # Pattern appears 3+ times
                    # Predict next digit in pattern
                    last_occurrence = -1
                    for j in range(len(digits) - pattern_len, -1, -1):
                        if digits[j:j+pattern_len] == pattern:
                            last_occurrence = j
                            break
                    
                    if last_occurrence >= 0 and last_occurrence + pattern_len < len(digits):
                        next_digit = digits[last_occurrence + pattern_len]
                        score = pattern_count * pattern_len * 4
                        
                        if score > best_score:
                            best_score = score
                            best_digit = next_digit
        
        if best_score == 0 or best_digit is None:
            return None
        
        # Calculate confidence
        confidence = min(best_score * 3 + 60, 99)
        
        # Simple market check - just avoid extreme volatility
        market_ok = True
        if len(self.prices) >= 20:
            recent_prices = list(self.prices)[-20:]
            volatility = np.std(recent_prices)
            if volatility > 0.01:  # Very high volatility threshold
                market_ok = False
        
        should_trade = (
            confidence >= self.min_confidence and
            best_score >= 12 and  # Reasonable threshold
            market_ok and
            self.trades_made < self.max_trades and
            self.losses < self.max_losses
        )
        
        return {
            'predicted_digit': best_digit,
            'confidence': confidence,
            'pattern_score': best_score,
            'should_trade': should_trade,
            'market_ok': market_ok
        }
    
    async def place_trade(self, prediction):
        """Place trade"""
        digit = prediction['predicted_digit']
        
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
                print(f"🛡️ TRADE: Contract {contract_id}")
                print(f"   DIFFERS on digit {digit}")
                print(f"   Confidence: {prediction['confidence']:.1f}%")
                print(f"   Stake: ${self.stake}")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_system(self):
        """Run the practical guardian system"""
        print("🛡️ PRACTICAL GUARDIAN ACTIVE")
        print(f"   Min Confidence: {self.min_confidence}%")
        print(f"   Stake: ${self.stake}")
        print(f"   Max Trades: {self.max_trades}")
        print(f"   Max Losses: {self.max_losses}")
        
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
                    
                    if tick_count >= 50:
                        prediction = self.find_strong_pattern()
                        
                        if prediction:
                            print(f"🧠 Analysis: Digit={prediction['predicted_digit']}, "
                                  f"Conf={prediction['confidence']:.1f}%, "
                                  f"Score={prediction['pattern_score']}, "
                                  f"Trade={prediction['should_trade']}")
                            
                            if prediction['should_trade']:
                                self.trades_made += 1
                                print(f"🛡️ TRADE #{self.trades_made}")
                                await self.place_trade(prediction)
                                await asyncio.sleep(3)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                        else:
                            self.losses += 1
                            print(f"💔 LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f}")
                        
                        # Stop conditions
                        if self.wins >= 3:
                            print("🎉 3 WINS - SUCCESS!")
                            self.is_trading = False
                        elif self.losses >= self.max_losses:
                            print(f"🛡️ {self.max_losses} LOSS - STOPPING")
                            self.is_trading = False
                        elif total_profit >= 100:
                            print("💰 $100 PROFIT - GREAT SUCCESS!")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 PRACTICAL GUARDIAN COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if self.trades_made > 0:
            win_rate = (self.wins / self.trades_made) * 100
            print(f"📊 Win Rate: {win_rate:.1f}%")

async def main():
    print("🛡️ PRACTICAL GUARDIAN SYSTEM")
    print("=" * 40)
    print("🎯 BALANCED APPROACH:")
    print("   ✅ 90%+ confidence")
    print("   ✅ $50 stakes")
    print("   ✅ Stop after 1 loss")
    print("   ✅ Strong pattern detection")
    print("   ✅ Will actually trade!")
    print("=" * 40)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = PracticalGuardian(api_token)
    
    if await trader.connect():
        await trader.run_system()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())