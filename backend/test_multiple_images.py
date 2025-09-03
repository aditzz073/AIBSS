#!/usr/bin/env python3
"""
Test multiple images to verify the fix works consistently.
"""

import sys
import os
sys.path.append('/Users/aditya/Documents/AIBSS/backend')

from utils.inference import DogAggressionDetector
import cv2

def test_multiple_images():
    """Test with multiple non-aggressive and aggressive images"""
    print("🧪 Testing Multiple Images")
    print("=" * 50)
    
    # Initialize detector
    model_path = "/Users/aditya/Documents/AIBSS/backend/models/best.pt"
    detector = DogAggressionDetector(model_path)
    
    # Test directories
    test_dirs = {
        "Non-Aggressive": "/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS/non_aggressive/",
        "Aggressive": "/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS/aggressive/"
    }
    
    for label, directory in test_dirs.items():
        print(f"\n🔍 Testing {label} Images:")
        print("-" * 30)
        
        if not os.path.exists(directory):
            print(f"   Directory not found: {directory}")
            continue
        
        images = [f for f in os.listdir(directory) if f.lower().endswith(('.jpg', '.jpeg', '.png'))][:5]  # Test first 5 images
        
        correct_predictions = 0
        
        for img_file in images:
            img_path = os.path.join(directory, img_file)
            frame = cv2.imread(img_path)
            
            if frame is None:
                continue
                
            result = detector.analyze_frame(frame)
            predicted = result['prediction']
            confidence = result['confidence']
            
            # Check if prediction matches expected label
            is_correct = (label == "Non-Aggressive" and predicted == "Non-Aggressive") or \
                        (label == "Aggressive" and predicted == "Aggressive")
            
            status = "✅" if is_correct else "❌"
            correct_predictions += is_correct
            
            print(f"   {status} {img_file[:30]:<30} → {predicted} ({confidence:.3f})")
        
        accuracy = correct_predictions / len(images) if images else 0
        print(f"   Accuracy: {correct_predictions}/{len(images)} ({accuracy*100:.1f}%)")

if __name__ == "__main__":
    test_multiple_images()
