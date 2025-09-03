#!/usr/bin/env python3
"""
Test script for Dog Behavior Analysis API
"""
import requests
import json
import os
from pathlib import Path

# API base URL
BASE_URL = "http://127.0.0.1:8001"

def test_health_check():
    """Test the health check endpoint."""
    print("Testing health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_model_info():
    """Test the model info endpoint."""
    print("\nTesting model info...")
    try:
        response = requests.get(f"{BASE_URL}/model/info")
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def test_image_analysis(image_path):
    """Test image analysis endpoint."""
    print(f"\nTesting image analysis with {image_path}...")
    try:
        if not os.path.exists(image_path):
            print(f"Image file not found: {image_path}")
            return False
            
        with open(image_path, "rb") as f:
            files = {"file": f}
            response = requests.post(f"{BASE_URL}/analyze_image", files=files)
            
        print(f"Status: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    """Run all tests."""
    print("=" * 50)
    print("Dog Behavior Analysis API Test Suite")
    print("=" * 50)
    
    # Test basic endpoints
    health_ok = test_health_check()
    model_ok = test_model_info()
    
    # Look for test images in the dataset
    dataset_path = Path("../dog-behavior-dashboard/dataset/IMAGESSS")
    test_image = None
    
    # Try to find an aggressive image for testing
    aggressive_path = dataset_path / "aggressive"
    if aggressive_path.exists():
        for img_file in aggressive_path.glob("*.jpg"):
            test_image = str(img_file)
            break
    
    # If no aggressive image, try non-aggressive
    if not test_image:
        non_aggressive_path = dataset_path / "non_aggressive"
        if non_aggressive_path.exists():
            for img_file in non_aggressive_path.glob("*.jpg"):
                test_image = str(img_file)
                break
    
    image_ok = False
    if test_image:
        image_ok = test_image_analysis(test_image)
    else:
        print("\nNo test images found in dataset directory")
    
    # Summary
    print("\n" + "=" * 50)
    print("Test Results:")
    print(f"Health Check: {'✓' if health_ok else '✗'}")
    print(f"Model Info: {'✓' if model_ok else '✗'}")
    print(f"Image Analysis: {'✓' if image_ok else '✗'}")
    print("=" * 50)
    
    if all([health_ok, model_ok]):
        print("✓ Basic API functionality is working!")
        if image_ok:
            print("✓ Image analysis is working!")
        else:
            print("⚠ Image analysis could not be tested (no test images)")
    else:
        print("✗ Some tests failed. Check if the server is running.")

if __name__ == "__main__":
    main()
