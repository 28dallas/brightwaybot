#!/usr/bin/env python3
"""PROFIT TRACKER - Waits for trade results"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque

class ProfitTracker:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        self.active_contracts = {}
        
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
                
            print("💰 PROFIT TRACKER CONNECTED")
            
            # Get balance and subscribe to updates
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
    
    async def place_tracked_trade(self, digit):
        """Place trade and track contract"""
        stake = 1.00  # CHANGE THIS VALUE - minimum 0.35
        
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
            response = await self.ws.recv()
            result = json.loads(response)
            
            if "buy" in result:
                contract_id = result['buy']['contract_id']
                self.active_contracts[contract_id] = {
                    'digit': digit,
                    'stake': stake,
                    'time': asyncio.get_event_loop().time()
                }
                print(f"✅ TRADE PLACED: Contract {contract_id} on digit {digit}")
                return result
            else:
                print(f"❌ Trade failed: {result}")
                return result
                
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_profit_tracking(self):
        """Track profits with balance monitoring"""
        print("💰 STARTING PROFIT TRACKING")
        print("⏰ Will wait for trade results...")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        tick_count = 0
        last_balance_check = asyncio.get_event_loop().time()
        
        while self.is_trading and self.trades_made < 3:
            try:
                message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    tick_count += 1
                    
                    print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                    
                    # Trade every 8th tick (more time between trades)
                    if tick_count >= 8 and tick_count % 8 == 0:
                        # Use a simple strategy: bet on digit 5 (most common)
                        target_digit = 5
                        self.trades_made += 1
                        
                        print(f"🎯 PROFIT TRADE #{self.trades_made}: $0.50 on digit {target_digit}")
                        
                        await self.place_tracked_trade(target_digit)
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    total_profit = new_balance - self.starting_balance
                    
                    if profit != 0:  # Only show when balance actually changes
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"🎉 PROFIT! +${profit:.2f} | Total: +${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        else:
                            print(f"💔 Loss: ${profit:.2f} | Total: ${total_profit:.2f} | Balance: ${self.balance:.2f}")
                        
                        # Stop conditions
                        if self.wins >= 2:
                            print("🎉 2 WINS ACHIEVED - STOPPING!")
                            self.is_trading = False
                        elif total_profit <= -2.0:
                            print("⚠️ $2 LOSS LIMIT - STOPPING")
                            self.is_trading = False
                
                # Check for contract updates
                elif "proposal_open_contract" in data:
                    contract = data["proposal_open_contract"]
                    contract_id = contract.get("contract_id")
                    
                    if contract_id in self.active_contracts:
                        status = contract.get("status")
                        if status in ["won", "lost"]:
                            profit = float(contract.get("profit", 0))
                            print(f"📋 Contract {contract_id}: {status.upper()} | Profit: ${profit:.2f}")
                
                # Periodic balance check
                current_time = asyncio.get_event_loop().time()
                if current_time - last_balance_check > 10:  # Every 10 seconds
                    await self.ws.send(json.dumps({"balance": 1}))
                    last_balance_check = current_time
                    
            except asyncio.TimeoutError:
                print("⏰ Timeout - checking balance...")
                await self.ws.send(json.dumps({"balance": 1}))
            except Exception as e:
                print(f"❌ Error: {e}")
                break
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 PROFIT TRACKING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Result: ${final_profit:.2f}")
        
        if final_profit > 0:
            print("🎉 MISSION ACCOMPLISHED! 💰")

async def main():
    print("💰 PROFIT TRACKER - BALANCE MONITOR")
    print("=" * 40)
    print("⏰ Waits for trade results")
    print("📊 Tracks balance changes")
    print("🎯 Target: 2 wins")
    print("=" * 40)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = ProfitTracker(api_token)
    
    if await trader.connect():
        await trader.run_profit_tracking()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())