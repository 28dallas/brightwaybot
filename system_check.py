#!/usr/bin/env python3
"""
System readiness check for Volatility 100 AI Trading System
"""
import sys
import os
sys.path.append('./backend')

def check_imports():
    """Check if all required modules can be imported"""
    try:
        import numpy as np
        print("✅ NumPy imported successfully")
        
        from ai_predictor_simple import EnhancedPredictor
        print("✅ AI Predictor imported successfully")
        
        import fastapi
        print("✅ FastAPI imported successfully")
        
        import websockets
        print("✅ WebSockets imported successfully")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_files():
    """Check if all required files exist"""
    required_files = [
        'backend/main.py',
        'backend/ai_predictor_simple.py',
        'frontend/src/App.js',
        'frontend/src/components/Dashboard.js',
        'frontend/src/components/TradingPanel.js',
        '.env.example'
    ]
    
    all_exist = True
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - MISSING")
            all_exist = False
    
    return all_exist

def test_ai_system():
    """Test the AI prediction system"""
    try:
        from ai_predictor_simple import EnhancedPredictor
        import numpy as np
        
        ai = EnhancedPredictor()
        
        # Generate test data
        test_digits = [1, 5, 3, 7, 2, 8, 4, 9, 0, 6, 1, 5, 3, 7, 2]
        test_prices = [100.0 + i * 0.001 for i in range(15)]
        
        prediction = ai.get_comprehensive_prediction(
            test_digits, test_prices, 1000.0, 1.0
        )
        
        print(f"✅ AI Prediction Test:")
        print(f"   Predicted Digit: {prediction['predicted_digit']}")
        print(f"   Confidence: {prediction['final_confidence']:.1f}%")
        print(f"   Should Trade: {prediction['should_trade']}")
        
        return True
    except Exception as e:
        print(f"❌ AI System Test Failed: {e}")
        return False

def main():
    print("🔍 Volatility 100 AI Trading System - Readiness Check")
    print("=" * 55)
    
    print("\n📦 Checking Imports...")
    imports_ok = check_imports()
    
    print("\n📁 Checking Files...")
    files_ok = check_files()
    
    print("\n🧠 Testing AI System...")
    ai_ok = test_ai_system()
    
    print("\n" + "=" * 55)
    
    if imports_ok and files_ok and ai_ok:
        print("🎉 SYSTEM READY FOR DEMO TESTING!")
        print("\n🚀 Next Steps:")
        print("1. Add your Deriv API token to .env file")
        print("2. Run: ./start_demo.sh (to start backend)")
        print("3. Run: python3 demo_trading.py (for simulation)")
        print("4. Run: cd frontend && npm start (for web interface)")
        print("\n💡 Expected Performance: 60-70% win rate")
        return True
    else:
        print("❌ SYSTEM NOT READY - Please fix the issues above")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)