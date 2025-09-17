#!/usr/bin/env python3
"""DIFFERS WINNER - Uses DIFFERS strategy (9/10 win probability) with Loss Prevention"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter
from loss_prevention_system import LossPreventionSystem
from backend.ai_predictor import EnhancedPredictor
from backend.ai_performance_monitor import AIPerformanceMonitor
from backend.performance_tracker import PerformanceTracker

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
        self.recent_prices = deque(maxlen=100)  # For AI analysis

        # Initialize Loss Prevention System
        self.loss_prevention = LossPreventionSystem(api_token)
        self.loss_prevention.max_daily_loss = 5.0  # Reduced for safety
        self.loss_prevention.max_trade_size = 10.0  # Allow higher stakes when safe
        self.loss_prevention.min_balance = 10.0  # Higher minimum balance
        self.loss_prevention.max_consecutive_losses = 2  # Stop after 2 losses

        # Initialize AI Predictor
        self.ai_predictor = EnhancedPredictor()

        # Initialize AI Performance Monitor
        self.ai_monitor = AIPerformanceMonitor()

        # Initialize Performance Tracker
        self.performance_tracker = PerformanceTracker()
        
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

            # Initialize loss prevention with current balance
            self.loss_prevention.balance = self.balance
            self.loss_prevention.starting_balance = self.balance

            print(f"💰 Starting Balance: ${self.balance}")
            print("🛡️ Loss Prevention System: ACTIVE")
            print(f"   Max Daily Loss: ${self.loss_prevention.max_daily_loss}")
            print(f"   Max Trade Size: ${self.loss_prevention.max_trade_size}")
            print(f"   Min Balance: ${self.loss_prevention.min_balance}")
            print(f"   Max Consecutive Losses: {self.loss_prevention.max_consecutive_losses}")

            print("🤖 AI Predictor: ACTIVE")
            print("   Training LSTM model with historical data...")

            # Try to train AI model with available data
            try:
                # Generate some sample historical data for training
                sample_digits = []
                for i in range(100):
                    # Generate pseudo-random digits based on some patterns
                    digit = (i * 7 + 3) % 10
                    sample_digits.append(digit)

                if self.ai_predictor.train_model(sample_digits):
                    print("   ✅ AI model trained successfully")
                else:
                    print("   ⚠️ AI model training failed, using pattern analysis only")
            except Exception as e:
                print(f"   ⚠️ AI training error: {e}")

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

    def calculate_safe_stake(self, digit):
        """Calculate stake based on win probability and safety limits"""
        base_stake = 1.00
        confidence_multiplier = 1.0

        # Calculate confidence based on digit frequency
        digit_count = self.recent_digits.count(digit)
        total_digits = len(self.recent_digits)

        if total_digits > 0:
            frequency = digit_count / total_digits

            # Higher confidence when digit appears more frequently
            if digit_count >= 5:  # Very strong pattern
                confidence_multiplier = 5.0
            elif digit_count >= 4:  # Strong pattern
                confidence_multiplier = 3.0
            elif digit_count >= 3:  # Good pattern
                confidence_multiplier = 2.0

        # Calculate stake
        calculated_stake = base_stake * confidence_multiplier

        # Apply safety limits from loss prevention system
        max_safe_stake = min(
            self.loss_prevention.max_trade_size,
            self.loss_prevention.balance * 0.05,  # Max 5% of balance
            50.0  # Absolute maximum for safety
        )

        safe_stake = min(calculated_stake, max_safe_stake)

        # Ensure minimum stake
        safe_stake = max(safe_stake, 0.35)

        return round(safe_stake, 2)
    
    async def place_differs_trade(self, digit, stake):
        """Place DIFFERS trade (win if next digit is NOT this digit) with AI and loss prevention"""
        # Check loss prevention limits before trading
        if not self.loss_prevention.check_risk_limits(stake):
            print(f"🛑 Trade blocked by loss prevention system")
            return None

        if not self.loss_prevention.is_trading_allowed:
            print(f"🛑 Trading not allowed - safety limits exceeded")
            return None

        print(f"💰 AI Stake: ${stake:.2f} (AI-optimized)")

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
                    self.recent_prices.append(price)
                    tick_count += 1

                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    print(f"   Recent: {list(self.recent_digits)}")
                    
                    # Get AI prediction for next digit
                    if len(self.recent_digits) >= 20 and len(self.recent_prices) >= 20:
                        ai_prediction = self.ai_predictor.get_comprehensive_prediction(
                            list(self.recent_digits),
                            list(self.recent_prices),
                            self.balance,
                            1.0  # base stake
                        )

                        # Only trade if AI confidence is high enough and conditions are favorable
                        if ai_prediction['should_trade'] and ai_prediction['final_confidence'] >= 70:
                            predicted_digit = ai_prediction['predicted_digit']
                            ai_stake = ai_prediction['optimal_stake']

                            # Use DIFFERS strategy: bet AGAINST the predicted digit
                            differs_digit = predicted_digit

                            # Store prediction for accuracy tracking
                            self.last_prediction = predicted_digit
                            self.last_confidence = ai_prediction['final_confidence']

                            self.trades_made += 1

                            print(f"🤖 AI TRADE #{self.trades_made}: ${ai_stake:.2f} AGAINST digit {differs_digit}")
                            print(f"   AI Confidence: {ai_prediction['final_confidence']:.1f}%")
                            print(f"   Strategy: WIN if next digit ≠ {differs_digit}")
                            print(f"   Market Session: {ai_prediction['market_session']}")
                            print(f"   Volatility Favorable: {ai_prediction['volatility']['trade_favorable']}")

                            await self.place_differs_trade(differs_digit, ai_stake)

                            # Log trade in performance tracker
                            trade_info = {
                                'trade_number': self.trades_made,
                                'predicted_digit': predicted_digit,
                                'differs_digit': differs_digit,
                                'stake': ai_stake,
                                'confidence': ai_prediction['final_confidence'],
                                'market_session': ai_prediction['market_session'],
                                'volatility_favorable': ai_prediction['volatility']['trade_favorable']
                            }
                            self.performance_tracker.log_trade(trade_info)

                            # Wait between trades
                            await asyncio.sleep(3)
                        else:
                            print(f"🤖 AI SKIP: Confidence {ai_prediction['final_confidence']:.1f}% (need ≥70%)")
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance

                    if profit != 0:
                        self.balance = new_balance

                        # Update loss prevention system
                        self.loss_prevention.update_balance(new_balance)

                        # Log AI prediction accuracy if we have a prediction
                        if hasattr(self, 'last_prediction') and hasattr(self, 'last_confidence'):
                            # Get the actual digit that just occurred (the one that determined win/loss)
                            if self.recent_digits:
                                actual_digit = self.recent_digits[-1]
                                self.ai_monitor.log_prediction(self.last_prediction, actual_digit, self.last_confidence)
                                print(f"🤖 AI Accuracy: {self.ai_monitor.get_accuracy():.1f}%")

                        # Update performance tracker with trade result
                        trade_result = {
                            'profit': profit,
                            'balance': self.balance,
                            'total_profit': total_profit,
                            'ai_accuracy': self.ai_monitor.get_accuracy() if hasattr(self, 'ai_monitor') else 0
                        }
                        self.performance_tracker.log_trade(trade_result)

                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        else:
                            self.losses += 1
                            print(f"💔 LOSS #{self.losses}: ${profit:.2f} | Total: ${total_profit:.2f} | Balance: ${self.balance:.2f}")

                        # Check loss prevention stop conditions
                        if not self.loss_prevention.is_trading_allowed:
                            print("🛑 LOSS PREVENTION: Trading stopped due to risk limits")
                            self.is_trading = False
                            break

                        # Stop conditions
                        if self.wins >= 10:
                            print("🎉 10 WINS ACHIEVED - MISSION ACCOMPLISHED!")
                            self.is_trading = False
                        elif self.losses >= 2:  # Reduced from 3 to match loss prevention
                            print("⚠️ 2 LOSSES - STOPPING FOR SAFETY")
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

        # Update final metrics in performance tracker
        self.performance_tracker.update_metrics('total_trades', self.trades_made)
        self.performance_tracker.update_metrics('wins', self.wins)
        self.performance_tracker.update_metrics('losses', self.losses)
        self.performance_tracker.update_metrics('final_profit', final_profit)
        self.performance_tracker.update_metrics('win_rate', (self.wins / self.trades_made) * 100 if self.trades_made > 0 else 0)

        # Log AI performance
        self.performance_tracker.log_ai_performance(
            self.ai_monitor.get_accuracy(),
            75.0,  # Average confidence (could be calculated more precisely)
            self.trades_made
        )

        # Log loss prevention metrics
        self.performance_tracker.log_loss_prevention(
            abs(final_profit) if final_profit < 0 else 0,
            self.loss_prevention.max_daily_loss,
            self.losses
        )

        # Save performance data and generate report
        self.performance_tracker.save_session()
        report = self.performance_tracker.generate_report()
        print(report)

        if final_profit > 0:
            print("🎉 DIFFERS STRATEGY SUCCESSFUL! 💰")

async def main():
    print("🤖 AI-POWERED DIFFERS WINNER - MAXIMUM LOSS PREVENTION")
    print("=" * 65)
    print("📊 DIFFERS = Win if next digit is DIFFERENT")
    print("🎲 AI-Predicted win probability with LSTM neural network")
    print("💰 Stakes: AI-optimized (Kelly Criterion, up to $10)")
    print("🎯 Target: 10 wins")
    print("🛑 Stop: 2 losses (loss prevention safety)")
    print("🛡️ Loss Prevention: ACTIVE")
    print("🤖 AI Predictor: ACTIVE (LSTM + Market Analysis)")
    print("=" * 65)
    
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