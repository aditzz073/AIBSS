#!/usr/bin/env python3
"""
Start server and test detections endpoint
"""

import subprocess
import time
import requests
import json
import sys
import os
from pathlib import Path

def start_server_and_test():
    backend_dir = Path(__file__).parent
    
    # Start server
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app:app",
        "--host", "127.0.0.1",
        "--port", "8002"
    ]
    
    print("Starting FastAPI server on port 8002...")
    
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for server to start
    time.sleep(5)
    
    try:
        # Test the detections endpoint
        print("Testing /detections endpoint...")
        response = requests.get("http://127.0.0.1:8002/detections", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Success! Status Code: {response.status_code}")
            print(f"✅ Number of detections: {len(data)}")
            print("\nSample detection:")
            print(json.dumps(data[0], indent=2))
        else:
            print(f"❌ Failed! Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"❌ Connection error: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        # Clean up
        process.terminate()
        process.wait()
        print("Server stopped.")

if __name__ == "__main__":
    start_server_and_test()
