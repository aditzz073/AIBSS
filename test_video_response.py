#!/usr/bin/env python3
"""
Test script to understand the video analysis API response format.
"""

import requests
import json

def test_video_api():
    """Test the video analysis endpoint with a sample image (since we don't have video files)."""
    
    # Test with health endpoint first
    health_response = requests.get("http://127.0.0.1:8000/health")
    print("Health check:", health_response.json())
    
    # Test model info
    model_response = requests.get("http://127.0.0.1:8000/model/info")
    print("Model info:", json.dumps(model_response.json(), indent=2))
    
    # Test with an image file (since we don't have video files available)
    try:
        with open("/Users/aditya/Documents/AIBSS/backend/live_view/kutte.jpeg", "rb") as f:
            # Test image analysis to see format
            image_response = requests.post(
                "http://127.0.0.1:8000/analyze_image",
                files={"file": ("test.jpg", f, "image/jpeg")}
            )
            print("\nImage Analysis Response:")
            print(json.dumps(image_response.json(), indent=2, default=str))
            
    except FileNotFoundError:
        print("Sample image file not found")
    
    # Create a simple test video using OpenCV (if available)
    try:
        import cv2
        import numpy as np
        import tempfile
        import os
        
        # Create a simple test video
        with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp_file:
            temp_video_path = tmp_file.name
            
        # Create a simple video with a few frames
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        out = cv2.VideoWriter(temp_video_path, fourcc, 1.0, (640, 480))
        
        for i in range(5):  # 5 frames
            frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
            out.write(frame)
        
        out.release()
        
        # Test video analysis
        with open(temp_video_path, "rb") as f:
            video_response = requests.post(
                "http://127.0.0.1:8000/analyze_video",
                files={"file": ("test.mp4", f, "video/mp4")}
            )
            print("\nVideo Analysis Response:")
            print(json.dumps(video_response.json(), indent=2, default=str))
        
        # Clean up
        os.unlink(temp_video_path)
        
    except ImportError:
        print("OpenCV not available for video generation")
    except Exception as e:
        print(f"Error creating test video: {e}")

if __name__ == "__main__":
    test_video_api()
