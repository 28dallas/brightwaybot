#!/usr/bin/env python3
"""
Health Monitor System - Monitors system health and triggers alerts
"""

import time
import psutil
import sqlite3
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

class HealthMonitor:
    def __init__(self, db_path: str = "health_monitor.db"):
        self.db_path = db_path
        self.setup_database()
        self.setup_logging()
        
    def setup_database(self):
        """Initialize health monitoring database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS health_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                cpu_percent REAL,
                memory_percent REAL,
                disk_usage REAL,
                network_io TEXT,
                active_trades INTEGER,
                system_status TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                alert_type TEXT,
                message TEXT,
                severity TEXT,
                resolved BOOLEAN DEFAULT FALSE
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def setup_logging(self):
        """Setup logging for health monitor"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('health_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def collect_metrics(self) -> Dict:
        """Collect system health metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Network I/O
            net_io = psutil.net_io_counters()
            network_data = {
                'bytes_sent': net_io.bytes_sent,
                'bytes_recv': net_io.bytes_recv
            }
            
            metrics = {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'disk_usage': disk.percent,
                'network_io': json.dumps(network_data),
                'active_trades': self.get_active_trades_count(),
                'system_status': self.determine_system_status(cpu_percent, memory.percent)
            }
            
            return metrics
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics: {e}")
            return {}
            
    def get_active_trades_count(self) -> int:
        """Get count of active trades from trading database"""
        try:
            conn = sqlite3.connect('trading_data.db')
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM trades WHERE status = 'active'")
            count = cursor.fetchone()[0]
            conn.close()
            return count
        except:
            return 0
            
    def determine_system_status(self, cpu: float, memory: float) -> str:
        """Determine overall system status"""
        if cpu > 90 or memory > 90:
            return "CRITICAL"
        elif cpu > 70 or memory > 70:
            return "WARNING"
        else:
            return "HEALTHY"
            
    def store_metrics(self, metrics: Dict):
        """Store metrics in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO health_metrics 
                (cpu_percent, memory_percent, disk_usage, network_io, active_trades, system_status)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                metrics.get('cpu_percent'),
                metrics.get('memory_percent'),
                metrics.get('disk_usage'),
                metrics.get('network_io'),
                metrics.get('active_trades'),
                metrics.get('system_status')
            ))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error storing metrics: {e}")
            
    def check_alerts(self, metrics: Dict):
        """Check for alert conditions"""
        alerts = []
        
        # CPU alert
        if metrics.get('cpu_percent', 0) > 85:
            alerts.append({
                'type': 'HIGH_CPU',
                'message': f"CPU usage at {metrics['cpu_percent']:.1f}%",
                'severity': 'HIGH'
            })
            
        # Memory alert
        if metrics.get('memory_percent', 0) > 85:
            alerts.append({
                'type': 'HIGH_MEMORY',
                'message': f"Memory usage at {metrics['memory_percent']:.1f}%",
                'severity': 'HIGH'
            })
            
        # Disk space alert
        if metrics.get('disk_usage', 0) > 90:
            alerts.append({
                'type': 'LOW_DISK',
                'message': f"Disk usage at {metrics['disk_usage']:.1f}%",
                'severity': 'CRITICAL'
            })
            
        # Store alerts
        for alert in alerts:
            self.store_alert(alert)
            
        return alerts
        
    def store_alert(self, alert: Dict):
        """Store alert in database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (alert_type, message, severity)
                VALUES (?, ?, ?)
            ''', (alert['type'], alert['message'], alert['severity']))
            
            conn.commit()
            conn.close()
            
            self.logger.warning(f"ALERT: {alert['message']}")
            
        except Exception as e:
            self.logger.error(f"Error storing alert: {e}")
            
    def get_system_health(self) -> Dict:
        """Get current system health summary"""
        metrics = self.collect_metrics()
        
        return {
            'status': metrics.get('system_status', 'UNKNOWN'),
            'cpu_percent': metrics.get('cpu_percent', 0),
            'memory_percent': metrics.get('memory_percent', 0),
            'disk_usage': metrics.get('disk_usage', 0),
            'active_trades': metrics.get('active_trades', 0),
            'timestamp': datetime.now().isoformat()
        }
        
    def run_monitoring_cycle(self):
        """Run one monitoring cycle"""
        metrics = self.collect_metrics()
        if metrics:
            self.store_metrics(metrics)
            alerts = self.check_alerts(metrics)
            
            if alerts:
                self.logger.info(f"Generated {len(alerts)} alerts")
                
        return metrics
        
    def start_monitoring(self, interval: int = 60):
        """Start continuous monitoring"""
        self.logger.info("Starting health monitoring...")
        
        try:
            while True:
                self.run_monitoring_cycle()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            self.logger.info("Health monitoring stopped")
        except Exception as e:
            self.logger.error(f"Monitoring error: {e}")

if __name__ == "__main__":
    monitor = HealthMonitor()
    
    # Run single check
    health = monitor.get_system_health()
    print(f"System Status: {health['status']}")
    print(f"CPU: {health['cpu_percent']:.1f}%")
    print(f"Memory: {health['memory_percent']:.1f}%")
    print(f"Disk: {health['disk_usage']:.1f}%")
    print(f"Active Trades: {health['active_trades']}")