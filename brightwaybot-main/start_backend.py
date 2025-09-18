#!/usr/bin/env python3
import os
import sys
sys.path.append('./backend')

# Set environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Import and run the app
if __name__ == "__main__":
    import uvicorn
    sys.path.insert(0, './backend')
    from main import app
    
    print("Starting Volatility 100 Trading Backend...")
    print("Backend will be available at: http://localhost:8002")
    print("API docs at: http://localhost:8002/docs")
    
    uvicorn.run(app, host="127.0.0.1", port=8002, log_level="info")