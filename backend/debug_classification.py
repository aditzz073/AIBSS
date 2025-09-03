#!/usr/bin/env python3
"""
Debug script to understand why the aggression model is misclassifying.
"""

import sys
import os
sys.path.append('/Users/aditya/Documents/AIBSS/backend')

from utils.inference import DogAggressionDetector
import cv2
import numpy as np

def debug_classification():
    """Debug the classification process step by step"""
    print("🔍 Debugging Dog Aggression Classification")
    print("=" * 60)
    
    # Initialize detector
    model_path = "/Users/aditya/Documents/AIBSS/backend/models/best.pt"
    detector = DogAggressionDetector(model_path)
    
    # Test with a non-aggressive image
    test_image_path = "/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS/non_aggressive/2AoiPsaOr4YiEGxiOAhfMQpZ3K77nc168.jpg"
    
    if not os.path.exists(test_image_path):
        # Try to find any non-aggressive image
        non_agg_dir = "/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS/non_aggressive/"
        if os.path.exists(non_agg_dir):
            images = [f for f in os.listdir(non_agg_dir) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
            if images:
                test_image_path = os.path.join(non_agg_dir, images[0])
    
    print(f"📸 Testing with: {os.path.basename(test_image_path)}")
    
    # Load image
    frame = cv2.imread(test_image_path)
    if frame is None:
        print("❌ Could not load test image")
        return
    
    # Step 1: YOLO detection
    print("\n1️⃣  YOLO Detection:")
    results = detector.model(frame, verbose=False)
    if results and len(results) > 0 and results[0].boxes is not None:
        boxes = results[0].boxes
        print(f"   Dogs detected: {len(boxes.conf)}")
        print(f"   Detection confidences: {boxes.conf.cpu().numpy()}")
        print(f"   Classes detected: {boxes.cls.cpu().numpy()}")
    else:
        print("   No dogs detected by YOLO")
        return
    
    # Step 2: Keypoint extraction
    print("\n2️⃣  Keypoint Extraction:")
    keypoints = detector.detect_keypoints(frame)
    if keypoints is not None:
        print(f"   Keypoints shape: {keypoints.shape}")
        avg_conf = np.mean(keypoints[:, 2])
        high_conf_count = np.sum(keypoints[:, 2] > 0.3)
        print(f"   Average keypoint confidence: {avg_conf:.3f}")
        print(f"   High confidence keypoints (>0.3): {high_conf_count}/24")
        
        # Show some key keypoint confidences
        key_points = {
            'nose': keypoints[0, 2],
            'left_eye': keypoints[1, 2], 
            'right_eye': keypoints[2, 2],
            'left_ear': keypoints[3, 2],
            'right_ear': keypoints[4, 2],
            'tail_base': keypoints[21, 2] if len(keypoints) > 21 else 0,
            'tail_tip': keypoints[23, 2] if len(keypoints) > 23 else 0
        }
        print("   Key keypoint confidences:")
        for name, conf in key_points.items():
            print(f"     {name}: {conf:.3f}")
    else:
        print("   No keypoints detected")
        return
    
    # Step 3: Feature extraction
    print("\n3️⃣  Feature Extraction:")
    features = detector.extract_behavioral_features(keypoints)
    print(f"   Features shape: {features.shape}")
    print(f"   Non-zero features: {np.count_nonzero(features)}/35")
    print(f"   Feature range: [{np.min(features):.3f}, {np.max(features):.3f}]")
    print(f"   Feature mean: {np.mean(features):.3f}")
    
    # Step 4: Model prediction details
    print("\n4️⃣  Classification Process:")
    if detector.aggression_classifier is not None:
        # Preprocess features
        features_reshaped = features.reshape(1, -1)
        features_imputed = detector.imputer.transform(features_reshaped)
        features_scaled = detector.scaler.transform(features_imputed)
        features_selected = detector.feature_selector.transform(features_scaled)
        
        print(f"   After preprocessing: {features_selected.shape}")
        print(f"   Preprocessed range: [{np.min(features_selected):.3f}, {np.max(features_selected):.3f}]")
        
        # Get prediction probabilities
        probabilities = detector.aggression_classifier.predict_proba(features_selected)[0]
        prediction = detector.aggression_classifier.predict(features_selected)[0]
        
        print(f"   Class probabilities:")
        print(f"     Non-Aggressive (0): {probabilities[0]:.3f}")
        print(f"     Aggressive (1): {probabilities[1]:.3f}")
        print(f"   Prediction: {prediction} ({'Aggressive' if prediction == 1 else 'Non-Aggressive'})")
        print(f"   Confidence: {max(probabilities):.3f}")
        
        # Check if this looks like a model training issue
        if probabilities[0] < 0.3 and probabilities[1] > 0.7:
            print("\n⚠️  ISSUE: Model strongly predicts aggressive for non-aggressive image")
            print("   This suggests the training data or model may have issues:")
            print("   - Training labels might be swapped")
            print("   - Model might be overfitted to aggressive patterns")
            print("   - Feature extraction might not capture the right behavioral cues")
        
    else:
        print("   No aggression classifier loaded")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    debug_classification()
