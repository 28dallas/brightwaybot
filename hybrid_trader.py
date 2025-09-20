#!/usr/bin/env python3
"""HYBRID TRADER - Combines DIFFERS + MATCHES strategies with intelligent switching"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque, Counter
from backend.ai_predictor import EnhancedPredictor
from backend.ai_performance_monitor import AIPerformanceMonitor
from backend.performance_tracker import PerformanceTracker
import numpy as np
from datetime import datetime

class HybridTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.losses = 0
        self.recent_digits = deque(maxlen=30)
        self.recent_prices = deque(maxlen=100)
        self.strategy_history = deque(maxlen=20)  # Track recent strategy performance

        # Initialize AI systems
        self.ai_predictor = EnhancedPredictor()
        self.ai_monitor = AIPerformanceMonitor()
        self.performance_tracker = PerformanceTracker()

        # Strategy settings
        self.current_strategy = "HYBRID"  # Start in hybrid mode
        self.differs_confidence = 70  # DIFFERS threshold
        self.matches_confidence = 75  # MATCHES threshold
        self.min_hybrid_confidence = 65  # Lower threshold for hybrid

        # Performance tracking per strategy
        self.strategy_performance = {
            'DIFFERS': {'wins': 0, 'losses': 0, 'trades': 0},
            'MATCHES': {'wins': 0, 'losses': 0, 'trades': 0},
            'HYBRID': {'wins': 0, 'losses': 0, 'trades': 0}
        }

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

            print("🎯 HYBRID TRADER CONNECTED")
            print("🔄 Combines DIFFERS + MATCHES with intelligent switching")
            print("🤖 AI-powered strategy selection and optimization")

            # Get balance and subscribe
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance

            print(f"💰 Starting Balance: ${self.balance}")

            # Train AI for hybrid strategy
            try:
                sample_digits = []
                for i in range(200):
                    # Generate diverse patterns for hybrid training
                    digit = (i * 5 + 2) % 10
                    sample_digits.append(digit)

                if self.ai_predictor.train_model(sample_digits):
                    print("   ✅ AI model trained for hybrid strategy")
                else:
                    print("   ⚠️ AI model training failed")
            except Exception as e:
                print(f"   ⚠️ AI training error: {e}")

            return True

        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False

    def select_optimal_strategy(self, ai_prediction, market_conditions):
        """Select best strategy based on AI prediction and market conditions"""
        confidence = ai_prediction['final_confidence']
        volatility = market_conditions.get('volatility', {}).get('volatility_score', 0)
        session = ai_prediction.get('market_session', 'unknown')

        # Strategy selection logic
        if confidence >= self.matches_confidence:
            # High confidence - use MATCHES
            return 'MATCHES', confidence
        elif confidence >= self.differs_confidence:
            # Medium-high confidence - use DIFFERS
            return 'DIFFERS', confidence
        elif confidence >= self.min_hybrid_confidence and volatility < 0.001:
            # Lower confidence but stable market - use HYBRID
            return 'HYBRID', confidence
        else:
            # Low confidence or high volatility - don't trade
            return 'WAIT', 0

    def calculate_hybrid_stake(self, strategy, confidence):
        """Calculate stake based on strategy and confidence"""
        base_stake = 1.00

        if strategy == 'MATCHES':
            # Conservative staking for MATCHES
            if confidence >= 85:
                multiplier = 1.8
            elif confidence >= 80:
                multiplier = 1.4
            else:
                multiplier = 1.1
        elif strategy == 'DIFFERS':
            # More aggressive for DIFFERS
            if confidence >= 80:
                multiplier = 2.5
            elif confidence >= 75:
                multiplier = 2.0
            else:
                multiplier = 1.5
        else:  # HYBRID
            multiplier = 1.2  # Conservative hybrid

        calculated_stake = base_stake * multiplier

        # Apply balance limits
        max_stake = min(
            self.balance * 0.04,  # Max 4% of balance
            15.0  # Absolute maximum
        )

        safe_stake = min(calculated_stake, max_stake)
        safe_stake = max(safe_stake, 0.35)

        return round(safe_stake, 2)

    async def place_hybrid_trade(self, strategy, digit, stake):
        """Place trade based on selected strategy"""
        if strategy == 'MATCHES':
            contract_type = "DIGITMATCH"
            description = f"WIN if next digit = {digit}"
        elif strategy == 'DIFFERS':
            contract_type = "DIGITDIFF"
            description = f"WIN if next digit ≠ {digit}"
        else:
            return None

        print(f"💰 {strategy} Stake: ${stake:.2f} (Hybrid-optimized)")

        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": contract_type,
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
                print(f"✅ {strategy} TRADE: Contract {contract_id} - {description}")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result

        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}

    async def run_hybrid_trading(self):
        """Run hybrid trading with intelligent strategy selection"""
        print("🎯 STARTING HYBRID TRADING")
        print("🔄 DIFFERS + MATCHES with AI-powered switching")
        print("🤖 Strategy selection based on confidence and market conditions")

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

                    # Get comprehensive AI prediction
                    if len(self.recent_digits) >= 20 and len(self.recent_prices) >= 20:
                        ai_prediction = self.ai_predictor.get_comprehensive_prediction(
                            list(self.recent_digits),
                            list(self.recent_prices),
                            self.balance,
                            1.0
                        )

                        # Analyze market conditions
                        market_conditions = {
                            'volatility': self.ai_predictor.market_analyzer.analyze_volatility_patterns(
                                list(self.recent_prices)
                            ),
                            'session': ai_prediction.get('market_session'),
                            'momentum': self._calculate_momentum()
                        }

                        # Select optimal strategy
                        strategy, confidence = self.select_optimal_strategy(ai_prediction, market_conditions)

                        if strategy != 'WAIT' and confidence > 0:
                            predicted_digit = ai_prediction['predicted_digit']
                            hybrid_stake = self.calculate_hybrid_stake(strategy, confidence)

                            # Store prediction for accuracy tracking
                            self.last_prediction = predicted_digit
                            self.last_confidence = confidence
                            self.last_strategy = strategy

                            self.trades_made += 1

                            print(f"🎯 HYBRID TRADE #{self.trades_made}: {strategy} - ${hybrid_stake:.2f}")
                            print(f"   AI Confidence: {confidence:.1f}%")
                            print(f"   Market Volatility: {market_conditions['volatility']['volatility_score']:.6f}")
                            print(f"   Session: {market_conditions['session']}")

                            await self.place_hybrid_trade(strategy, predicted_digit, hybrid_stake)

                            # Log trade
                            trade_info = {
                                'trade_number': self.trades_made,
                                'strategy': strategy,
                                'predicted_digit': predicted_digit,
                                'stake': hybrid_stake,
                                'confidence': confidence,
                                'market_session': market_conditions['session'],
                                'volatility': market_conditions['volatility']['volatility_score']
                            }
                            self.performance_tracker.log_trade(trade_info)

                            # Wait between trades
                            await asyncio.sleep(3)
                        else:
                            print(f"🤖 AI SKIP: Strategy={strategy}, Confidence={confidence:.1f}%")

                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance

                    if profit != 0:
                        self.balance = new_balance

                        # Log AI prediction accuracy
                        if hasattr(self, 'last_prediction') and hasattr(self, 'last_confidence'):
                            if self.recent_digits:
                                actual_digit = self.recent_digits[-1]
                                self.ai_monitor.log_prediction(self.last_prediction, actual_digit, self.last_confidence)
                                print(f"🤖 AI Accuracy: {self.ai_monitor.get_accuracy():.1f}%")

                        # Update strategy performance
                        if hasattr(self, 'last_strategy'):
                            if profit > 0:
                                self.strategy_performance[self.last_strategy]['wins'] += 1
                                self.wins += 1
                            else:
                                self.strategy_performance[self.last_strategy]['losses'] += 1
                                self.losses += 1

                            self.strategy_performance[self.last_strategy]['trades'] += 1

                        # Update performance tracker
                        trade_result = {
                            'profit': profit,
                            'balance': self.balance,
                            'total_profit': total_profit,
                            'ai_accuracy': self.ai_monitor.get_accuracy(),
                            'strategy_used': getattr(self, 'last_strategy', 'UNKNOWN')
                        }
                        self.performance_tracker.log_trade(trade_result)

                        if profit > 0:
                            print(f"🎉 WIN! +${profit:.2f} | Total: +${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        else:
                            print(f"💔 LOSS: ${profit:.2f} | Total: ${total_profit:.2f} | Balance: ${self.balance:.2f}")

                        # Stop conditions
                        if self.wins >= 12:  # Higher target for hybrid
                            print("🎉 12 WINS ACHIEVED - HYBRID MISSION ACCOMPLISHED!")
                            self.is_trading = False
                        elif self.losses >= 4:  # Allow more losses for hybrid
                            print("⚠️ 4 LOSSES - STOPPING FOR SAFETY")
                            self.is_trading = False

            except asyncio.TimeoutError:
                print("⏰ Timeout - continuing...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break

        final_profit = self.balance - self.starting_balance
        print(f"\n📊 HYBRID TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins} | Losses: {self.losses}")
        print(f"Final Result: ${final_profit:.2f}")

        # Print strategy performance
        print("\n📈 STRATEGY PERFORMANCE:")
        for strategy, stats in self.strategy_performance.items():
            if stats['trades'] > 0:
                win_rate = (stats['wins'] / stats['trades']) * 100
                print(f"   {strategy}: {stats['trades']} trades, {stats['wins']}W/{stats['losses']}L ({win_rate:.1f}% win rate)")

        # Update final metrics
        self.performance_tracker.update_metrics('total_trades', self.trades_made)
        self.performance_tracker.update_metrics('wins', self.wins)
        self.performance_tracker.update_metrics('losses', self.losses)
        self.performance_tracker.update_metrics('final_profit', final_profit)
        self.performance_tracker.update_metrics('win_rate', (self.wins / self.trades_made) * 100 if self.trades_made > 0 else 0)

        # Log AI and strategy performance
        self.performance_tracker.log_ai_performance(
            self.ai_monitor.get_accuracy(),
            75.0,
            self.trades_made
        )

        # Save and generate report
        self.performance_tracker.save_session()
        report = self.performance_tracker.generate_report()
        print(report)

        if final_profit > 0:
            print("🎉 HYBRID STRATEGY SUCCESSFUL! 💰")

    def _calculate_momentum(self):
        """Calculate price momentum"""
        if len(self.recent_prices) < 5:
            return 0
        return (self.recent_prices[-1] - self.recent_prices[-5]) / self.recent_prices[-5]

async def main():
    print("🤖 AI-POWERED HYBRID TRADER - INTELLIGENT STRATEGY SWITCHING")
    print("=" * 70)
    print("🔄 Combines DIFFERS + MATCHES strategies")
    print("🎯 AI selects optimal strategy based on confidence and market conditions")
    print("💰 Dynamic position sizing per strategy")
    print("🎯 Target: 12 wins")
    print("🛑 Stop: 4 losses")
    print("🤖 AI Predictor: ACTIVE (Hybrid-optimized)")
    print("=" * 70)

    import os
    from dotenv import load_dotenv
    load_dotenv()

    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return

    trader = HybridTrader(api_token)

    if await trader.connect():
        await trader.run_hybrid_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())
