#!/usr/bin/env python3
"""ROBUST TRADER - Handles connection issues and trades fast"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
from collections import deque

class RobustTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.balance = 0
        self.is_trading = True
        self.trades_made = 0
        self.wins = 0
        
    async def connect_with_retry(self):
        """Connect with retry logic"""
        for attempt in range(3):
            try:
                print(f"🔌 Connection attempt {attempt + 1}...")
                self.ws = await websockets.connect(
                    "wss://ws.derivws.com/websockets/v3?app_id=1089",
                    ping_interval=20,
                    ping_timeout=10
                )
                
                # Authorize
                auth_msg = {"authorize": self.api_token}
                await self.ws.send(json.dumps(auth_msg))
                response = await asyncio.wait_for(self.ws.recv(), timeout=10)
                auth_data = json.loads(response)
                
                if "error" in auth_data:
                    print(f"❌ Authorization failed: {auth_data['error']}")
                    return False
                    
                print("✅ ROBUST TRADER CONNECTED")
                
                # Get balance
                await self.ws.send(json.dumps({"balance": 1}))
                balance_response = await asyncio.wait_for(self.ws.recv(), timeout=10)
                balance_data = json.loads(balance_response)
                self.balance = balance_data.get('balance', {}).get('balance', 0)
                self.starting_balance = self.balance
                print(f"💰 Starting Balance: ${self.balance}")
                
                return True
                
            except Exception as e:
                print(f"❌ Connection attempt {attempt + 1} failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(2)
                    
        return False
    
    async def place_quick_trade(self, digit):
        """Place trade quickly with timeout"""
        stake = 0.50
        
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
            response = await asyncio.wait_for(self.ws.recv(), timeout=5)
            return json.loads(response)
        except asyncio.TimeoutError:
            print("⏰ Trade timeout")
            return {"error": {"message": "Timeout"}}
        except Exception as e:
            print(f"❌ Trade error: {e}")
            return {"error": {"message": str(e)}}
    
    async def run_robust_trading(self):
        """Robust trading with quick execution"""
        print("🚀 STARTING ROBUST TRADING")
        
        try:
            # Subscribe to ticks
            await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
            
            tick_count = 0
            recent_digits = deque(maxlen=5)
            
            while self.is_trading and self.trades_made < 5:
                try:
                    # Get message with timeout
                    message = await asyncio.wait_for(self.ws.recv(), timeout=30)
                    data = json.loads(message)
                    
                    if "tick" in data:
                        tick = data["tick"]
                        price = float(tick["quote"])
                        current_digit = int(str(price).replace(".", "")[-1])
                        
                        recent_digits.append(current_digit)
                        tick_count += 1
                        
                        print(f"📈 Tick {tick_count}: {price:.5f} | Digit: {current_digit}")
                        
                        # Trade on specific digits that appear frequently
                        target_digits = [1, 2, 3, 4, 5, 6, 7, 8, 9]  # All except 0
                        
                        # Trade every 3rd tick on common digits
                        if tick_count >= 3 and tick_count % 3 == 0:
                            # Pick most recent digit as target
                            target_digit = current_digit
                            self.trades_made += 1
                            
                            print(f"🎯 QUICK TRADE #{self.trades_made}: $0.50 on digit {target_digit}")
                            
                            result = await self.place_quick_trade(target_digit)
                            
                            if "buy" in result:
                                print(f"✅ TRADE PLACED: {result['buy']['contract_id']}")
                            elif "error" in result:
                                print(f"❌ Error: {result['error']['message']}")
                    
                    elif "balance" in data:
                        new_balance = data["balance"]["balance"]
                        profit = new_balance - self.balance
                        total_profit = new_balance - self.starting_balance
                        self.balance = new_balance
                        
                        if profit > 0:
                            self.wins += 1
                            print(f"💚 WIN #{self.wins}! +${profit:.2f} | Total: +${total_profit:.2f}")
                        elif profit < 0:
                            print(f"💔 Loss: ${profit:.2f} | Total: ${total_profit:.2f}")
                        
                        # Stop conditions
                        if self.wins >= 2:
                            print("🎉 2 WINS - SUCCESS!")
                            self.is_trading = False
                        elif total_profit <= -1.5:
                            print("⚠️ $1.50 LOSS LIMIT")
                            self.is_trading = False
                
                except asyncio.TimeoutError:
                    print("⏰ Message timeout - reconnecting...")
                    break
                except Exception as e:
                    print(f"❌ Message error: {e}")
                    break
                    
        except Exception as e:
            print(f"❌ Trading error: {e}")
        
        finally:
            if self.ws:
                await self.ws.close()
        
        final_profit = self.balance - self.starting_balance
        print(f"\n📊 ROBUST TRADING COMPLETE")
        print(f"Trades: {self.trades_made} | Wins: {self.wins}")
        print(f"Final Result: ${final_profit:.2f}")

async def main():
    print("🛡️ ROBUST TRADER - CONNECTION SAFE")
    print("=" * 35)
    print("⚡ Quick trades every 3rd tick")
    print("🎯 Target: 2 wins")
    print("🛑 Stop: $1.50 loss")
    print("=" * 35)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = RobustTrader(api_token)
    
    if await trader.connect_with_retry():
        await trader.run_robust_trading()
    else:
        print("❌ Failed to connect after retries")

if __name__ == "__main__":
    asyncio.run(main())