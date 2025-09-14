#!/usr/bin/env python3
"""ULTRA CONSERVATIVE - Only trade on 95%+ confidence with perfect conditions"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque
from datetime import datetime

class UltraConservative:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        
        # Data storage
        self.digits = deque(maxlen=50)
        self.prices = deque(maxlen=50)
        
    async def connect(self):
        try:
            self.ws = await websockets.connect(
                "wss://ws.derivws.com/websockets/v3?app_id=1089",
                ping_interval=20,
                ping_timeout=10
            )
            
            auth_msg = {"authorize": self.api_token}
            await self.ws.send(json.dumps(auth_msg))
            response = await self.ws.recv()
            auth_data = json.loads(response)
            
            if "error" in auth_data:
                print(f"❌ Authorization failed: {auth_data['error']}")
                return False
                
            print("🚀 ULTRA CONSERVATIVE SYSTEM CONNECTED")
            
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            self.starting_balance = self.balance
            print(f"💰 Starting Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def analyze_pattern(self):
        """Ultra-conservative pattern analysis"""
        if len(self.digits) < 30:
            return None
        
        recent = list(self.digits)[-20:]
        
        # Count digit frequencies
        counts = {}
        for d in recent:
            counts[d] = counts.get(d, 0) + 1
        
        # Find most frequent digit
        most_frequent = max(counts, key=counts.get)
        frequency = counts[most_frequent]
        
        # Only trade if digit appears 6+ times in last 20 ticks (30%+ frequency)
        if frequency >= 6:
            confidence = min(frequency * 15 + 10, 98)  # Cap at 98%
            
            # Additional checks for ultra-conservative approach
            volatility = np.std(list(self.prices)[-15:]) if len(self.prices) >= 15 else 0
            
            # Perfect conditions required
            perfect_conditions = (
                confidence >= 95 and
                frequency >= 7 and  # Very high frequency
                volatility < 0.5 and  # Low volatility
                most_frequent != 0  # Avoid digit 0
            )
            
            if perfect_conditions:
                return {
                    'digit': most_frequent,
                    'confidence': confidence,
                    'frequency': frequency,
                    'should_trade': True
                }
        
        return None
    
    async def place_conservative_trade(self, prediction):
        """Place ultra-conservative trade"""
        digit = prediction['digit']
        stake = 0.35  # Minimum stake only
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": "DIGITDIFF",
                "currency": "USD",
                "duration": 1,
                "duration_unit": "t",
                "symbol": "R_100",
                "barrier": str(digit)
            }
        }
        
        try:
            await self.ws.send(json.dumps(trade_msg))
            response = await self.ws.recv()
            result = json.loads(response)
            
            if "buy" in result:
                contract_id = result['buy']['contract_id']
                print(f"🚀 CONSERVATIVE TRADE: Contract {contract_id}")
                print(f"   DIFFERS on digit {digit} (appears {prediction['frequency']}/20 times)")
                print(f"   Confidence: {prediction['confidence']:.1f}%")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_conservative_system(self):
        """Run ultra-conservative system"""
        print("🚀 STARTING ULTRA CONSERVATIVE SYSTEM")
        print("🛡️ Only trading on 95%+ confidence with perfect conditions")
        
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        
        while self.is_trading and self.wins < 3:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.digits.append(current_digit)
                    self.prices.append(price)
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Analyze for ultra-conservative trade
                    prediction = self.analyze_pattern()
                    
                    if prediction and prediction['should_trade']:
                        self.trades_made += 1
                        print(f"🚀 PERFECT CONDITIONS DETECTED!")
                        print(f"   Digit {prediction['digit']} appeared {prediction['frequency']}/20 times")
                        print(f"   Confidence: {prediction['confidence']:.1f}%")
                        
                        await self.place_conservative_trade(prediction)
                        await asyncio.sleep(3)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                            
                            if self.wins >= 3:
                                print("🎉 3 WINS - CONSERVATIVE SUCCESS!")
                                self.is_trading = False
                        else:
                            print(f"💔 LOSS: ${profit:.2f} | Total: ${total_profit:.2f}")
                            print("🛡️ STOPPING - Ultra-conservative approach")
                            self.is_trading = False
                    
            except asyncio.TimeoutError:
                print("⏰ Waiting for perfect conditions...")
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 ULTRA CONSERVATIVE COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Result: ${final_profit:.2f}")

async def main():
    print("🛡️ ULTRA CONSERVATIVE TRADING SYSTEM")
    print("=" * 40)
    print("🎯 Strategy: Only trade on 95%+ confidence")
    print("🔍 Requirement: Digit appears 7+ times in 20 ticks")
    print("💰 Stake: Minimum $0.35 only")
    print("🎯 Target: 3 wins")
    print("🛡️ Stop: Any loss")
    print("=" * 40)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = UltraConservative(api_token)
    
    if await trader.connect():
        await trader.run_conservative_system()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())