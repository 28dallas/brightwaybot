import json
import os
from datetime import datetime
from collections import defaultdict

class PerformanceTracker:
    def __init__(self, log_file="performance_log.json"):
        self.log_file = log_file
        self.session_data = {
            'start_time': datetime.now().isoformat(),
            'trades': [],
            'metrics': defaultdict(float),
            'ai_performance': {},
            'loss_prevention': {}
        }

    def log_trade(self, trade_data):
        """Log individual trade data"""
        self.session_data['trades'].append({
            'timestamp': datetime.now().isoformat(),
            'data': trade_data
        })

    def update_metrics(self, metric_name, value):
        """Update performance metrics"""
        self.session_data['metrics'][metric_name] = value

    def log_ai_performance(self, accuracy, confidence, trades_taken):
        """Log AI performance metrics"""
        self.session_data['ai_performance'] = {
            'accuracy': accuracy,
            'avg_confidence': confidence,
            'trades_taken': trades_taken,
            'timestamp': datetime.now().isoformat()
        }

    def log_loss_prevention(self, total_loss, max_daily_loss, consecutive_losses):
        """Log loss prevention metrics"""
        self.session_data['loss_prevention'] = {
            'total_loss': total_loss,
            'max_daily_loss': max_daily_loss,
            'consecutive_losses': consecutive_losses,
            'timestamp': datetime.now().isoformat()
        }

    def save_session(self):
        """Save current session data to file"""
        try:
            if os.path.exists(self.log_file):
                with open(self.log_file, 'r') as f:
                    history = json.load(f)
            else:
                history = []

            self.session_data['end_time'] = datetime.now().isoformat()
            history.append(self.session_data)

            with open(self.log_file, 'w') as f:
                json.dump(history, f, indent=2)

            print(f"📊 Performance data saved to {self.log_file}")

        except Exception as e:
            print(f"❌ Error saving performance data: {e}")

    def generate_report(self):
        """Generate performance report"""
        if not self.session_data['trades']:
            return "No trades to report"

        total_trades = len(self.session_data['trades'])
        wins = sum(1 for trade in self.session_data['trades'] if trade['data'].get('profit', 0) > 0)
        losses = total_trades - wins
        win_rate = (wins / total_trades) * 100 if total_trades > 0 else 0

        total_profit = sum(trade['data'].get('profit', 0) for trade in self.session_data['trades'])

        report = f"""
📊 PERFORMANCE REPORT
{'='*50}
Total Trades: {total_trades}
Wins: {wins}
Losses: {losses}
Win Rate: {win_rate:.1f}%
Total Profit: ${total_profit:.2f}

AI Performance:
- Accuracy: {self.session_data['ai_performance'].get('accuracy', 0):.1f}%
- Avg Confidence: {self.session_data['ai_performance'].get('avg_confidence', 0):.1f}%
- Trades Taken: {self.session_data['ai_performance'].get('trades_taken', 0)}

Loss Prevention:
- Total Loss: ${self.session_data['loss_prevention'].get('total_loss', 0):.2f}
- Max Daily Loss: ${self.session_data['loss_prevention'].get('max_daily_loss', 0):.2f}
- Consecutive Losses: {self.session_data['loss_prevention'].get('consecutive_losses', 0)}
"""
        return report
