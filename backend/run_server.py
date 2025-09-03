#!/usr/bin/env python3
"""
Simple launcher for the Dog Behavior Analysis API
"""
import subprocess
import sys
import time
import requests
import json
from pathlib import Path

def start_server():
    """Start the FastAPI server."""
    backend_dir = Path(__file__).parent
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app:app",
        "--host", "127.0.0.1",
        "--port", "8001"
    ]
    
    print("Starting FastAPI server...")
    print(f"Command: {' '.join(cmd)}")
    print(f"Working directory: {backend_dir}")
    
    # Set PYTHONPATH to current directory
    env = {"PYTHONPATH": str(backend_dir)}
    
    process = subprocess.Popen(
        cmd,
        cwd=backend_dir,
        env={**subprocess.os.environ, **env},
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Wait for server to start
    print("Waiting for server to initialize...")
    time.sleep(10)
    
    # Test the server
    try:
        response = requests.get("http://127.0.0.1:8001/health", timeout=5)
        print(f"Health check: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
        # Test model info
        response = requests.get("http://127.0.0.1:8001/model/info", timeout=5)
        print(f"Model info: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        
    except Exception as e:
        print(f"Error testing server: {e}")
    
    return process

if __name__ == "__main__":
    process = start_server()
    
    print("\n" + "="*50)
    print("Server started successfully!")
    print("API Documentation: http://127.0.0.1:8001/docs")
    print("Health Check: http://127.0.0.1:8001/health")
    print("Press Ctrl+C to stop the server")
    print("="*50)
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping server...")
        process.terminate()
        process.wait()
