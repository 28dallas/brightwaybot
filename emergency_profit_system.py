#!/usr/bin/env python3
"""EMERGENCY PROFIT SYSTEM - Reverse Strategy"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque, Counter

class EmergencyProfitTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.digits = deque(maxlen=50)
        self.prices = deque(maxlen=50)
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        
    async def connect(self):
        try:
            self.ws = await websockets.connect("wss://ws.derivws.com/websockets/v3?app_id=1089")
            
            auth_msg = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_msg))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if "error" in auth_data:
                print(f"❌ Authorization failed: {auth_data['error']}")
                return False
                
            print("🚨 EMERGENCY PROFIT SYSTEM ACTIVE")
            
            # Get balance
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            print(f"💰 Current Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_winning_strategy(self):
        """REVERSE STRATEGY - Use what's been losing"""
        if len(self.digits) < 20:
            return None
        
        recent = list(self.digits)[-20:]
        counter = Counter(recent)
        
        # Find LEAST frequent digit (reverse psychology)
        least_frequent = counter.most_common()[-1][0]
        
        # Find gaps - digits that haven't appeared
        all_digits = set(range(10))
        recent_digits = set(recent)
        missing_digits = all_digits - recent_digits
        
        if missing_digits:
            # Pick a missing digit
            chosen_digit = min(missing_digits)
        else:
            # Pick least frequent
            chosen_digit = least_frequent
        
        # Very conservative confidence
        confidence = 60.0  # Lower threshold
        
        return {
            'digit': chosen_digit,
            'confidence': confidence,
            'strategy': 'REVERSE'
        }
    
    async def place_emergency_trade(self, digit, stake=0.35):
        """Place small emergency trade"""
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
        
        await self.ws.send(json.dumps(trade_msg))
        response = await self.ws.recv()
        return json.loads(response)
    
    async def run_emergency_trading(self):
        """Emergency trading with reverse strategy"""
        print("🚨 STARTING EMERGENCY RECOVERY")
        print("📊 Using REVERSE STRATEGY")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        while self.is_trading and self.trades_made < 10:  # Limit trades
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.prices.append(price)
                    self.digits.append(current_digit)
                    
                    print(f"📈 {price:.5f} | Digit: {current_digit}")
                    
                    # Get reverse strategy
                    strategy = self.get_winning_strategy()
                    
                    if strategy and len(self.digits) >= 25:
                        print(f"🔄 REVERSE: Target digit {strategy['digit']}")
                        
                        # Only trade if current digit matches our target
                        if current_digit == strategy['digit']:
                            self.trades_made += 1
                            
                            print(f"🎯 EMERGENCY TRADE #{self.trades_made}: $0.35 on digit {strategy['digit']}")
                            
                            result = await self.place_emergency_trade(strategy['digit'])
                            
                            if "buy" in result:
                                print(f"✅ Trade placed: {result['buy']['contract_id']}")
                            else:
                                print(f"❌ Trade failed: {result}")
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    self.balance = new_balance
                    
                    if profit > 0:
                        self.wins += 1
                        print(f"💚 WIN! +${profit:.2f} | Balance: ${self.balance:.2f}")
                    elif profit < 0:
                        print(f"💔 Loss: ${profit:.2f} | Balance: ${self.balance:.2f}")
                    
                    # Stop if we get 3 wins or 5 losses
                    if self.wins >= 3:
                        print("🎉 3 WINS ACHIEVED - STOPPING FOR SAFETY")
                        self.is_trading = False
                    elif self.trades_made - self.wins >= 5:
                        print("⚠️ 5 LOSSES - STOPPING TO PRESERVE CAPITAL")
                        self.is_trading = False
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        print(f"\n📊 EMERGENCY SESSION COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Balance: ${self.balance}")

async def main():
    print("🚨 EMERGENCY PROFIT RECOVERY SYSTEM")
    print("=" * 40)
    print("🔄 Using REVERSE STRATEGY")
    print("💰 Small stakes ($0.35)")
    print("🛑 Auto-stop after 3 wins or 5 losses")
    print("=" * 40)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = EmergencyProfitTrader(api_token)
    
    if await trader.connect():
        await trader.run_emergency_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())