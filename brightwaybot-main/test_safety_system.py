#!/usr/bin/env python3
"""
Test Safety System - Demonstrates the integrated loss prevention system
"""

from integrated_safety_system import IntegratedSafetySystem
import time

def test_safety_system():
    """Test the integrated safety system"""
    print("=== Testing Integrated Safety System ===\n")
    
    # Initialize safety system
    safety = IntegratedSafetySystem()
    
    # Test 1: System Status
    print("1. Checking system status...")
    status = safety.get_system_status()
    print(f"   Health: {status['health']['status']}")
    print(f"   CPU: {status['health']['cpu_percent']:.1f}%")
    print(f"   Memory: {status['health']['memory_percent']:.1f}%")
    print(f"   Circuit Breaker: {status['circuit_breaker']['status']}")
    
    # Test 2: Trade Safety Check
    print("\n2. Testing trade safety checks...")
    
    test_trades = [
        (10.0, "EUR/USD"),
        (50.0, "GBP/USD"),
        (100.0, "USD/JPY")
    ]
    
    for amount, symbol in test_trades:
        safe = safety.check_trade_safety(amount, symbol)
        print(f"   Trade ${amount} {symbol}: {'SAFE' if safe else 'BLOCKED'}")
    
    # Test 3: Record Trade Results
    print("\n3. Recording trade results...")
    
    # Simulate some trades
    trade_results = [
        (5.0, True),   # Profit
        (-2.0, False), # Loss
        (8.0, True),   # Profit
        (-15.0, False) # Large loss
    ]
    
    for profit_loss, success in trade_results:
        safety.record_trade_result(profit_loss, success)
        result_type = "PROFIT" if profit_loss > 0 else "LOSS"
        print(f"   Recorded {result_type}: ${abs(profit_loss)}")
    
    # Test 4: Final Status
    print("\n4. Final system status...")
    final_status = safety.get_system_status()
    print(f"   Balance: ${final_status['loss_prevention']['current_balance']:.2f}")
    print(f"   Daily Loss: ${final_status['loss_prevention']['daily_loss']:.2f}")
    print(f"   Can Trade: {final_status['loss_prevention']['can_trade']}")
    print(f"   Circuit Breaker Failures: {final_status['circuit_breaker']['failure_count']}")
    
    print("\n=== Safety System Test Complete ===")

if __name__ == "__main__":
    test_safety_system()