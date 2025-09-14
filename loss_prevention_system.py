#!/usr/bin/env python3
"""COMPREHENSIVE LOSS PREVENTION SYSTEM"""

import asyncio
import websockets
import json
import sqlite3
import os
from datetime import datetime, timedelta
from collections import deque
import logging

class LossPreventionSystem:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        
        # Risk Management
        self.max_daily_loss = 10.0
        self.max_trade_size = 1.0
        self.min_balance = 5.0
        self.max_consecutive_losses = 3
        
        # State Tracking
        self.balance = 0
        self.starting_balance = 0
        self.daily_loss = 0
        self.consecutive_losses = 0
        self.trades_today = 0
        self.is_trading_allowed = True
        
        # Setup logging
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Initialize database
        self.init_database()
    
    def init_database(self):
        """Initialize SQLite database for trade tracking"""
        self.conn = sqlite3.connect('loss_prevention.db')
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY,
                timestamp TEXT,
                balance_before REAL,
                balance_after REAL,
                profit_loss REAL,
                trade_size REAL,
                status TEXT
            )
        ''')
        self.conn.commit()
    
    async def connect_safely(self):
        """Connect with multiple safety checks"""
        try:
            self.ws = await websockets.connect(
                "wss://ws.derivws.com/websockets/v3?app_id=1089",
                ping_interval=20,
                ping_timeout=10
            )
            
            # Authorize
            auth_msg = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_msg))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if "error" in auth_data:
                self.logger.error(f"Authorization failed: {auth_data['error']}")
                return False
            
            # Get balance
            await self.ws.send(json.dumps({"balance": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance
            
            self.logger.info(f"✅ Connected safely. Balance: ${self.balance}")
            
            # Check if balance is above minimum
            if self.balance < self.min_balance:
                self.logger.error(f"❌ Balance ${self.balance} below minimum ${self.min_balance}")
                self.is_trading_allowed = False
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Connection failed: {e}")
            return False
    
    def check_risk_limits(self, trade_size):
        """Check all risk limits before trading"""
        checks = []
        
        # Balance check
        if self.balance < self.min_balance:
            checks.append(f"❌ Balance ${self.balance} below minimum ${self.min_balance}")
        
        # Daily loss check
        if self.daily_loss >= self.max_daily_loss:
            checks.append(f"❌ Daily loss ${self.daily_loss} exceeds limit ${self.max_daily_loss}")
        
        # Trade size check
        if trade_size > self.max_trade_size:
            checks.append(f"❌ Trade size ${trade_size} exceeds maximum ${self.max_trade_size}")
        
        # Consecutive losses check
        if self.consecutive_losses >= self.max_consecutive_losses:
            checks.append(f"❌ {self.consecutive_losses} consecutive losses - trading suspended")
        
        # Balance percentage check (never risk more than 10% of balance)
        max_risk = self.balance * 0.1
        if trade_size > max_risk:
            checks.append(f"❌ Trade size ${trade_size} exceeds 10% of balance (${max_risk:.2f})")
        
        if checks:
            for check in checks:
                self.logger.warning(check)
            self.is_trading_allowed = False
            return False
        
        return True
    
    async def place_protected_trade(self, digit, stake):
        """Place trade with full protection"""
        if not self.is_trading_allowed:
            self.logger.warning("🛑 Trading not allowed - risk limits exceeded")
            return None
        
        if not self.check_risk_limits(stake):
            return None
        
        # Record pre-trade state
        pre_balance = self.balance
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "DIGITMATCH",
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": str(digit)
            }
        }
        
        try:
            await self.ws.send(json.dumps(trade_msg))
            response = await asyncio.wait_for(self.ws.recv(), timeout=10)
            result = json.loads(response)
            
            if "buy" in result:
                self.trades_today += 1
                self.logger.info(f"✅ Protected trade placed: ${stake} on digit {digit}")
                
                # Log to database
                self.conn.execute('''
                    INSERT INTO trades (timestamp, balance_before, trade_size, status)
                    VALUES (?, ?, ?, ?)
                ''', (datetime.now().isoformat(), pre_balance, stake, 'PLACED'))
                self.conn.commit()
                
                return result
            else:
                self.logger.error(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            self.logger.error(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    def update_balance(self, new_balance):
        """Update balance and check for losses"""
        old_balance = self.balance
        profit_loss = new_balance - old_balance
        self.balance = new_balance
        
        # Update daily loss
        if profit_loss < 0:
            self.daily_loss += abs(profit_loss)
            self.consecutive_losses += 1
            self.logger.warning(f"💔 Loss: ${profit_loss:.2f} | Daily loss: ${self.daily_loss:.2f}")
        else:
            self.consecutive_losses = 0  # Reset on win
            if profit_loss > 0:
                self.logger.info(f"💚 Win: +${profit_loss:.2f}")
        
        # Update database
        self.conn.execute('''
            UPDATE trades SET balance_after = ?, profit_loss = ?
            WHERE id = (SELECT MAX(id) FROM trades)
        ''', (new_balance, profit_loss))
        self.conn.commit()
        
        # Check if we need to stop trading
        if self.daily_loss >= self.max_daily_loss:
            self.is_trading_allowed = False
            self.logger.error(f"🚨 DAILY LOSS LIMIT REACHED: ${self.daily_loss}")
        
        if self.consecutive_losses >= self.max_consecutive_losses:
            self.is_trading_allowed = False
            self.logger.error(f"🚨 CONSECUTIVE LOSS LIMIT REACHED: {self.consecutive_losses}")
        
        if self.balance < self.min_balance:
            self.is_trading_allowed = False
            self.logger.error(f"🚨 MINIMUM BALANCE REACHED: ${self.balance}")
    
    async def emergency_stop(self):
        """Emergency stop all trading"""
        self.is_trading_allowed = False
        self.logger.error("🚨 EMERGENCY STOP ACTIVATED")
        
        # Close websocket
        if self.ws:
            await self.ws.close()
        
        # Final report
        total_loss = self.starting_balance - self.balance
        self.logger.info(f"📊 EMERGENCY STOP REPORT:")
        self.logger.info(f"Starting Balance: ${self.starting_balance}")
        self.logger.info(f"Current Balance: ${self.balance}")
        self.logger.info(f"Total Loss: ${total_loss:.2f}")
        self.logger.info(f"Trades Today: {self.trades_today}")
    
    async def run_protected_trading(self):
        """Run trading with full loss prevention"""
        self.logger.info("🛡️ STARTING PROTECTED TRADING")
        
        # Subscribe to ticks and balance
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
        
        tick_count = 0
        
        while self.is_trading_allowed and self.trades_today < 5:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    tick_count += 1
                    
                    self.logger.info(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Conservative trading - only every 10th tick
                    if tick_count >= 10 and tick_count % 10 == 0:
                        # Use very conservative stake
                        safe_stake = min(0.35, self.balance * 0.05)  # Max 5% of balance
                        
                        # Target most common digit (5)
                        target_digit = 5
                        
                        self.logger.info(f"🎯 Protected trade: ${safe_stake} on digit {target_digit}")
                        await self.place_protected_trade(target_digit, safe_stake)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    if new_balance != self.balance:
                        self.update_balance(new_balance)
                
            except asyncio.TimeoutError:
                self.logger.warning("⏰ Timeout - checking connection")
                break
            except Exception as e:
                self.logger.error(f"❌ Error: {e}")
                await self.emergency_stop()
                break
        
        # Final report
        final_loss = self.starting_balance - self.balance
        self.logger.info(f"📊 PROTECTED TRADING COMPLETE")
        self.logger.info(f"Final Loss: ${final_loss:.2f}")
        self.logger.info(f"Daily Loss Limit: ${self.max_daily_loss}")
        self.logger.info(f"Trades Made: {self.trades_today}")

async def main():
    print("🛡️ COMPREHENSIVE LOSS PREVENTION SYSTEM")
    print("=" * 50)
    print("🚨 Maximum daily loss: $10")
    print("💰 Minimum balance: $5")
    print("🛑 Max consecutive losses: 3")
    print("📊 Max trade size: $1")
    print("=" * 50)
    
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    system = LossPreventionSystem(api_token)
    
    if await system.connect_safely():
        await system.run_protected_trading()
    else:
        print("❌ Failed to connect safely")

if __name__ == "__main__":
    asyncio.run(main())