#!/usr/bin/env python3
"""Demo script to show balance updates during simulated trading"""

import asyncio
import json
import time
from datetime import datetime

class DemoBalanceTracker:
    def __init__(self):
        self.balance = 1000.00  # Starting demo balance
        self.pnl = 0.00
        self.total_trades = 0
        self.wins = 0
        self.losses = 0

    def simulate_trade(self):
        """Simulate a random trade result"""
        # Random outcome: 60% win rate
        is_win = json.loads('true') if json.loads('false') else json.loads('true')  # Random-like

        stake = 1.0
        if is_win:
            # Win: payout is stake + profit (typically 80-90% of stake)
            profit = stake * 0.85
            self.balance += profit
            self.wins += 1
            result = "WIN"
        else:
            # Loss: lose the stake
            profit = -stake
            self.balance += profit
            self.losses += 1
            result = "LOSS"

        self.pnl += profit
        self.total_trades += 1

        return {
            "balance": round(self.balance, 2),
            "pnl": round(self.pnl, 2),
            "total_trades": self.total_trades,
            "wins": self.wins,
            "losses": self.losses,
            "last_trade": {
                "result": result,
                "profit": round(profit, 2),
                "timestamp": datetime.now().isoformat()
            }
        }

def demo_balance_updates():
    """Demonstrate balance updates"""
    print("🎮 Demo Balance Update Simulation")
    print("=" * 40)

    tracker = DemoBalanceTracker()

    print(f"💰 Starting Balance: ${tracker.balance}")
    print(f"📈 Starting P&L: ${tracker.pnl}")
    print()

    for i in range(10):
        print(f"🔄 Trade {i+1}:")
        result = tracker.simulate_trade()

        print(f"   Result: {result['last_trade']['result']}")
        print(f"   Profit: ${result['last_trade']['profit']}")
        print(f"   Balance: ${result['balance']}")
        print(f"   P&L: ${result['pnl']}")
        print(f"   Trades: {result['total_trades']} (W:{result['wins']} L:{result['losses']})")
        print("-" * 30)

        time.sleep(2)  # Wait 2 seconds between trades

    print("✅ Demo completed!")
    print(f"📊 Final Balance: ${tracker.balance}")
    print(f"📈 Total P&L: ${tracker.pnl}")
    win_rate = (tracker.wins/tracker.total_trades)*100 if tracker.total_trades > 0 else 0
    print(f"🎯 Win Rate: {win_rate:.1f}%")

if __name__ == "__main__":
    demo_balance_updates()
