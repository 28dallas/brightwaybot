#!/usr/bin/env python3
"""
Integrated Safety System - Coordinates all loss prevention components
"""

import time
import threading
from datetime import datetime
from loss_prevention_system import LossPreventionSystem
from circuit_breaker import CircuitBreaker
from health_monitor import HealthMonitor
from backup_system import BackupSystem
import logging

class IntegratedSafetySystem:
    def __init__(self):
        self.loss_prevention = LossPreventionSystem()
        self.circuit_breaker = CircuitBreaker()
        self.health_monitor = HealthMonitor()
        self.backup_system = BackupSystem()
        
        self.setup_logging()
        self.running = False
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('safety_system.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
    def start_all_systems(self):
        """Start all safety systems"""
        self.logger.info("Starting Integrated Safety System...")
        self.running = True
        
        # Start monitoring threads
        threading.Thread(target=self.monitor_health, daemon=True).start()
        threading.Thread(target=self.monitor_circuit_breaker, daemon=True).start()
        threading.Thread(target=self.run_backups, daemon=True).start()
        
        self.logger.info("All safety systems started")
        
    def monitor_health(self):
        """Monitor system health continuously"""
        while self.running:
            try:
                health = self.health_monitor.get_system_health()
                
                if health['status'] == 'CRITICAL':
                    self.logger.critical("System health critical - triggering emergency stop")
                    self.emergency_stop()
                    
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                self.logger.error(f"Health monitoring error: {e}")
                time.sleep(60)
                
    def monitor_circuit_breaker(self):
        """Monitor circuit breaker status"""
        while self.running:
            try:
                if self.circuit_breaker.is_open():
                    self.logger.warning("Circuit breaker is OPEN - trading halted")
                    
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Circuit breaker monitoring error: {e}")
                time.sleep(30)
                
    def run_backups(self):
        """Run periodic backups"""
        while self.running:
            try:
                # Run backup every hour
                self.backup_system.run_full_backup()
                time.sleep(3600)  # 1 hour
                
            except Exception as e:
                self.logger.error(f"Backup error: {e}")
                time.sleep(1800)  # Retry in 30 minutes
                
    def check_trade_safety(self, trade_amount: float, symbol: str) -> bool:
        """Check if trade is safe to execute"""
        try:
            # Check circuit breaker
            if self.circuit_breaker.is_open():
                self.logger.warning("Trade blocked - circuit breaker open")
                return False
                
            # Check loss prevention
            if not self.loss_prevention.can_trade(trade_amount):
                self.logger.warning("Trade blocked - loss prevention triggered")
                return False
                
            # Check system health
            health = self.health_monitor.get_system_health()
            if health['status'] == 'CRITICAL':
                self.logger.warning("Trade blocked - system health critical")
                return False
                
            return True
            
        except Exception as e:
            self.logger.error(f"Safety check error: {e}")
            return False
            
    def record_trade_result(self, profit_loss: float, success: bool):
        """Record trade result in all systems"""
        try:
            # Update loss prevention
            self.loss_prevention.update_balance(profit_loss)
            
            # Update circuit breaker
            if not success:
                self.circuit_breaker.record_failure()
            else:
                self.circuit_breaker.record_success()
                
        except Exception as e:
            self.logger.error(f"Error recording trade result: {e}")
            
    def emergency_stop(self):
        """Emergency stop all trading activities"""
        self.logger.critical("EMERGENCY STOP ACTIVATED")
        
        try:
            # Trigger circuit breaker
            self.circuit_breaker.force_open()
            
            # Create emergency backup
            self.backup_system.create_emergency_backup()
            
            # Log emergency
            self.loss_prevention.log_emergency("System emergency stop activated")
            
        except Exception as e:
            self.logger.error(f"Emergency stop error: {e}")
            
    def get_system_status(self) -> dict:
        """Get comprehensive system status"""
        try:
            return {
                'timestamp': datetime.now().isoformat(),
                'health': self.health_monitor.get_system_health(),
                'circuit_breaker': {
                    'status': 'OPEN' if self.circuit_breaker.is_open() else 'CLOSED',
                    'failure_count': self.circuit_breaker.failure_count
                },
                'loss_prevention': {
                    'current_balance': self.loss_prevention.current_balance,
                    'daily_loss': self.loss_prevention.get_daily_loss(),
                    'can_trade': self.loss_prevention.can_trade(1.0)
                },
                'running': self.running
            }
            
        except Exception as e:
            self.logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}
            
    def stop_all_systems(self):
        """Stop all safety systems"""
        self.logger.info("Stopping Integrated Safety System...")
        self.running = False

if __name__ == "__main__":
    safety_system = IntegratedSafetySystem()
    
    try:
        safety_system.start_all_systems()
        
        # Keep running and show status
        while True:
            status = safety_system.get_system_status()
            print(f"\nSystem Status: {status['health']['status']}")
            print(f"Circuit Breaker: {status['circuit_breaker']['status']}")
            print(f"Can Trade: {status['loss_prevention']['can_trade']}")
            
            time.sleep(60)
            
    except KeyboardInterrupt:
        safety_system.stop_all_systems()
        print("\nSafety system stopped")