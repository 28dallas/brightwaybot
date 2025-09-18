#!/usr/bin/env python3
"""
Simple startup script for the Brightway Trading Bot
"""
import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def main():
    print("🚀 Starting Brightway Trading Bot...")
    
    # Change to the correct directory
    script_dir = Path(__file__).parent
    backend_dir = script_dir / "backend"
    
    if not backend_dir.exists():
        print("❌ Backend directory not found!")
        return
    
    # Start the backend server
    print("📡 Starting backend server...")
    try:
        os.chdir(backend_dir)
        
        # Start the FastAPI server
        subprocess.Popen([
            sys.executable, "-m", "uvicorn", 
            "main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000",
            "--reload"
        ])
        
        print("✅ Backend server starting on http://localhost:8000")
        
        # Wait a moment for server to start
        time.sleep(3)
        
        # Open the frontend
        frontend_path = script_dir / "simple_frontend.html"
        if frontend_path.exists():
            print("🌐 Opening frontend dashboard...")
            webbrowser.open(f"file://{frontend_path.absolute()}")
        
        print("\n" + "="*50)
        print("🎯 BRIGHTWAY TRADING BOT STARTED!")
        print("="*50)
        print("📊 Frontend: Open simple_frontend.html in your browser")
        print("🔧 Backend API: http://localhost:8000")
        print("📚 API Docs: http://localhost:8000/docs")
        print("="*50)
        print("\n💡 Quick Start:")
        print("1. Click 'Run Demo' to test with simulated data")
        print("2. Add your Deriv API token to .env file")
        print("3. Click 'Start Trading' for live trading")
        print("\n⚠️  Press Ctrl+C to stop the server")
        
        # Keep the script running
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n🛑 Shutting down...")
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        print("💡 Make sure you have installed the requirements:")
        print("   pip install -r requirements.txt")

if __name__ == "__main__":
    main()