import os
import numpy as np
import pandas as pd
import pickle
import cv2
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.metrics import classification_report, accuracy_score
from ultralytics import YOLO


class DogAggressionDetector:
    def __init__(self, yolo_model_path):
        """
        Initialize aggression detector with your trained YOLO model
        
        Args:
            yolo_model_path: Path to your YOLO model (best.pt)
        """
        print(f"Loading YOLO model from: {yolo_model_path}")
        self.yolo_model = YOLO(yolo_model_path)
        self.scaler = None
        self.imputer = None
        self.feature_selector = None
        self.classifier = None
        print("✅ YOLO model loaded successfully!")
        
        # YOLO Dog Keypoint Mapping (24 keypoints)
        self.YOLO_DOG_KEYPOINTS = {
            0: "nose", 1: "left_eye", 2: "right_eye", 3: "left_ear", 4: "right_ear",
            5: "left_front_shoulder", 6: "right_front_shoulder", 
            7: "left_front_elbow", 8: "right_front_elbow",
            9: "left_front_paw", 10: "right_front_paw",
            11: "left_hind_hip", 12: "right_hind_hip",
            13: "left_hind_knee", 14: "right_hind_knee",
            15: "left_hind_paw", 16: "right_hind_paw",
            17: "neck", 18: "back_spine_1", 19: "back_spine_2", 20: "back_spine_3",
            21: "tail_base", 22: "tail_mid", 23: "tail_tip"
        }
        
    def detect_keypoints(self, image_path):
        """Extract 24 keypoints from dog image using YOLO"""
        try:
            results = self.yolo_model(image_path, verbose=False)
            
            if len(results) > 0 and hasattr(results[0], 'keypoints') and results[0].keypoints is not None:
                # Get keypoints: shape (1, 24, 3) -> (24, 3)
                keypoints = results[0].keypoints.data[0].cpu().numpy()
                return keypoints  # Shape: (24, 3) - [x, y, confidence]
            else:
                print(f"No keypoints detected in {image_path}")
                return None
                
        except Exception as e:
            print(f"Error processing {image_path}: {e}")
            return None
    
    def extract_behavioral_features(self, keypoints):
        """
        Extract behavioral features using correct YOLO dog keypoint mapping
        
        YOLO Dog Keypoint Indices:
        - Head: 0-4 (nose, eyes, ears)
        - Front legs: 5-10 (shoulders, elbows, paws) 
        - Hind legs: 11-16 (hips, knees, paws)
        - Spine: 17-20 (neck, back points)
        - Tail: 21-23 (base, mid, tip)
        """
        if keypoints is None:
            return np.zeros(35)
        
        features = []
        
        # Only use high-confidence keypoints  
        confident_kpts = keypoints[keypoints[:, 2] > 0.3]  # Lowered threshold
        
        if len(confident_kpts) < 5:
            return np.zeros(35)
        
        # Overall bounding box for normalization
        x_coords = confident_kpts[:, 0] 
        y_coords = confident_kpts[:, 1]
        
        bbox_width = np.max(x_coords) - np.min(x_coords)
        bbox_height = np.max(y_coords) - np.min(y_coords)
        
        if bbox_width == 0 or bbox_height == 0:
            return np.zeros(35)
            
        bbox_area = bbox_width * bbox_height
        aspect_ratio = bbox_width / bbox_height
        
        # Body center for relative measurements
        body_center_x = np.mean(x_coords)
        body_center_y = np.mean(y_coords)
        
        features.extend([bbox_width, bbox_height, bbox_area, aspect_ratio])
        
        # 1. HEAD ANALYSIS (indices 0-4: nose, eyes, ears)
        head_indices = [0, 1, 2, 3, 4]  # nose, left_eye, right_eye, left_ear, right_ear
        head_kpts = keypoints[head_indices]
        valid_head = head_kpts[head_kpts[:, 2] > 0.3]
        
        if len(valid_head) > 0:
            head_x = np.mean(valid_head[:, 0])
            head_y = np.mean(valid_head[:, 1])
            
            # Head position relative to body (normalized)
            head_forward_lean = (head_x - body_center_x) / bbox_width
            head_height = (body_center_y - head_y) / bbox_height  # Positive = head lower
            
            # Head keypoint spread (rigidity indicator)
            head_spread = np.std(valid_head[:, :2]) / bbox_width if len(valid_head) > 1 else 0
            
            features.extend([head_forward_lean, head_height, head_spread])
        else:
            features.extend([0, 0, 0])
        
        # 2. FRONT LEG ANALYSIS (indices 5-10: shoulders, elbows, paws)
        front_leg_indices = [5, 6, 7, 8, 9, 10]
        front_legs = keypoints[front_leg_indices]
        valid_front = front_legs[front_legs[:, 2] > 0.3]
        
        if len(valid_front) > 1:
            # Front stance width (normalized)
            front_width = (np.max(valid_front[:, 0]) - np.min(valid_front[:, 0])) / bbox_width
            # Front leg height variation (normalized)
            front_height_std = np.std(valid_front[:, 1]) / bbox_height
            
            # Front leg symmetry
            left_front_indices = [5, 7, 9]  # Left shoulder, elbow, paw
            right_front_indices = [6, 8, 10]  # Right shoulder, elbow, paw
            
            left_front = keypoints[left_front_indices]
            right_front = keypoints[right_front_indices]
            valid_left_front = left_front[left_front[:, 2] > 0.3]
            valid_right_front = right_front[right_front[:, 2] > 0.3]
            
            if len(valid_left_front) > 0 and len(valid_right_front) > 0:
                left_front_center = np.mean(valid_left_front[:, :2], axis=0)
                right_front_center = np.mean(valid_right_front[:, :2], axis=0)
                front_asymmetry = np.linalg.norm(left_front_center - right_front_center) / bbox_width
            else:
                front_asymmetry = 0
                
            features.extend([front_width, front_height_std, front_asymmetry])
        else:
            features.extend([0, 0, 0])
        
        # 3. HIND LEG ANALYSIS (indices 11-16: hips, knees, paws) 
        hind_leg_indices = [11, 12, 13, 14, 15, 16]
        hind_legs = keypoints[hind_leg_indices]
        valid_hind = hind_legs[hind_legs[:, 2] > 0.3]
        
        if len(valid_hind) > 1:
            # Hind stance width (normalized)
            hind_width = (np.max(valid_hind[:, 0]) - np.min(valid_hind[:, 0])) / bbox_width
            # Hind leg height variation (normalized)
            hind_height_std = np.std(valid_hind[:, 1]) / bbox_height
            
            # Hind leg symmetry
            left_hind_indices = [11, 13, 15]  # Left hip, knee, paw
            right_hind_indices = [12, 14, 16]  # Right hip, knee, paw
            
            left_hind = keypoints[left_hind_indices]
            right_hind = keypoints[right_hind_indices]
            valid_left_hind = left_hind[left_hind[:, 2] > 0.3]
            valid_right_hind = right_hind[right_hind[:, 2] > 0.3]
            
            if len(valid_left_hind) > 0 and len(valid_right_hind) > 0:
                left_hind_center = np.mean(valid_left_hind[:, :2], axis=0)
                right_hind_center = np.mean(valid_right_hind[:, :2], axis=0)
                hind_asymmetry = np.linalg.norm(left_hind_center - right_hind_center) / bbox_width
            else:
                hind_asymmetry = 0
                
            features.extend([hind_width, hind_height_std, hind_asymmetry])
        else:
            features.extend([0, 0, 0])
        
        # 4. SPINE/BACK ANALYSIS (indices 17-20: neck, back points)
        spine_indices = [17, 18, 19, 20]  # neck, back_spine points
        spine_kpts = keypoints[spine_indices]
        valid_spine = spine_kpts[spine_kpts[:, 2] > 0.3]
        
        if len(valid_spine) > 2:
            spine_coords = valid_spine[:, :2]
            try:
                # Linear fit to spine for curvature analysis
                coeffs = np.polyfit(spine_coords[:, 0], spine_coords[:, 1], 1)
                predicted_y = np.polyval(coeffs, spine_coords[:, 0])
                spine_deviation = np.mean(np.abs(spine_coords[:, 1] - predicted_y)) / bbox_height
                spine_slope = abs(coeffs[0])  # Spine angle
                
                features.extend([spine_deviation, spine_slope])
            except:
                features.extend([0, 0])
        else:
            features.extend([0, 0])
        
        # 5. TAIL ANALYSIS (indices 21-23: base, mid, tip) - CRITICAL for aggression
        tail_indices = [21, 22, 23]  # tail_base, tail_mid, tail_tip
        tail_kpts = keypoints[tail_indices]
        valid_tail = tail_kpts[tail_kpts[:, 2] > 0.3]
        
        if len(valid_tail) > 1:
            tail_coords = valid_tail[:, :2]
            
            # Tail height relative to body center (normalized)
            tail_avg_y = np.mean(tail_coords[:, 1])
            tail_relative_height = (body_center_y - tail_avg_y) / bbox_height
            
            # Tail stiffness - low variation = stiff tail (aggression indicator)
            tail_x_var = np.var(tail_coords[:, 0]) / (bbox_width**2)
            tail_y_var = np.var(tail_coords[:, 1]) / (bbox_height**2)
            tail_stiffness = 1.0 / (tail_x_var + tail_y_var + 1e-6)
            
            # Tail angle/direction
            if len(valid_tail) > 2:
                tail_base = keypoints[21]  # tail_base
                tail_tip = keypoints[23]   # tail_tip
                if tail_base[2] > 0.3 and tail_tip[2] > 0.3:
                    tail_angle = np.arctan2(tail_tip[1] - tail_base[1], 
                                          tail_tip[0] - tail_base[0])
                    tail_angle_normalized = tail_angle / np.pi  # Normalize to [-1, 1]
                else:
                    tail_angle_normalized = 0
            else:
                tail_angle_normalized = 0
                
            features.extend([tail_relative_height, tail_stiffness, tail_angle_normalized])
        else:
            features.extend([0, 0, 0])
        
        # 6. OVERALL BODY SYMMETRY
        left_side_indices = [1, 3, 5, 7, 9, 11, 13, 15]   # Left eye, ear, leg points
        right_side_indices = [2, 4, 6, 8, 10, 12, 14, 16] # Right eye, ear, leg points
        
        left_kpts = keypoints[left_side_indices]
        right_kpts = keypoints[right_side_indices]
        
        valid_left = left_kpts[left_kpts[:, 2] > 0.3]
        valid_right = right_kpts[right_kpts[:, 2] > 0.3]
        
        if len(valid_left) > 0 and len(valid_right) > 0:
            left_center = np.mean(valid_left[:, :2], axis=0)
            right_center = np.mean(valid_right[:, :2], axis=0)
            symmetry_distance = np.linalg.norm(left_center - right_center) / bbox_width
            features.append(symmetry_distance)
        else:
            features.append(0)
        
        # 7. OVERALL TENSION INDICATORS
        avg_confidence = np.mean(keypoints[:, 2])
        high_conf_ratio = np.sum(keypoints[:, 2] > 0.5) / 24
        
        # Body compactness (tense vs relaxed posture)
        if len(confident_kpts) > 5:
            x_std = np.std(confident_kpts[:, 0]) / bbox_width
            y_std = np.std(confident_kpts[:, 1]) / bbox_height 
            body_compactness = 1.0 / (x_std + y_std + 1e-6)
            
            features.extend([avg_confidence, high_conf_ratio, body_compactness])
        else:
            features.extend([avg_confidence, high_conf_ratio, 0])
        
        # 8. SPECIFIC AGGRESSION INDICATORS
        # Distance from nose to body center (forward aggression lean)
        nose_kpt = keypoints[0]  # Index 0 = nose
        if nose_kpt[2] > 0.3:
            nose_to_body_distance = np.linalg.norm([nose_kpt[0] - body_center_x, 
                                                   nose_kpt[1] - body_center_y]) / bbox_width
            features.append(nose_to_body_distance)
        else:
            features.append(0)
        
        # Front vs hind leg positioning (weight distribution)
        if len(valid_front) > 0 and len(valid_hind) > 0:
            front_center_y = np.mean(valid_front[:, 1])
            hind_center_y = np.mean(valid_hind[:, 1])
            front_hind_y_diff = (hind_center_y - front_center_y) / bbox_height
            features.append(front_hind_y_diff)
        else:
            features.append(0)
        
        # 9. HEAD-TO-TAIL ALIGNMENT (posture indicator)
        nose_kpt = keypoints[0]   # nose
        tail_base_kpt = keypoints[21]  # tail_base
        
        if nose_kpt[2] > 0.3 and tail_base_kpt[2] > 0.3:
            head_tail_distance = np.linalg.norm([nose_kpt[0] - tail_base_kpt[0],
                                               nose_kpt[1] - tail_base_kpt[1]]) / bbox_width
            # Body alignment - straight vs curved
            body_alignment = head_tail_distance / (bbox_width + bbox_height)
            features.extend([head_tail_distance, body_alignment])
        else:
            features.extend([0, 0])
        
        # 10. EAR POSITION ANALYSIS
        left_ear = keypoints[3]   # left_ear
        right_ear = keypoints[4]  # right_ear
        
        if left_ear[2] > 0.3 and right_ear[2] > 0.3:
            ear_center_y = (left_ear[1] + right_ear[1]) / 2
            ear_height_relative = (body_center_y - ear_center_y) / bbox_height  # Positive = ears lower
            
            # Ear spread (alert vs relaxed)
            ear_spread = abs(left_ear[0] - right_ear[0]) / bbox_width
            
            features.extend([ear_height_relative, ear_spread])
        else:
            features.extend([0, 0])
        
        # Ensure exactly 35 features
        while len(features) < 35:
            features.append(0)
        
        return np.array(features[:35])
    
    def debug_keypoint_quality(self, dataset_folder):
        """Debug keypoint detection quality across dataset"""
        labels = {'aggressive': 1, 'non_aggressive': 0}
        
        for label_name, label_value in labels.items():
            folder_path = os.path.join(dataset_folder, label_name)
            if not os.path.exists(folder_path):
                continue
                
            image_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            print(f"\n=== {label_name.upper()} ANALYSIS ===")
            
            good_detections = 0
            total_confidence = []
            
            for i, img_file in enumerate(image_files[:20]):  # Sample 20 images
                img_path = os.path.join(folder_path, img_file)
                keypoints = self.detect_keypoints(img_path)
                
                if keypoints is not None:
                    avg_conf = np.mean(keypoints[:, 2])
                    high_conf_count = np.sum(keypoints[:, 2] > 0.5)
                    
                    if avg_conf > 0.3 and high_conf_count > 10:  # Good quality threshold
                        good_detections += 1
                    
                    total_confidence.append(avg_conf)
                    
                    if i < 3:  # Show first 3
                        print(f"  {img_file}: Avg conf={avg_conf:.3f}, High conf keypoints={high_conf_count}/24")
            
            print(f"Good quality detections: {good_detections}/20 ({good_detections/20*100:.1f}%)")
            if total_confidence:
                print(f"Average confidence across all: {np.mean(total_confidence):.3f}")
    
    def prepare_training_data(self, dataset_folder):
        """
        Prepare training data from folder structure with enhanced quality checks
        """
        X, y = [], []
        labels = {'aggressive': 1, 'non_aggressive': 0}
        
        for label_name, label_value in labels.items():
            folder_path = os.path.join(dataset_folder, label_name)
            
            if not os.path.exists(folder_path):
                print(f"Warning: {folder_path} not found")
                continue
                
            image_files = [f for f in os.listdir(folder_path) 
                          if f.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp'))]
            
            print(f"Processing {len(image_files)} {label_name} images...")
            
            successful_extractions = 0
            
            for img_file in image_files:
                img_path = os.path.join(folder_path, img_file)
                keypoints = self.detect_keypoints(img_path)
                
                if keypoints is not None:
                    features = self.extract_behavioral_features(keypoints)
                    # Only add if we extracted meaningful features
                    if not np.all(features == 0) and np.sum(features != 0) > 10:
                        X.append(features)
                        y.append(label_value)
                        successful_extractions += 1
            
            print(f"Successfully extracted features from {successful_extractions}/{len(image_files)} images")
                        
        print(f"Total samples prepared: {len(X)}")
        print(f"Aggressive: {sum(y)}, Non-aggressive: {len(y) - sum(y)}")
        
        return np.array(X), np.array(y)
    
    def train_model(self, X, y):
        """Enhanced model training with better hyperparameters"""
        if len(X) == 0:
            print("❌ No training data available!")
            return None
        
        print("🔄 Training enhanced aggression detection model...")
        print(f"Training samples: {len(X)}")
        print(f"Feature dimensions: {X.shape[1]}")
        
        # Check class balance
        unique, counts = np.unique(y, return_counts=True)
        print(f"Class distribution: {dict(zip(['Non-Aggressive', 'Aggressive'], counts))}")
        
        # Split data with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Enhanced preprocessing
        self.imputer = SimpleImputer(strategy='median')
        X_train_imputed = self.imputer.fit_transform(X_train)
        X_test_imputed = self.imputer.transform(X_test)
        
        # Use StandardScaler for better performance
        self.scaler = StandardScaler()
        X_train_scaled = self.scaler.fit_transform(X_train_imputed)
        X_test_scaled = self.scaler.transform(X_test_imputed)
        
        # Feature selection - use more features
        self.feature_selector = SelectKBest(f_classif, k=min(25, X_train_scaled.shape[1]))
        X_train_selected = self.feature_selector.fit_transform(X_train_scaled, y_train)
        X_test_selected = self.feature_selector.transform(X_test_scaled)
        
        print(f"Selected {X_train_selected.shape[1]} features out of {X_train_scaled.shape[1]}")
        
        # Better model configurations
        models = {
            'Random Forest': RandomForestClassifier(
                n_estimators=300, 
                max_depth=15, 
                min_samples_split=5,
                min_samples_leaf=2,
                class_weight='balanced', 
                random_state=42
            ),
            'Gradient Boosting': GradientBoostingClassifier(
                n_estimators=200, 
                max_depth=8, 
                learning_rate=0.05,
                subsample=0.8,
                random_state=42
            ),
        }
        
        best_score = 0
        best_model = None
        best_name = ""
        
        for name, model in models.items():
            # 10-fold cross validation
            cv_scores = cross_val_score(model, X_train_selected, y_train, cv=10, scoring='accuracy')
            avg_score = cv_scores.mean()
            std_score = cv_scores.std()
            
            print(f"{name}: CV Score = {avg_score:.3f} (+/- {std_score * 2:.3f})")
            
            if avg_score > best_score:
                best_score = avg_score
                best_model = model
                best_name = name
        
        # Train best model
        self.classifier = best_model
        self.classifier.fit(X_train_selected, y_train)
        
        # Detailed evaluation
        y_pred = self.classifier.predict(X_test_selected)
        test_accuracy = accuracy_score(y_test, y_pred)
        
        print(f"\n✅ Best model: {best_name}")
        print(f"Cross-validation score: {best_score:.3f}")
        print(f"Test accuracy: {test_accuracy:.3f}")
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred, target_names=['Non-Aggressive', 'Aggressive']))
        
        # Feature importance analysis
        if hasattr(self.classifier, 'feature_importances_'):
            feature_importance = self.classifier.feature_importances_
            top_features_idx = np.argsort(feature_importance)[-10:]
            print(f"\nTop 10 most important feature indices: {top_features_idx}")
            print("Feature importance scores:")
            for idx in top_features_idx[::-1]:  # Show in descending order
                print(f"  Feature {idx}: {feature_importance[idx]:.4f}")
        
        return test_accuracy
    
    def predict_aggression(self, image_path):
        """
        Predict if dog in image is aggressive or not
        
        Returns:
            tuple: (prediction_text, confidence_score)
        """
        if self.classifier is None:
            return "Model not trained yet!", 0.0
        
        # Extract keypoints
        keypoints = self.detect_keypoints(image_path)
        if keypoints is None:
            return "No dog detected in image", 0.0
        
        # Extract features
        features = self.extract_behavioral_features(keypoints)
        if np.all(features == 0):
            return "Insufficient keypoints detected", 0.0
        
        # Preprocess features
        features = features.reshape(1, -1)
        features_imputed = self.imputer.transform(features)
        features_scaled = self.scaler.transform(features_imputed)
        features_selected = self.feature_selector.transform(features_scaled)
        
        # Predict
        prediction = self.classifier.predict(features_selected)[0]
        probabilities = self.classifier.predict_proba(features_selected)[0]
        confidence = max(probabilities)
        
        result = "Aggressive" if prediction == 1 else "Non-Aggressive"
        
        return result, confidence
    
    def save_model(self, filepath):
        """Save trained model"""
        model_data = {
            'scaler': self.scaler,
            'imputer': self.imputer,
            'feature_selector': self.feature_selector,
            'classifier': self.classifier
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"✅ Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load trained model"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.scaler = model_data['scaler']
        self.imputer = model_data['imputer']
        self.feature_selector = model_data['feature_selector']
        self.classifier = model_data['classifier']
        
        print(f"✅ Model loaded from {filepath}")


# Example usage
if __name__ == "__main__":
    # Initialize detector with your YOLO model
    yolo_path = r"/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/models/best.pt"
    detector = DogAggressionDetector(yolo_path)
    
    # Option 1: Debug keypoint quality first
    print("\n🔍 DEBUG MODE - Check keypoint quality")
    dataset_path = r"/Users/aditya/Documents/AIBSS/dog-behavior-dashboard/dataset/IMAGESSS"
    # detector.debug_keypoint_quality(dataset_path)
    
    # Option 2: Train on your dataset
    print("\n📚 TRAINING MODE")
    print("Organize your images like this:")
    print("training_data/")
    print("├── aggressive/")
    print("│   ├── aggressive_dog1.jpg")
    print("│   └── aggressive_dog2.jpg") 
    print("└── non_aggressive/")
    print("    ├── calm_dog1.jpg")
    print("    └── calm_dog2.jpg")
    
    # Uncomment to train:
    # X, y = detector.prepare_training_data(dataset_path)
    # detector.train_model(X, y)
    # detector.save_model("dog_aggression_model_v2.pkl")
    
    # Option 3: Load pre-trained model and test
    print("\n🔮 PREDICTION MODE")
    print("After training, test on new images:")
    
    # Example prediction (update image path):
    # detector.load_model("dog_aggression_model_v2.pkl")
    # test_image = r"C:\Users\DELL\Desktop\Area 51\Delhi-Sarkaar\test_dog.jpg"
    # result, confidence = detector.predict_aggression(test_image)
    # print(f"Result: {result} (Confidence: {confidence:.3f})")
