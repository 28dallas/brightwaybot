#!/usr/bin/env python3
"""Simple test to check if the backend is working"""

import requests
import time
import json

def test_backend():
    """Test if backend is running and responding"""
    print("🔍 Testing Backend Connection")
    print("=" * 40)

    try:
        # Test basic connection
        response = requests.get("http://localhost:8000/api/history", timeout=5)
        if response.status_code == 200:
            print("✅ Backend is running and responding")
            return True
        else:
            print(f"❌ Backend responded with status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend. Is it running?")
        print("💡 Try running: ./start_backend.sh")
        return False
    except Exception as e:
        print(f"❌ Error testing backend: {e}")
        return False

def test_ai_analysis():
    """Test AI analysis endpoint"""
    print("\n🤖 Testing AI Analysis")
    print("=" * 40)

    try:
        response = requests.get("http://localhost:8000/api/trading/ai-analysis", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ AI Analysis endpoint working")
            print(f"   Market volatility: {data.get('market_analysis', {}).get('volatility', 'unknown')}")
            print(f"   AI confidence: {data.get('market_analysis', {}).get('ai_consensus', 0) * 100".1f"}%")
            return True
        else:
            print(f"❌ AI Analysis failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error testing AI analysis: {e}")
        return False

def test_websocket():
    """Test WebSocket connection"""
    print("\n🌐 Testing WebSocket Connection")
    print("=" * 40)

    try:
        import websockets
        import asyncio

        async def test_ws():
            try:
                async with websockets.connect("ws://localhost:8000/ws") as websocket:
                    print("✅ WebSocket connected successfully")
                    # Send a test message
                    await websocket.send('{"test": "connection"}')
                    # Wait a bit
                    await asyncio.sleep(1)
                    return True
            except Exception as e:
                print(f"❌ WebSocket connection failed: {e}")
                return False

        return asyncio.run(test_ws())
    except ImportError:
        print("❌ websockets library not available")
        return False
    except Exception as e:
        print(f"❌ Error testing WebSocket: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Deriv Bot - System Test")
    print("=" * 50)

    # Test backend
    backend_ok = test_backend()

    if backend_ok:
        # Test AI analysis
        ai_ok = test_ai_analysis()

        # Test WebSocket
        ws_ok = test_websocket()

        print("\n📊 Test Results:")
        print("=" * 30)
        print(f"Backend: {'✅ PASS' if backend_ok else '❌ FAIL'}")
        print(f"AI Analysis: {'✅ PASS' if ai_ok else '❌ FAIL'}")
        print(f"WebSocket: {'✅ PASS' if ws_ok else '❌ FAIL'}")

        if backend_ok and ai_ok and ws_ok:
            print("\n🎉 All tests passed! Your bot should be working correctly.")
            print("💡 Try opening http://localhost:3000 in your browser")
        else:
            print("\n⚠️  Some tests failed. Check the issues above.")
    else:
        print("\n❌ Backend is not running. Please start it first.")

if __name__ == "__main__":
    main()
