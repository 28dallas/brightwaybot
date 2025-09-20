#!/usr/bin/env python3
"""Test script to verify balance functionality"""

import asyncio
import json
import websockets
import os
from dotenv import load_dotenv

load_dotenv()

async def test_balance():
    """Test WebSocket connection and balance updates"""
    print("🧪 Testing Balance Functionality")
    print("=" * 40)

    try:
        # Connect to WebSocket
        uri = "ws://localhost:8000/ws"
        print(f"🔌 Connecting to {uri}...")

        async with websockets.connect(uri) as websocket:
            print("✅ Connected to WebSocket")

            # Listen for balance updates
            for i in range(10):  # Listen for 10 seconds
                try:
                    message = await websocket.recv()
                    data = json.loads(message)

                    print(f"📊 Update {i+1}:")
                    print(f"   Balance: ${data.get('balance', 'N/A')}")
                    print(f"   P&L: ${data.get('pnl', 'N/A')}")
                    print(f"   Trades: {data.get('total_trades', 0)}")
                    print(f"   Trading: {data.get('is_trading', False)}")
                    print("-" * 20)

                except Exception as e:
                    print(f"❌ Error receiving data: {e}")
                    break

                await asyncio.sleep(1)

    except Exception as e:
        print(f"❌ Connection failed: {e}")
        print("💡 Make sure the backend server is running:")
        print("   ./start_backend.sh")

if __name__ == "__main__":
    asyncio.run(test_balance())
