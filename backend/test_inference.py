#!/usr/bin/env python3
"""
Test script to verify the inference fix for dog aggression classification.
"""

import sys
import os
sys.path.append('/Users/aditya/Documents/AIBSS/backend')

from utils.inference import DogAggressionDetector
import cv2

def test_inference():
    """Test the inference on a known non-aggressive image"""
    print("🧪 Testing Dog Aggression Inference Fix")
    print("=" * 50)
    
    # Initialize detector
    model_path = "/Users/aditya/Documents/AIBSS/backend/models/best.pt"
    detector = DogAggressionDetector(model_path)
    
    print(f"✅ Detector initialized")
    print(f"YOLO model loaded: {detector.model is not None}")
    print(f"Aggression classifier loaded: {detector.aggression_classifier is not None}")
    print(f"Scaler loaded: {detector.scaler is not None}")
    print()
    
    # Test with a non-aggressive image
    test_image_path = "/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS/non_aggressive/2AoiPsaOr4YiEGxiOAhfMQpZ3K77nc168.jpg"
    
    if not os.path.exists(test_image_path):
        print(f"❌ Test image not found: {test_image_path}")
        # Try to find any non-aggressive image
        non_agg_dir = "/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS/non_aggressive/"
        if os.path.exists(non_agg_dir):
            images = [f for f in os.listdir(non_agg_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                test_image_path = os.path.join(non_agg_dir, images[0])
                print(f"🔄 Using alternative test image: {images[0]}")
            else:
                print("❌ No test images found in non_aggressive directory")
                return
        else:
            print("❌ Non-aggressive directory not found")
            return
    
    print(f"🔍 Analyzing image: {os.path.basename(test_image_path)}")
    
    # Load and analyze image
    frame = cv2.imread(test_image_path)
    if frame is None:
        print("❌ Could not load test image")
        return
    
    result = detector.analyze_frame(frame)
    
    print("\n📊 Analysis Results:")
    print(f"Prediction: {result['prediction']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Dog detected: {result['dog_detected']}")
    print(f"Processing time: {result['processing_time']:.3f}s")
    
    if 'note' in result:
        print(f"Note: {result['note']}")
    
    if 'error' in result:
        print(f"Error: {result['error']}")
    
    # Determine if the fix worked
    if result['prediction'] == "Non-Aggressive":
        print("\n✅ SUCCESS: Non-aggressive dog correctly classified!")
    elif result['prediction'] == "Aggressive":
        print("\n⚠️  ISSUE: Non-aggressive dog still classified as aggressive")
        print("This might be due to:")
        print("- The ML model itself needs retraining")
        print("- Keypoint detection issues")
        print("- Feature extraction problems")
    else:
        print(f"\n❓ UNEXPECTED: Got prediction '{result['prediction']}'")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    test_inference()
