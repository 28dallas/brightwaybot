#!/usr/bin/env python3
"""Ultra-High Profit Strategy - Maximum Accuracy System"""

import sys
sys.path.append('./backend')

import asyncio
import websockets
import json
import numpy as np
from collections import deque
from advanced_ai import UltraAdvancedPredictor
from ai_predictor_simple import EnhancedPredictor

class MaxProfitTrader:
    def __init__(self, api_token):
        self.api_token = api_token
        self.ws = None
        self.standard_ai = EnhancedPredictor()
        self.ultra_ai = UltraAdvancedPredictor()
        self.digits = deque(maxlen=200)  # More history
        self.prices = deque(maxlen=200)
        self.balance = 0
        self.trades_won = deque(maxlen=20)
        self.consecutive_wins = 0
        self.is_trading = True
        
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
                
            print("🚀 ULTRA-PROFIT SYSTEM CONNECTED")
            print(f"👤 Account: {auth_data.get('authorize', {}).get('email', 'Demo')}")
            
            # Get balance
            await self.ws.send(json.dumps({"balance": 1, "subscribe": 1}))
            balance_response = await self.ws.recv()
            balance_data = json.loads(balance_response)
            self.balance = balance_data.get('balance', {}).get('balance', 0)
            print(f"💰 Starting Balance: ${self.balance}")
            
            return True
            
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    def get_ultra_prediction(self):
        """Get the highest accuracy prediction possible"""
        if len(self.digits) < 30:
            return None
        
        # Get both AI predictions
        standard_pred = self.standard_ai.get_comprehensive_prediction(
            list(self.digits), list(self.prices), self.balance, 1.0
        )
        
        ultra_pred = self.ultra_ai.ensemble_prediction(
            list(self.digits), list(self.prices)
        )
        
        # Combine for maximum accuracy
        if ultra_pred['confidence'] > standard_pred['final_confidence']:
            final_confidence = self.ultra_ai.adaptive_confidence_adjustment(ultra_pred['confidence'])
            predicted_digit = ultra_pred['predicted_digit']
        else:
            final_confidence = standard_pred['final_confidence']
            predicted_digit = standard_pred['predicted_digit']
        
        # Ultra-conservative: only trade on VERY high confidence
        should_trade = (
            final_confidence >= 80 and  # Increased threshold
            len(self.digits) >= 50 and  # More data required
            (self.consecutive_wins < 3 or final_confidence >= 85)  # Streak management
        )
        
        # Advanced position sizing with minimum stake
        stake = self.ultra_ai.kelly_criterion_advanced(
            final_confidence, self.balance, list(self.trades_won)
        )
        stake = max(stake, 0.35)  # Ensure minimum stake
        
        return {
            'predicted_digit': predicted_digit,
            'confidence': final_confidence,
            'should_trade': should_trade,
            'stake': stake,
            'ultra_features': ultra_pred
        }
    
    async def place_smart_trade(self, prediction):
        """Place trade with maximum profit strategy"""
        digit = prediction['predicted_digit']
        stake = min(prediction['stake'], 3.0)  # Conservative max
        
        # Use DIGITMATCH for high confidence
        contract_type = "DIGITMATCH"
        
        trade_msg = {
            "buy": 1,
            "price": stake,
            "parameters": {
                "amount": stake,
                "basis": "stake",
                "contract_type": contract_type,
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
    
    async def run_ultra_trading(self):
        """Main ultra-profit trading loop"""
        print("🎯 STARTING ULTRA-PROFIT AI TRADING")
        print("📊 Collecting data for maximum accuracy...")
        
        # Subscribe to ticks
        await self.ws.send(json.dumps({"ticks": "R_100", "subscribe": 1}))
        
        trades_made = 0
        
        while self.is_trading:
            try:
                message = await self.ws.recv()
                data = json.loads(message)
                
                if "tick" in data:
                    tick = data["tick"]
                    price = float(tick["quote"])
                    current_digit = int(str(price).replace(".", "")[-1])
                    
                    self.prices.append(price)
                    self.digits.append(current_digit)
                    
                    print(f"📈 {price:.5f} | Digit: {current_digit} | Data: {len(self.digits)}")
                    
                    # Get ultra prediction
                    prediction = self.get_ultra_prediction()
                    
                    if prediction:
                        print(f"🧠 AI: Digit={prediction['predicted_digit']}, "
                              f"Conf={prediction['confidence']:.1f}%, "
                              f"Trade={prediction['should_trade']}")
                        
                        # Only trade on ultra-high confidence
                        if (prediction['should_trade'] and 
                            current_digit == prediction['predicted_digit']):
                            
                            trades_made += 1
                            stake = prediction['stake']
                            
                            print(f"🚀 ULTRA TRADE #{trades_made}: ${stake:.2f} on digit {prediction['predicted_digit']}")
                            print(f"   Confidence: {prediction['confidence']:.1f}%")
                            print(f"   Features: Momentum={prediction['ultra_features'].get('momentum', 0):.2f}")
                            
                            result = await self.place_smart_trade(prediction)
                            
                            if "buy" in result:
                                contract_id = result['buy']['contract_id']
                                print(f"✅ Trade placed: {contract_id}")
                            else:
                                print(f"❌ Trade failed: {result}")
                
                elif "balance" in data:
                    new_balance = data["balance"]["balance"]
                    profit = new_balance - self.balance
                    self.balance = new_balance
                    
                    if profit > 0:
                        self.consecutive_wins += 1
                        self.trades_won.append(1)
                        print(f"💚 PROFIT: +${profit:.2f} | Balance: ${self.balance:.2f} | Streak: {self.consecutive_wins}")
                    elif profit < 0:
                        self.consecutive_wins = 0
                        self.trades_won.append(0)
                        print(f"💔 Loss: ${profit:.2f} | Balance: ${self.balance:.2f}")
                    
            except Exception as e:
                print(f"❌ Error: {e}")
                break

async def main():
    print("🚀 ULTRA-HIGH PROFIT TRADING SYSTEM")
    print("=" * 50)
    print("⚡ Maximum Accuracy AI")
    print("💎 Advanced Pattern Recognition")
    print("🎯 Ultra-Conservative Risk Management")
    print("=" * 50)
    
    import os
    from dotenv import load_dotenv
    load_dotenv()
    
    api_token = os.getenv('DERIV_API_TOKEN')
    if not api_token:
        print("❌ No API token found")
        return
    
    trader = MaxProfitTrader(api_token)
    
    if await trader.connect():
        await trader.run_ultra_trading()
    else:
        print("❌ Failed to connect")

if __name__ == "__main__":
    asyncio.run(main())