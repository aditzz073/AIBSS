#!/bin/bash

# Dog Behavior Analysis API Test Script

echo "==================================="
echo "Dog Behavior Analysis API Testing"
echo "==================================="

# Start the server in background
echo "Starting FastAPI server..."
cd /Users/aditya/Documents/AIBSS/backend
export PYTHONPATH=.
python -m uvicorn app:app --host 127.0.0.1 --port 8001 &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Waiting for server to initialize..."
sleep 8

# Test endpoints
echo ""
echo "Testing Health Check..."
curl -s -X GET "http://127.0.0.1:8001/health" | python -m json.tool

echo ""
echo "Testing Model Info..."
curl -s -X GET "http://127.0.0.1:8001/model/info" | python -m json.tool

echo ""
echo "Testing Root Endpoint..."
curl -s -X GET "http://127.0.0.1:8001/" | python -m json.tool

echo ""
echo "==================================="
echo "Tests completed!"
echo "API Documentation available at: http://127.0.0.1:8001/docs"
echo "To stop the server, run: kill $SERVER_PID"
echo "==================================="
