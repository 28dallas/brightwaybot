#!/usr/bin/env python3
"""Test script to verify balance functionality and trading"""

import asyncio
import json
import logging
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

async def test_balance():
    """Test balance fetching"""
    from backend.main import deriv_client

    print("🔍 Testing Balance Functionality")
    print("=" * 40)

    # Check if API token is set
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No DERIV_API_TOKEN found in .env file")
        print("💡 Please add your Deriv API token to the .env file")
        return False

    print(f"✅ API Token found: {api_token[:10]}...")

    # Test connection
    print("🔌 Testing Deriv API connection...")
    if await deriv_client.connect():
        print("✅ Connected to Deriv API successfully")

        # Test balance fetching
        print("💰 Testing balance fetching...")
        balance = await deriv_client.get_balance_with_retry()
        if balance is not None:
            print(f"✅ Balance fetched successfully: ${balance}")
            deriv_client.balance = balance
            return True
        else:
            print("❌ Failed to fetch balance")
            return False
    else:
        print("❌ Failed to connect to Deriv API")
        return False

async def test_trading_logic():
    """Test trading logic without placing real trades"""
    from backend.main import tracker, ai_predictor, trading_bot

    print("\n🤖 Testing Trading Logic")
    print("=" * 40)

    # Check if we have enough data
    if len(tracker.digits) < 50:
        print(f"⚠️  Not enough tick data: {len(tracker.digits)} ticks (need 50+)")
        print("💡 Wait for more market data to accumulate")
        return False

    print(f"✅ Have {len(tracker.digits)} ticks for analysis")

    # Test AI prediction
    try:
        prediction = ai_predictor.get_comprehensive_prediction(
            list(tracker.digits),
            list(tracker.prices),
            1000,  # Test balance
            1.0    # Test stake
        )
        print(f"✅ AI prediction successful: Digit {prediction.get('predicted_digit', '?')}, Confidence {prediction.get('final_confidence', 0)".1f"}%")
        return True
    except Exception as e:
        print(f"❌ AI prediction failed: {e}")
        return False

async def main():
    """Main test function"""
    print("🚀 Deriv Bot - Balance & Trading Test")
    print("=" * 50)

    # Test balance
    balance_ok = await test_balance()

    # Test trading logic
    trading_ok = await test_trading_logic()

    print("\n📊 Test Results:")
    print("=" * 30)
    print(f"Balance Test: {'✅ PASS' if balance_ok else '❌ FAIL'}")
    print(f"Trading Test: {'✅ PASS' if trading_ok else '❌ FAIL'}")

    if balance_ok and trading_ok:
        print("\n🎉 All tests passed! Your bot should be working correctly.")
        print("💡 Try starting AI-Optimized Trading in the frontend.")
    else:
        print("\n⚠️  Some tests failed. Check the issues above.")

    # Keep connection alive for manual testing
    print("\n🔄 Keeping connection alive for manual testing...")
    print("Press Ctrl+C to exit")

    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Test completed")

if __name__ == "__main__":
    asyncio.run(main())
