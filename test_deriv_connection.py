#!/usr/bin/env python3
"""Test script to verify Deriv API token connection"""

import asyncio
import json
import os
import websockets
from dotenv import load_dotenv

load_dotenv()

async def test_deriv_token():
    """Test if Deriv API token is working"""
    print("🔐 Testing Deriv API Token Connection")
    print("=" * 40)

    # Get token from environment
    api_token = os.getenv('DERIV_API_TOKEN')

    if not api_token:
        print("❌ No DERIV_API_TOKEN found in .env file")
        print("💡 Please add your token to .env file:")
        print("   DERIV_API_TOKEN=your_actual_token_here")
        return False

    if api_token == "your_deriv_api_token_here":
        print("⚠️  Using placeholder token - this won't work!")
        print("💡 Please replace with your real Deriv API token")
        return False

    print(f"🔑 API Token: {api_token[:10]}...{api_token[-10:]}")
    print("🌐 Connecting to Deriv API...")

    try:
        # Connect to Deriv WebSocket
        ws = await websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")

        # Authorize with token
        auth_msg = {"authorize": api_token}
        await ws.send(json.dumps(auth_msg))

        # Get response
        response = await ws.recv()
        data = json.loads(response)

        if "error" in data:
            print(f"❌ Authorization failed: {data['error']['message']}")
            return False

        if "authorize" in data:
            account_info = data["authorize"]
            print("✅ Successfully connected to Deriv!")
            print(f"👤 Account: {account_info.get('email', 'Demo Account')}")
            print(f"💰 Currency: {account_info.get('currency', 'USD')}")
            print(f"🏦 Account Type: {account_info.get('account_type', 'Demo')}")

            # Get balance
            await ws.send(json.dumps({"balance": 1, "subscribe": 0}))
            balance_response = await ws.recv()
            balance_data = json.loads(balance_response)

            if "balance" in balance_data:
                balance = balance_data["balance"]["balance"]
                print(f"💵 Current Balance: ${balance}")
                print("✅ Balance retrieved successfully!")
                return True
            else:
                print("⚠️  Could not retrieve balance")
                return False

    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

    finally:
        try:
            await ws.close()
        except:
            pass

async def main():
    """Main test function"""
    print("🚀 Deriv API Connection Test")
    print("=" * 40)

    success = await test_deriv_token()

    if success:
        print("\n🎉 SUCCESS: Your API token is working!")
        print("✅ You can now trade with real money")
        print("💡 Start your trading bot:")
        print("   ./start_backend.sh")
    else:
        print("\n❌ FAILED: Please fix your API token")
        print("💡 Get your token from: https://app.deriv.com/account/api-token")

if __name__ == "__main__":
    asyncio.run(main())
