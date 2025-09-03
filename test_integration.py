#!/usr/bin/env python3
"""
Quick integration test to verify frontend-backend communication works.
This script tests the API calls that the frontend will make.
"""

import requests
import json
import time

def test_frontend_backend_integration():
    """Test the key endpoints that the frontend uses."""
    print("🔗 Testing Frontend-Backend Integration")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test 1: Health check
    print("\n1️⃣ Testing Health Check...")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Backend health check: OK")
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")
        return False
    
    # Test 2: Model info
    print("\n2️⃣ Testing Model Info...")
    try:
        response = requests.get(f"{base_url}/model/info", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Model info retrieved successfully")
            print(f"   Image Model: {data.get('image_analysis', {}).get('status', 'unknown')}")
            print(f"   Video Model: {data.get('video_analysis', {}).get('status', 'unknown')}")
            print(f"   System: {data.get('system_status', 'unknown')}")
        else:
            print(f"❌ Model info failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Model info error: {e}")
        return False
    
    # Test 3: Check if frontend is accessible
    print("\n3️⃣ Testing Frontend Accessibility...")
    try:
        response = requests.get("http://localhost:3000", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend accessible at http://localhost:3000")
        else:
            print(f"❌ Frontend not accessible: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Frontend not reachable: {e}")
        print("   Make sure 'npm run dev' is running")
        return False
    
    # Test 4: CORS check (simulate frontend request)
    print("\n4️⃣ Testing CORS Configuration...")
    try:
        headers = {
            'Origin': 'http://localhost:3000',
            'Access-Control-Request-Method': 'POST',
            'Access-Control-Request-Headers': 'Content-Type'
        }
        response = requests.options(f"{base_url}/analyze_image", headers=headers, timeout=5)
        if response.status_code in [200, 204]:
            print("✅ CORS configured correctly")
        else:
            print(f"⚠️ CORS might need adjustment: {response.status_code}")
    except Exception as e:
        print(f"⚠️ CORS check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Frontend-Backend Integration Ready!")
    print("\n📋 Next Steps:")
    print("1. Open http://localhost:3000 in your browser")
    print("2. Test image upload functionality")
    print("3. Test live feed functionality")
    print("4. Test video upload functionality")
    print("\n💡 Your backend API is available at:")
    print("   - Image Analysis: POST http://localhost:8000/analyze_image")
    print("   - Live Feed: POST http://localhost:8000/analyze_live")
    print("   - Video Analysis: POST http://localhost:8000/analyze_video")
    print("   - Model Info: GET http://localhost:8000/model/info")
    
    return True

if __name__ == "__main__":
    success = test_frontend_backend_integration()
    if success:
        print("\n✅ Integration test completed successfully!")
    else:
        print("\n❌ Integration test failed. Check the issues above.")
