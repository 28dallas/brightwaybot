#!/usr/bin/env python3
"""
Test script to verify the trading bot setup
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except ImportError as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except ImportError as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        from backend.ai_predictor_simple import EnhancedPredictor
        print("✅ AI Predictor imported successfully")
    except ImportError as e:
        print(f"❌ AI Predictor import failed: {e}")
        return False
    
    try:
        from backend.advanced_ai import UltraAdvancedPredictor
        print("✅ Advanced AI imported successfully")
    except ImportError as e:
        print(f"❌ Advanced AI import failed: {e}")
        return False
    
    return True

def test_ai_prediction():
    """Test AI prediction functionality"""
    print("\n🤖 Testing AI prediction...")
    
    try:
        from backend.ai_predictor_simple import EnhancedPredictor
        from backend.advanced_ai import UltraAdvancedPredictor
        
        # Create test data
        test_digits = [1, 2, 3, 4, 5, 6, 7, 8, 9, 0, 1, 2, 3, 4, 5]
        test_prices = [1206.59 + i * 0.01 for i in range(15)]
        
        # Test simple predictor
        predictor = EnhancedPredictor()
        prediction = predictor.get_comprehensive_prediction(test_digits, test_prices, 1000, 1.0)
        
        print(f"✅ Simple AI prediction: Digit {prediction['predicted_digit']}, Confidence: {prediction['final_confidence']:.1f}%")
        
        # Test advanced predictor
        advanced = UltraAdvancedPredictor()
        adv_prediction = advanced.ensemble_prediction(test_digits, test_prices)
        
        print(f"✅ Advanced AI prediction: Digit {adv_prediction['predicted_digit']}, Confidence: {adv_prediction['confidence']:.1f}%")
        
        return True
        
    except Exception as e:
        print(f"❌ AI prediction test failed: {e}")
        return False

def test_database():
    """Test database functionality"""
    print("\n💾 Testing database...")
    
    try:
        import sqlite3
        
        # Test database creation
        conn = sqlite3.connect("test_volatility_data.db")
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS test_ticks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME,
                price REAL,
                last_digit INTEGER
            )
        """)
        
        # Test insert
        cursor.execute(
            "INSERT INTO test_ticks (timestamp, price, last_digit) VALUES (?, ?, ?)",
            ("2024-01-01 12:00:00", 1206.59000, 9)
        )
        
        # Test select
        cursor.execute("SELECT * FROM test_ticks")
        result = cursor.fetchone()
        
        conn.commit()
        conn.close()
        
        # Clean up
        os.remove("test_volatility_data.db")
        
        print("✅ Database operations successful")
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    print("🔍 BRIGHTWAY TRADING BOT - SETUP TEST")
    print("=" * 40)
    
    all_tests_passed = True
    
    # Run tests
    all_tests_passed &= test_imports()
    all_tests_passed &= test_ai_prediction()
    all_tests_passed &= test_database()
    
    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Your setup is ready.")
        print("\n💡 Next steps:")
        print("1. Run: python start_trading.py")
        print("2. Open the frontend in your browser")
        print("3. Click 'Run Demo' to test")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        print("\n💡 Try installing missing dependencies:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()