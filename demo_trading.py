#!/usr/bin/env python3
import sys
sys.path.append('./backend')

from ai_predictor_simple import EnhancedPredictor
import numpy as np
import time
import random

class DemoTrader:
    def __init__(self):
        self.ai = EnhancedPredictor()
        self.balance = 1000.0
        self.total_trades = 0
        self.wins = 0
        self.losses = 0
        self.digits_history = []
        self.prices_history = []
        
    def simulate_tick(self):
        """Simulate a new price tick"""
        if not self.prices_history:
            price = 100.0
        else:
            # Simulate realistic price movement
            price = self.prices_history[-1] + np.random.normal(0, 0.001)
        
        digit = int(str(abs(price)).replace('.', '')[-1])
        
        self.digits_history.append(digit)
        self.prices_history.append(price)
        
        return price, digit
    
    def place_trade(self, predicted_digit, stake, strategy='matches'):
        """Simulate placing a trade"""
        # Simulate next tick
        next_price, next_digit = self.simulate_tick()
        
        # Determine win/loss
        if strategy == 'matches':
            win = (next_digit == predicted_digit)
        else:  # differs
            win = (next_digit != predicted_digit)
        
        # Calculate profit/loss (95% payout typical for Deriv)
        if win:
            profit = stake * 0.95
            self.wins += 1
        else:
            profit = -stake
            self.losses += 1
        
        self.balance += profit
        self.total_trades += 1
        
        return {
            'win': win,
            'profit': profit,
            'next_digit': next_digit,
            'predicted_digit': predicted_digit
        }
    
    def run_demo(self, num_ticks=50):
        """Run demo trading session"""
        print("🚀 Starting Demo Trading Session")
        print(f"💰 Starting Balance: ${self.balance:.2f}")
        print("=" * 50)
        
        # Generate initial data
        for _ in range(20):
            self.simulate_tick()
        
        trades_made = 0
        
        for tick in range(num_ticks):
            # Simulate new tick
            price, current_digit = self.simulate_tick()
            
            # Get AI prediction
            prediction = self.ai.get_comprehensive_prediction(
                self.digits_history,
                self.prices_history,
                self.balance,
                1.0  # Base stake
            )
            
            print(f"Tick {tick+1:2d}: Price={price:.5f}, Digit={current_digit}, "
                  f"AI Pred={prediction['predicted_digit']}, "
                  f"Conf={prediction['final_confidence']:.1f}%")
            
            # Check if AI recommends trading
            if prediction['should_trade'] and prediction['final_confidence'] >= 70:
                # Use AI prediction and optimal stake
                stake = min(prediction['optimal_stake'], 5.0)  # Cap at $5
                
                if stake > 0 and self.balance >= stake:
                    result = self.place_trade(
                        prediction['predicted_digit'],
                        stake,
                        'matches'  # Using matches strategy
                    )
                    
                    trades_made += 1
                    status = "✅ WIN" if result['win'] else "❌ LOSS"
                    
                    print(f"    🎯 TRADE #{trades_made}: Stake=${stake:.2f}, "
                          f"Next={result['next_digit']}, {status}, "
                          f"P&L=${result['profit']:.2f}, Balance=${self.balance:.2f}")
            
            # Stop if balance too low
            if self.balance < 1.0:
                print("⚠️  Balance too low, stopping demo")
                break
        
        # Final results
        print("\n" + "=" * 50)
        print("📊 DEMO TRADING RESULTS")
        print("=" * 50)
        print(f"💰 Final Balance: ${self.balance:.2f}")
        print(f"📈 Total P&L: ${self.balance - 1000:.2f}")
        print(f"🎯 Total Trades: {self.total_trades}")
        print(f"✅ Wins: {self.wins}")
        print(f"❌ Losses: {self.losses}")
        
        if self.total_trades > 0:
            win_rate = (self.wins / self.total_trades) * 100
            print(f"🏆 Win Rate: {win_rate:.1f}%")
            
            if win_rate >= 60:
                print("🎉 EXCELLENT! Win rate above 60%")
            elif win_rate >= 50:
                print("👍 GOOD! Win rate above 50%")
            else:
                print("⚠️  Win rate needs improvement")
        
        return {
            'final_balance': self.balance,
            'total_trades': self.total_trades,
            'wins': self.wins,
            'losses': self.losses,
            'win_rate': (self.wins / self.total_trades * 100) if self.total_trades > 0 else 0
        }

if __name__ == "__main__":
    print("🎮 Volatility 100 AI Trading Demo")
    print("This simulates trading with your AI system")
    print()
    
    trader = DemoTrader()
    results = trader.run_demo(100)  # Run 100 ticks
    
    print(f"\n🎯 Ready for live demo account testing!")
    print(f"Expected performance: {results['win_rate']:.1f}% win rate")