#!/usr/bin/env python3
"""Test AI-enhanced trading under various market conditions"""

import sys
sys.path.append('./backend')

from backend.ai_predictor import EnhancedPredictor
import numpy as np
import random

def generate_market_data(condition, num_ticks=100):
    """Generate synthetic market data for different conditions"""
    if condition == 'high_volatility':
        # High volatility: rapid price changes
        base_price = 1.2345
        prices = []
        digits = []
        for i in range(num_ticks):
            change = np.random.normal(0, 0.005)  # High volatility
            price = base_price + change
            prices.append(price)
            digits.append(int(str(price).replace(".", "")[-1]))
            base_price = price

    elif condition == 'low_volatility':
        # Low volatility: stable prices
        base_price = 1.2345
        prices = []
        digits = []
        for i in range(num_ticks):
            change = np.random.normal(0, 0.0005)  # Low volatility
            price = base_price + change
            prices.append(price)
            digits.append(int(str(price).replace(".", "")[-1]))
            base_price = price

    elif condition == 'trending':
        # Trending market
        base_price = 1.2345
        prices = []
        digits = []
        trend = 0.001  # Upward trend
        for i in range(num_ticks):
            change = trend + np.random.normal(0, 0.001)
            price = base_price + change
            prices.append(price)
            digits.append(int(str(price).replace(".", "")[-1]))
            base_price = price

    elif condition == 'sideways':
        # Sideways market
        base_price = 1.2345
        prices = []
        digits = []
        for i in range(num_ticks):
            change = np.random.normal(0, 0.001)
            price = base_price + change
            prices.append(price)
            digits.append(int(str(price).replace(".", "")[-1]))
            base_price = price

    elif condition == 'patterned':
        # Patterned digits (repeating sequences)
        digits = []
        pattern = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0]
        for i in range(num_ticks):
            digits.append(pattern[i % len(pattern)])

        # Generate corresponding prices
        prices = []
        base_price = 1.2345
        for i in range(num_ticks):
            change = np.random.normal(0, 0.001)
            price = base_price + change
            prices.append(price)
            base_price = price

    return digits, prices

def test_ai_under_conditions():
    """Test AI performance under different market conditions"""
    predictor = EnhancedPredictor()

    conditions = ['high_volatility', 'low_volatility', 'trending', 'sideways', 'patterned']

    print("🧪 TESTING AI-ENHANCED TRADING UNDER VARIOUS MARKET CONDITIONS")
    print("=" * 70)

    for condition in conditions:
        print(f"\n📊 Testing: {condition.upper()}")
        print("-" * 40)

        digits, prices = generate_market_data(condition, 200)

        # Test AI predictions
        trades_taken = 0
        profitable_trades = 0

        for i in range(50, len(digits) - 1):
            recent_digits = digits[:i]
            recent_prices = prices[:i]

            prediction = predictor.get_comprehensive_prediction(
                recent_digits, recent_prices, 1000, 1.0
            )

            if prediction['should_trade'] and prediction['final_confidence'] >= 70:
                trades_taken += 1
                predicted_digit = prediction['predicted_digit']
                actual_next_digit = digits[i]

                # For DIFFERS strategy: win if actual != predicted
                if actual_next_digit != predicted_digit:
                    profitable_trades += 1

        if trades_taken > 0:
            win_rate = (profitable_trades / trades_taken) * 100
            print(f"   Trades Taken: {trades_taken}")
            print(f"   Profitable Trades: {profitable_trades}")
            print(f"   Win Rate: {win_rate:.1f}%")
            print(f"   AI Confidence Avg: {prediction['final_confidence']:.1f}%")
        else:
            print("   No trades taken under current conditions")

    print("\n✅ MARKET CONDITION TESTING COMPLETE")

if __name__ == "__main__":
    test_ai_under_conditions()
