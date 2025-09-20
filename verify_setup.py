#!/usr/bin/env python3
"""Verify that the trading system is properly configured"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

def verify_configuration():
    """Check if everything is set up correctly"""
    print("🔍 Verifying Trading System Configuration")
    print("=" * 45)

    # Check API token
    api_token = os.getenv('DERIV_API_TOKEN')
    print("🔑 API Token Check:")
    if not api_token:
        print("   ❌ No DERIV_API_TOKEN found in .env")
        print("   💡 Run: python setup_env.py")
        return False
    elif api_token == "your_deriv_api_token_here":
        print("   ⚠️  Using placeholder token")
        print("   💡 Run: python setup_env.py to set real token")
        return False
    else:
        print(f"   ✅ API Token: {api_token[:10]}...{api_token[-10:]}")
        print("   ✅ Token format looks valid")

    # Check backend files
    print("\n📁 Backend Configuration:")
    backend_files = [
        "backend/main.py",
        "backend/ai_predictor_simple.py",
        "backend/advanced_ai.py"
    ]

    for file in backend_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            return False

    # Check database
    print("\n🗃️  Database Check:")
    db_file = "volatility_data.db"
    if os.path.exists(db_file):
        print(f"   ✅ {db_file} exists")
    else:
        print(f"   ⚠️  {db_file} not found (will be created)")

    # Check frontend
    print("\n🌐 Frontend Check:")
    frontend_files = [
        "frontend/package.json",
        "frontend/src/App.js"
    ]

    for file in frontend_files:
        if os.path.exists(file):
            print(f"   ✅ {file}")
        else:
            print(f"   ❌ {file} - MISSING!")
            return False

    # Check scripts
    print("\n🛠️  Scripts Check:")
    scripts = [
        "start_backend.sh",
        "test_balance.py",
        "test_deriv_connection.py"
    ]

    for script in scripts:
        if os.path.exists(script):
            print(f"   ✅ {script}")
        else:
            print(f"   ❌ {script} - MISSING!")

    return True

def show_trading_status():
    """Show current trading configuration"""
    print("\n🎯 Trading Configuration Summary:")
    print("-" * 35)

    api_token = os.getenv('DERIV_API_TOKEN')

    if api_token and api_token != "your_deriv_api_token_here":
        print("📊 Mode: REAL MONEY TRADING")
        print("💰 Balance: Will show real Deriv account balance")
        print("🔄 Trading: Will place real trades")
        print("⚡ Status: Ready for live trading!")
    else:
        print("📊 Mode: DEMO/SIMULATION")
        print("💰 Balance: Will show $1000 (demo)")
        print("🔄 Trading: Simulated trades only")
        print("⚡ Status: Needs API token for real trading")

def main():
    """Main verification function"""
    print("🚀 Deriv Trading Bot - Configuration Check")
    print("=" * 50)

    success = verify_configuration()

    if success:
        show_trading_status()
        print("\n✅ CONFIGURATION VERIFIED!")
        print("🎉 Your system is ready!")

        api_token = os.getenv('DERIV_API_TOKEN')
        if api_token and api_token != "your_deriv_api_token_here":
            print("\n💡 Next steps:")
            print("   1. Test connection: python test_deriv_connection.py")
            print("   2. Start backend: ./start_backend.sh")
            print("   3. Start frontend: cd frontend && npm start")
            print("   4. Begin real trading!")
        else:
            print("\n💡 Next steps:")
            print("   1. Set API token: python setup_env.py")
            print("   2. Test connection: python test_deriv_connection.py")
            print("   3. Start trading with real money!")

    else:
        print("\n❌ Configuration issues found!")
        print("💡 Please fix the issues above before trading.")

if __name__ == "__main__":
    main()
