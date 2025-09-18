#!/usr/bin/env python3
import sys
sys.path.append('./backend')

from ai_predictor_simple import EnhancedPredictor
import numpy as np

# Test the AI predictor
print("🧠 Testing AI Predictor System...")

# Create predictor
ai = EnhancedPredictor()

# Generate sample data (simulating real tick data)
np.random.seed(42)
sample_digits = np.random.randint(0, 10, 100).tolist()
sample_prices = [100.0 + np.random.normal(0, 0.001) for _ in range(100)]

print(f"📊 Sample data: {len(sample_digits)} digits, {len(sample_prices)} prices")

# Test prediction
prediction = ai.get_comprehensive_prediction(
    digits=sample_digits,
    prices=sample_prices,
    balance=1000.0,
    base_stake=1.0
)

print("\n🎯 AI Prediction Results:")
print(f"Predicted Digit: {prediction['predicted_digit']}")
print(f"Final Confidence: {prediction['final_confidence']:.1f}%")
print(f"Optimal Stake: ${prediction['optimal_stake']:.2f}")
print(f"Should Trade: {prediction['should_trade']}")
print(f"Market Session: {prediction['market_session']}")
print(f"Volatility Favorable: {prediction['volatility']['trade_favorable']}")

# Test multiple predictions
print("\n📈 Testing Multiple Predictions:")
for i in range(5):
    # Add new random digit
    sample_digits.append(np.random.randint(0, 10))
    sample_prices.append(sample_prices[-1] + np.random.normal(0, 0.001))
    
    pred = ai.get_comprehensive_prediction(sample_digits, sample_prices, 1000.0, 1.0)
    print(f"Prediction {i+1}: Digit={pred['predicted_digit']}, Confidence={pred['final_confidence']:.1f}%, Trade={pred['should_trade']}")

print(f"\n✅ AI System Test Complete! Prediction accuracy estimate: {ai.get_prediction_accuracy():.1f}%")