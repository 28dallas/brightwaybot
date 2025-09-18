#!/usr/bin/env python3
"""CIRCUIT BREAKER SYSTEM - Prevents cascade failures"""

import asyncio
import time
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED"      # Normal operation
    OPEN = "OPEN"          # Blocking all requests
    HALF_OPEN = "HALF_OPEN"  # Testing if service recovered

class CircuitBreaker:
    def __init__(self, failure_threshold=3, recovery_timeout=60, expected_exception=Exception):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception
        
        self.failure_count = 0
        self.last_failure_time = None
        self.state = CircuitState.CLOSED
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                print("🔄 Circuit breaker: HALF_OPEN - Testing recovery")
            else:
                raise Exception("🚨 Circuit breaker OPEN - Service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            self._on_success()
            return result
        except self.expected_exception as e:
            self._on_failure()
            raise e
    
    def _should_attempt_reset(self):
        """Check if enough time has passed to attempt reset"""
        return (time.time() - self.last_failure_time) >= self.recovery_timeout
    
    def _on_success(self):
        """Handle successful operation"""
        self.failure_count = 0
        self.state = CircuitState.CLOSED
        if self.state == CircuitState.HALF_OPEN:
            print("✅ Circuit breaker: CLOSED - Service recovered")
    
    def _on_failure(self):
        """Handle failed operation"""
        self.failure_count += 1
        self.last_failure_time = time.time()
        
        if self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            print(f"🚨 Circuit breaker: OPEN - {self.failure_count} failures detected")

class TradingCircuitBreaker:
    def __init__(self):
        self.connection_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)
        self.trading_breaker = CircuitBreaker(failure_threshold=5, recovery_timeout=60)
        self.balance_breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=120)
    
    async def protected_connect(self, connect_func, *args, **kwargs):
        """Protected connection with circuit breaker"""
        return await self.connection_breaker.call(connect_func, *args, **kwargs)
    
    async def protected_trade(self, trade_func, *args, **kwargs):
        """Protected trading with circuit breaker"""
        return await self.trading_breaker.call(trade_func, *args, **kwargs)
    
    async def protected_balance_check(self, balance_func, *args, **kwargs):
        """Protected balance check with circuit breaker"""
        return await self.balance_breaker.call(balance_func, *args, **kwargs)
    
    def get_status(self):
        """Get status of all circuit breakers"""
        return {
            "connection": self.connection_breaker.state.value,
            "trading": self.trading_breaker.state.value,
            "balance": self.balance_breaker.state.value
        }

# Example usage in trading system
async def example_protected_trading():
    """Example of how to use circuit breakers in trading"""
    breaker = TradingCircuitBreaker()
    
    async def risky_connection():
        # Simulate connection that might fail
        import random
        if random.random() < 0.3:  # 30% failure rate
            raise ConnectionError("Connection failed")
        return "Connected successfully"
    
    async def risky_trade():
        # Simulate trade that might fail
        import random
        if random.random() < 0.4:  # 40% failure rate
            raise Exception("Trade failed")
        return "Trade successful"
    
    # Try operations with circuit breaker protection
    for i in range(10):
        try:
            # Protected connection
            result = await breaker.protected_connect(risky_connection)
            print(f"✅ Connection {i+1}: {result}")
            
            # Protected trading
            trade_result = await breaker.protected_trade(risky_trade)
            print(f"✅ Trade {i+1}: {trade_result}")
            
        except Exception as e:
            print(f"❌ Operation {i+1} failed: {e}")
        
        # Show circuit breaker status
        status = breaker.get_status()
        print(f"📊 Circuit Status: {status}")
        
        await asyncio.sleep(1)

if __name__ == "__main__":
    print("🔌 CIRCUIT BREAKER SYSTEM TEST")
    print("=" * 40)
    asyncio.run(example_protected_trading())