from ultralytics import YOLO
import cv2
import numpy as np
from pathlib import Path

class AggressionDetector:
    def __init__(self, model_path):
        """Initialize the aggression detector with your trained YOLO model"""
        self.model = YOLO(model_path)
        # Classes from your data.yaml: ['chasing dog', 'child', 'dog', 'dog biting child', 'running child']
        self.class_names = ['chasing dog', 'child', 'dog', 'dog biting child', 'running child']
        
        # Define aggression rules based on detected classes
        self.aggressive_classes = {
            'dog biting child': 1.0,     # Highest aggression indicator
            'chasing dog': 0.8,          # High aggression indicator  
            'running child': 0.6         # Medium aggression (child running away)
        }
        
        self.neutral_classes = {
            'child': 0.1,                # Neutral presence
            'dog': 0.1                   # Neutral presence
        }
    
    def analyze_image(self, image_path, conf_threshold=0.25):
        """Analyze image and classify as AGGRESSIVE or NON-AGGRESSIVE"""
        print(f"🔍 Analyzing: {Path(image_path).name}")
        print("=" * 50)
        
        # Run YOLO detection
        results = self.model.predict(source=image_path, conf=conf_threshold, verbose=False)
        
        if not results or results[0].boxes is None:
            print("❌ No objects detected")
            return {
                'classification': 'NON-AGGRESSIVE',
                'confidence': 0.0,
                'reason': 'No relevant objects detected',
                'detections': []
            }
        
        # Process detections
        detections = []
        aggression_score = 0.0
        max_confidence = 0.0
        
        boxes = results[0].boxes
        for box, conf, cls in zip(boxes.xyxy, boxes.conf, boxes.cls):
            class_id = int(cls)
            class_name = self.class_names[class_id]
            confidence = float(conf)
            
            detection = {
                'class': class_name,
                'confidence': confidence,
                'bbox': box.tolist()
            }
            detections.append(detection)
            
            # Calculate aggression score
            if class_name in self.aggressive_classes:
                weight = self.aggressive_classes[class_name]
                aggression_score += confidence * weight
                max_confidence = max(max_confidence, confidence)
                print(f"🚨 AGGRESSIVE INDICATOR: {class_name} (confidence: {confidence:.3f})")
            
            elif class_name in self.neutral_classes:
                print(f"👤 NEUTRAL: {class_name} (confidence: {confidence:.3f})")
        
        # Determine final classification
        # High threshold for aggressive classification to avoid false positives
        if aggression_score >= 0.5:  # Aggressive if score >= 0.5
            classification = 'AGGRESSIVE'
            emoji = '🔴'
            reason = self._get_aggression_reason(detections)
        else:
            classification = 'NON-AGGRESSIVE' 
            emoji = '🟢'
            reason = 'No significant aggressive behavior detected'
        
        # Display results
        print(f"\n{emoji} CLASSIFICATION: {classification}")
        print(f"📊 Aggression Score: {aggression_score:.3f}")
        print(f"💭 Reason: {reason}")
        print(f"🎯 Total Detections: {len(detections)}")
        
        # Show detailed detection list
        if detections:
            print(f"\n📋 Detected Objects:")
            for i, det in enumerate(detections, 1):
                print(f"  {i}. {det['class']} (confidence: {det['confidence']:.3f})")
        
        return {
            'classification': classification,
            'confidence': aggression_score,
            'reason': reason,
            'detections': detections,
            'emoji': emoji
        }
    
    def _get_aggression_reason(self, detections):
        """Generate reason for aggressive classification"""
        aggressive_objects = []
        for det in detections:
            if det['class'] in self.aggressive_classes:
                aggressive_objects.append(det['class'])
        
        if 'dog biting child' in aggressive_objects:
            return "🚨 CRITICAL: Dog biting child detected!"
        elif 'chasing dog' in aggressive_objects:
            return "⚠️ HIGH RISK: Dog chasing behavior detected"
        elif 'running child' in aggressive_objects:
            return "⚠️ CONCERN: Child running (possibly fleeing)"
        else:
            return "Multiple risk indicators present"
    
    def batch_analyze(self, image_folder, conf_threshold=0.25):
        """Analyze multiple images in a folder"""
        image_folder = Path(image_folder)
        image_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
        
        results = []
        aggressive_count = 0
        
        print(f"🔍 BATCH ANALYSIS: {image_folder}")
        print("=" * 60)
        
        for img_path in image_folder.iterdir():
            if img_path.suffix.lower() in image_extensions:
                result = self.analyze_image(str(img_path), conf_threshold)
                results.append({
                    'image': img_path.name,
                    'result': result
                })
                
                if result['classification'] == 'AGGRESSIVE':
                    aggressive_count += 1
                
                print("\n" + "-" * 50 + "\n")
        
        # Summary
        total_images = len(results)
        non_aggressive_count = total_images - aggressive_count
        
        print(f"📊 BATCH SUMMARY:")
        print(f"  Total Images: {total_images}")
        print(f"  🔴 Aggressive: {aggressive_count}")
        print(f"  🟢 Non-Aggressive: {non_aggressive_count}")
        
        if total_images > 0:
            aggression_rate = (aggressive_count / total_images) * 100
            print(f"  📈 Aggression Rate: {aggression_rate:.1f}%")
        
        return results

# Initialize detector with your trained model
detector = AggressionDetector('/Users/aditya/Documents/AIBSS/backend/live_view/best.pt')

# Test on single image
single_result = detector.analyze_image(r'/Users/aditya/Documents/AIBSS/backend/live_view/doggie.jpg')

# # Test on multiple images (batch analysis)
# print("\n" + "=" * 60)
# print("🔄 STARTING BATCH ANALYSIS")
# print("=" * 60)
# batch_results = detector.batch_analyze(r'/Users/aditya/Documents/AIBSS/backend/live_view/photograph.jpeg')