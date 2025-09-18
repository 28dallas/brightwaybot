#!/usr/bin/env python3
"""SIMPLE MARTINGALE RECOVERY SYSTEM"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque

class MartingaleRecovery:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.base_stake = 0.35
        self.current_stake = 0.35
        self.consecutive_losses = 0
        self.is_trading = True
        self.target_profit = 2.0  # Stop at $2 profit
        self.max_losses = 4  # Stop after 4 consecutive losses
        
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
                
            print("💎 MARTINGALE RECOVERY SYSTEM")
            
            # Get balance
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
    
    async def place_martingale_trade(self, digit):
        """Place trade with current stake"""
        trade_msg = {
            "buy": 1,
            "price": self.current_stake,
            "parameters": {
                "amount": self.current_stake,
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
    
    def get_simple_prediction(self, recent_digits):
        """Simple: pick digit 5 (most common statistically)"""
        return 5
    
    async def run_martingale(self):
        """Martingale recovery system"""
        print("💎 STARTING MARTINGALE RECOVERY")
        print(f"🎯 Target: +${self.target_profit} profit")
        print(f"⚠️ Max losses: {self.max_losses}")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        recent_digits = deque(maxlen=10)
        waiting_for_trade = False
        
        while self.is_trading:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    recent_digits.append(current_digit)
                    
                    print(f"📈 {price:.5f} | Digit: {current_digit}")
                    
                    # Simple strategy: trade on digit 5
                    if not waiting_for_trade and len(recent_digits) >= 5:
                        target_digit = 5
                        
                        if current_digit == target_digit:
                            waiting_for_trade = True
                            
                            print(f"🎯 MARTINGALE TRADE: ${self.current_stake:.2f} on digit {target_digit}")
                            print(f"   Consecutive losses: {self.consecutive_losses}")
                            
                            result = await self.place_martingale_trade(target_digit)
                            
                            if "buy" in result:
                                print(f"✅ Trade placed: {result['buy']['contract_id']}")
                            else:
                                print(f"❌ Trade failed: {result}")
                                waiting_for_trade = False
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    self.balance = new_balance
                    waiting_for_trade = False
                    
                    if profit > 0:
                        # WIN - Reset stake
                        self.consecutive_losses = 0
                        self.current_stake = self.base_stake
                        print(f"💚 WIN! +${profit:.2f} | Total: +${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        
                        # Check if target reached
                        if total_profit >= self.target_profit:
                            print(f"🎉 TARGET REACHED! +${total_profit:.2f} - STOPPING")
                            self.is_trading = False
                            
                    elif profit < 0:
                        # LOSS - Double stake (Martingale)
                        self.consecutive_losses += 1
                        print(f"💔 Loss: ${profit:.2f} | Total: ${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        
                        if self.consecutive_losses >= self.max_losses:
                            print(f"⚠️ MAX LOSSES REACHED - STOPPING")
                            self.is_trading = False
                        else:
                            # Double the stake
                            self.current_stake = min(self.current_stake * 2, 5.0)  # Cap at $5
                            print(f"📈 Next stake: ${self.current_stake:.2f}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 MARTINGALE SESSION COMPLETE")
        print(f"Final Profit/Loss: ${final_profit:.2f}")
        print(f"Final Balance: ${self.balance:.2f}")

async def main():
    print("💎 MARTINGALE RECOVERY SYSTEM")
    print("=" * 35)
    print("🎯 Target: $2 profit")
    print("⚠️ Max 4 consecutive losses")
    print("📈 Doubles stake after loss")
    print("=" * 35)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = MartingaleRecovery(api_token)
    
    if await trader.connect():
        await trader.run_martingale()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())