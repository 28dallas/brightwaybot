#!/usr/bin/env python3
"""AUTOMATED BACKUP SYSTEM"""

import os
import shutil
import sqlite3
import json
from datetime import datetime
import zipfile

class BackupSystem:
    def __init__(self):
        self.backup_dir = "backups"
        self.ensure_backup_dir()
    
    def ensure_backup_dir(self):
        """Create backup directory if it doesn't exist"""
        if not os.path.exists(self.backup_dir):
            os.makedirs(self.backup_dir)
            print(f"✅ Created backup directory: {self.backup_dir}")
    
    def backup_databases(self):
        """Backup all database files"""
        db_files = [
            "volatility_data.db",
            "backend/volatility_data.db",
            "loss_prevention.db"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for db_file in db_files:
            if os.path.exists(db_file):
                backup_name = f"{self.backup_dir}/db_backup_{os.path.basename(db_file)}_{timestamp}"
                shutil.copy2(db_file, backup_name)
                print(f"✅ Backed up: {db_file} -> {backup_name}")
    
    def backup_config_files(self):
        """Backup configuration files"""
        config_files = [
            ".env",
            "requirements.txt",
            "requirements_simple.txt"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        for config_file in config_files:
            if os.path.exists(config_file):
                backup_name = f"{self.backup_dir}/config_{os.path.basename(config_file)}_{timestamp}"
                shutil.copy2(config_file, backup_name)
                print(f"✅ Backed up: {config_file} -> {backup_name}")
    
    def backup_trading_scripts(self):
        """Backup all trading scripts"""
        trading_files = [
            "emergency_profit_system.py",
            "profit_tracker.py",
            "robust_trader.py",
            "loss_prevention_system.py",
            "smart_profit.py",
            "simple_profit.py"
        ]
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_zip = f"{self.backup_dir}/trading_scripts_{timestamp}.zip"
        
        with zipfile.ZipFile(backup_zip, 'w') as zipf:
            for script in trading_files:
                if os.path.exists(script):
                    zipf.write(script)
                    print(f"✅ Added to backup: {script}")
        
        print(f"✅ Trading scripts backed up to: {backup_zip}")
    
    def create_full_backup(self):
        """Create complete system backup"""
        print("🔄 STARTING FULL BACKUP...")
        
        self.backup_databases()
        self.backup_config_files()
        self.backup_trading_scripts()
        
        # Create backup manifest
        manifest = {
            "timestamp": datetime.now().isoformat(),
            "backup_type": "full_system",
            "files_backed_up": os.listdir(self.backup_dir)
        }
        
        manifest_file = f"{self.backup_dir}/backup_manifest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(manifest_file, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"✅ FULL BACKUP COMPLETE")
        print(f"📁 Backup location: {os.path.abspath(self.backup_dir)}")

if __name__ == "__main__":
    backup_system = BackupSystem()
    backup_system.create_full_backup()