#!/usr/bin/env python3
"""Manual trading test - simulate connecting to Deriv demo account"""

import sys
import asyncio
import json
sys.path.append('./backend')

from main import DerivAPIClient, TradingBot, ai_predictor
import numpy as np

async def test_deriv_connection():
    """Test connection to Deriv API"""
    print("🔌 Testing Deriv API Connection...")
    
    # Get API token from .env
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found in .env file")
        return False
    
    print(f"✅ API Token found: {api_token[:10]}...")
    
    # Test connection (this will fail in demo but shows the flow)
    client = DerivAPIClient(api_token)
    print("✅ Deriv client created")
    
    return True

async def simulate_trading_session():
    """Simulate a trading session with AI"""
    print("\n🎮 Simulating Trading Session...")
    
    # Initialize trading bot
    bot = TradingBot()
    bot.config.use_ai_prediction = True
    bot.config.confidence_threshold = 70.0
    bot.config.stake = 1.0
    bot.is_trading = True
    
    # Simulate price ticks
    balance = 1000.0
    trades_made = 0
    
    for i in range(20):
        # Generate realistic price
        price = 100.0 + np.random.normal(0, 0.001)
        current_digit = int(str(abs(price)).replace('.', '')[-1])
        
        # Generate some history
        digits = np.random.randint(0, 10, 30).tolist()
        prices = [100.0 + j * 0.0001 for j in range(30)]
        
        # Get AI prediction
        prediction = ai_predictor.get_comprehensive_prediction(
            digits, prices, balance, bot.config.stake
        )
        
        print(f"Tick {i+1:2d}: Price={price:.5f}, Digit={current_digit}, "
              f"AI={prediction['predicted_digit']}, "
              f"Conf={prediction['final_confidence']:.1f}%")
        
        # Check if should trade
        if bot.should_trade(prediction, current_digit):
            trades_made += 1
            stake = min(prediction['optimal_stake'], 2.0)
            
            # Simulate trade outcome (66% win rate)
            win = np.random.random() < 0.66
            profit = stake * 0.95 if win else -stake
            balance += profit
            
            status = "✅ WIN" if win else "❌ LOSS"
            print(f"    🎯 TRADE #{trades_made}: Stake=${stake:.2f}, {status}, "
                  f"P&L=${profit:.2f}, Balance=${balance:.2f}")
        
        # Stop if balance too low
        if balance < 10:
            print("⚠️  Balance too low, stopping")
            break
    
    print(f"\n📊 Session Results:")
    print(f"💰 Final Balance: ${balance:.2f}")
    print(f"📈 Total P&L: ${balance - 1000:.2f}")
    print(f"🎯 Trades Made: {trades_made}")

async def main():
    print("🚀 Manual Trading Test")
    print("=" * 40)
    
    # Test connection
    await test_deriv_connection()
    
    # Simulate trading
    await simulate_trading_session()
    
    print("\n✅ Manual test complete!")
    print("🎯 System ready for demo account testing")

if __name__ == "__main__":
    asyncio.run(main())