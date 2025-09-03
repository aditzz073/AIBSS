#!/usr/bin/env python3
"""
Test script for the new /detections endpoint
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from fastapi.testclient import TestClient
from app import app
import json

def test_detections_endpoint():
    """Test the new /detections endpoint"""
    
    print("Testing /detections endpoint...")
    
    # Create test client
    client = TestClient(app)
    
    try:
        # Test the detections endpoint
        response = client.get("/detections")
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"Number of detections returned: {len(data)}")
            print("\nSample detections:")
            print(json.dumps(data[:3], indent=2))  # Show first 3 detections
            
            # Validate data structure
            if data:
                first_detection = data[0]
                required_fields = ["lat", "lon", "risk", "label", "timestamp"]
                
                print("\nValidating data structure...")
                for field in required_fields:
                    if field in first_detection:
                        print(f"✅ {field}: {first_detection[field]}")
                    else:
                        print(f"❌ Missing field: {field}")
                
                print("\nEndpoint test successful! ✅")
                return True
            else:
                print("❌ No data returned")
                return False
        else:
            print(f"❌ Request failed with status code: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing endpoint: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_detections_endpoint()
    sys.exit(0 if success else 1)
