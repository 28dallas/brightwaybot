#!/usr/bin/env python3
"""Quick test to verify the system works"""

import sys
import os
sys.path.append('./backend')

# Test the complete system
print("🧪 Quick System Test")
print("=" * 30)

try:
    # Test AI predictor
    from ai_predictor_simple import EnhancedPredictor
    ai = EnhancedPredictor()
    
    # Generate sample data
    import numpy as np
    np.random.seed(42)
    digits = np.random.randint(0, 10, 50).tolist()
    prices = [100.0 + i * 0.001 for i in range(50)]
    
    # Get prediction
    pred = ai.get_comprehensive_prediction(digits, prices, 1000.0, 1.0)
    
    print(f"✅ AI Prediction: {pred['predicted_digit']}")
    print(f"✅ Confidence: {pred['final_confidence']:.1f}%")
    print(f"✅ Should Trade: {pred['should_trade']}")
    print(f"✅ Optimal Stake: ${pred['optimal_stake']:.2f}")
    
    # Test trading logic
    from main import TradingBot
    bot = TradingBot()
    bot.config.use_ai_prediction = True
    bot.config.confidence_threshold = 70.0
    
    should_trade = bot.should_trade(pred, pred['predicted_digit'])
    print(f"✅ Trading Decision: {'TRADE' if should_trade else 'WAIT'}")
    
    print("\n🎯 SYSTEM TEST PASSED!")
    print("Ready for demo account testing!")
    
    # Show configuration
    print(f"\n⚙️  Current Config:")
    print(f"   AI Prediction: {bot.config.use_ai_prediction}")
    print(f"   Confidence Threshold: {bot.config.confidence_threshold}%")
    print(f"   Auto Stake Sizing: {bot.config.auto_stake_sizing}")
    
except Exception as e:
    print(f"❌ Test Failed: {e}")
    import traceback
    traceback.print_exc()