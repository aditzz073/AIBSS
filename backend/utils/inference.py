import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import UploadFile
import tempfile
import logging
from typing import Dict, Tuple
import os
import pickle

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DogAggressionDetector:
    def __init__(self, model_path: str):
        """Initialize the YOLO model for dog detection and load aggression classifier."""
        self.model_path = model_path
        self.model = None
        self.aggression_classifier = None
        self.scaler = None
        self.imputer = None
        self.feature_selector = None
        self.load_model()
        self.load_aggression_model()
        
    def load_model(self):
        """Load the YOLOv8 model for dog detection."""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"YOLO model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading YOLO model: {str(e)}")
            raise
    
    def load_aggression_model(self):
        """Load the trained aggression classification model."""
        try:
            pkl_path = "/Users/aditya/Documents/AIBSS/dog_aggression_model.pkl"
            if os.path.exists(pkl_path):
                with open(pkl_path, 'rb') as f:
                    model_data = pickle.load(f)
                
                self.scaler = model_data.get('scaler')
                self.imputer = model_data.get('imputer')
                self.feature_selector = model_data.get('feature_selector')
                self.aggression_classifier = model_data.get('classifier')
                
                logger.info("Aggression classification model loaded successfully")
            else:
                logger.warning(f"Aggression model not found at {pkl_path}")
        except Exception as e:
            logger.error(f"Error loading aggression model: {str(e)}")
    
    def detect_keypoints(self, frame):
        """Extract keypoints from dog image using YOLO"""
        try:
            results = self.model(frame, verbose=False)
            
            if len(results) > 0 and hasattr(results[0], 'keypoints') and results[0].keypoints is not None:
                # Get keypoints: shape (1, 24, 3) -> (24, 3)
                keypoints = results[0].keypoints.data[0].cpu().numpy()
                return keypoints  # Shape: (24, 3) - [x, y, confidence]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error detecting keypoints: {e}")
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
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a single frame for dog aggression using keypoint-based classification.
        
        Args:
            frame: numpy array representing the image frame
            
        Returns:
            dict: Analysis result with prediction, confidence, and detection info
        """
        import time
        start_time = time.time()
        
        try:
            # First, detect if there's a dog in the image using YOLO
            results = self.model(frame, verbose=False)
            
            if not results or len(results) == 0:
                processing_time = time.time() - start_time
                return {
                    "prediction": "No Detection",
                    "result": "No Detection",  # Keep for backward compatibility
                    "confidence": 0.0,
                    "dog_detected": False,
                    "bbox": None,
                    "processing_time": processing_time
                }
            
            # Get the first result (assuming single image)
            result = results[0]
            
            # Check if any detections were made
            if result.boxes is None or len(result.boxes) == 0:
                processing_time = time.time() - start_time
                return {
                    "prediction": "No Detection",
                    "result": "No Detection",  # Keep for backward compatibility
                    "confidence": 0.0,
                    "dog_detected": False,
                    "bbox": None,
                    "processing_time": processing_time
                }
            
            # Get the detection with highest confidence for bounding box
            confidences = result.boxes.conf.cpu().numpy()
            boxes = result.boxes.xyxy.cpu().numpy()
            max_conf_idx = np.argmax(confidences)
            max_detection_confidence = float(confidences[max_conf_idx])
            bbox = boxes[max_conf_idx].tolist()
            
            # Extract keypoints for aggression classification
            keypoints = self.detect_keypoints(frame)
            
            if keypoints is None or self.aggression_classifier is None:
                # Fallback: if no keypoints or no aggression model, return neutral
                processing_time = time.time() - start_time
                return {
                    "prediction": "Non-Aggressive",
                    "result": "Non-Aggressive",
                    "confidence": max_detection_confidence,
                    "dog_detected": True,
                    "bbox": bbox,
                    "processing_time": processing_time,
                    "note": "Using detection confidence - aggression model not available"
                }
            
            # Extract behavioral features from keypoints
            features = self.extract_behavioral_features(keypoints)
            
            if np.all(features == 0):
                # No meaningful features extracted
                processing_time = time.time() - start_time
                return {
                    "prediction": "Non-Aggressive",
                    "result": "Non-Aggressive",
                    "confidence": max_detection_confidence,
                    "dog_detected": True,
                    "bbox": bbox,
                    "processing_time": processing_time,
                    "note": "Insufficient keypoints for classification"
                }
            
            # Preprocess features for classification
            features = features.reshape(1, -1)
            features_imputed = self.imputer.transform(features)
            features_scaled = self.scaler.transform(features_imputed)
            features_selected = self.feature_selector.transform(features_scaled)
            
            # Predict aggression using the trained classifier
            prediction = self.aggression_classifier.predict(features_selected)[0]
            probabilities = self.aggression_classifier.predict_proba(features_selected)[0]
            classification_confidence = max(probabilities)
            
            # Map prediction to label (0 = Non-Aggressive, 1 = Aggressive)
            result_label = "Aggressive" if prediction == 1 else "Non-Aggressive"
            
            logger.info(f"Detection: {result_label} with confidence {classification_confidence:.3f}")
            
            processing_time = time.time() - start_time
            
            return {
                "prediction": result_label,
                "result": result_label,  # Keep for backward compatibility
                "confidence": round(classification_confidence, 3),
                "dog_detected": True,
                "bbox": bbox,
                "processing_time": processing_time
            }
            
        except Exception as e:
            logger.error(f"Error in frame analysis: {str(e)}")
            return {
                "prediction": "Error",
                "result": "Error",  # Keep for backward compatibility
                "confidence": 0.0,
                "dog_detected": False,
                "bbox": None,
                "error": str(e)
            }
    
    def analyze_image(self, file: UploadFile) -> Dict:
        """
        Analyze an uploaded image file for dog aggression.
        
        Args:
            file: UploadFile object containing the image
            
        Returns:
            dict: Analysis result
        """
        try:
            # Read image file
            contents = file.file.read()
            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {
                    "prediction": "Invalid Image",
                    "result": "Invalid Image",  # Keep for backward compatibility
                    "confidence": 0.0,
                    "filename": file.filename,
                    "dog_detected": False,
                    "error": "Could not decode image"
                }
            
            # Analyze the frame
            analysis_result = self.analyze_frame(frame)
            analysis_result["filename"] = file.filename
            
            return analysis_result
            
        except Exception as e:
            logger.error(f"Error analyzing image: {str(e)}")
            return {
                "prediction": "Error",
                "result": "Error",  # Keep for backward compatibility
                "confidence": 0.0,
                "filename": file.filename,
                "dog_detected": False,
                "error": str(e)
            }
    
    def analyze_video(self, file: UploadFile) -> Dict:
        """
        Analyze an uploaded video file for dog aggression using majority vote.
        
        Args:
            file: UploadFile object containing the video
            
        Returns:
            dict: Analysis result based on majority vote across frames
        """
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                contents = file.file.read()
                tmp_file.write(contents)
                tmp_path = tmp_file.name
            
            try:
                # Open video file
                cap = cv2.VideoCapture(tmp_path)
                
                if not cap.isOpened():
                    return {
                        "prediction": "Invalid Video",
                        "result": "Invalid Video",  # Keep for backward compatibility
                        "confidence": 0.0,
                        "filename": file.filename,
                        "dog_detected": False,
                        "error": "Could not open video file"
                    }
                
                frame_results = []
                frame_count = 0
                max_frames = 50  # Limit to first 50 frames for efficiency
                
                while True:
                    ret, frame = cap.read()
                    if not ret or frame_count >= max_frames:
                        break
                    
                    # Analyze every 5th frame to reduce processing time
                    if frame_count % 5 == 0:
                        result = self.analyze_frame(frame)
                        if result["dog_detected"]:
                            frame_results.append(result)
                    
                    frame_count += 1
                
                cap.release()
                
                # Clean up temporary file
                os.unlink(tmp_path)
                
                if not frame_results:
                    return {
                        "prediction": "No Detection",
                        "result": "No Detection",  # Keep for backward compatibility
                        "confidence": 0.0,
                        "filename": file.filename,
                        "dog_detected": False,
                        "frames_analyzed": frame_count
                    }
                
                # Majority vote logic
                aggressive_votes = sum(1 for r in frame_results if r.get("prediction", r.get("result")) == "Aggressive")
                non_aggressive_votes = sum(1 for r in frame_results if r.get("prediction", r.get("result")) == "Non-Aggressive")
                
                # Calculate average confidence for the winning class
                if aggressive_votes > non_aggressive_votes:
                    final_result = "Aggressive"
                    confidences = [r["confidence"] for r in frame_results if r.get("prediction", r.get("result")) == "Aggressive"]
                elif non_aggressive_votes > aggressive_votes:
                    final_result = "Non-Aggressive"
                    confidences = [r["confidence"] for r in frame_results if r.get("prediction", r.get("result")) == "Non-Aggressive"]
                else:
                    # Tie - go with higher average confidence
                    agg_conf = np.mean([r["confidence"] for r in frame_results if r.get("prediction", r.get("result")) == "Aggressive"])
                    non_agg_conf = np.mean([r["confidence"] for r in frame_results if r.get("prediction", r.get("result")) == "Non-Aggressive"])
                    
                    if agg_conf >= non_agg_conf:
                        final_result = "Aggressive"
                        confidences = [r["confidence"] for r in frame_results if r.get("prediction", r.get("result")) == "Aggressive"]
                    else:
                        final_result = "Non-Aggressive"
                        confidences = [r["confidence"] for r in frame_results if r.get("prediction", r.get("result")) == "Non-Aggressive"]
                
                avg_confidence = np.mean(confidences) if confidences else 0.0
                
                logger.info(f"Video analysis complete: {final_result} (Agg: {aggressive_votes}, Non-Agg: {non_aggressive_votes})")
                
                return {
                    "prediction": final_result,
                    "result": final_result,  # Keep for backward compatibility
                    "confidence": round(avg_confidence, 3),
                    "filename": file.filename,
                    "dog_detected": True,
                    "frames_analyzed": len(frame_results),
                    "aggressive_votes": aggressive_votes,
                    "non_aggressive_votes": non_aggressive_votes
                }
                
            except Exception as e:
                # Clean up temporary file on error
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                raise e
                
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            return {
                "prediction": "Error",
                "result": "Error",  # Keep for backward compatibility
                "confidence": 0.0,
                "filename": file.filename,
                "dog_detected": False,
                "error": str(e)
            }

# Global detector instance (will be initialized in app.py)
detector: DogAggressionDetector = None

def get_detector() -> DogAggressionDetector:
    """Get the global detector instance."""
    return detector

def initialize_detector(model_path: str):
    """Initialize the global detector instance."""
    global detector
    detector = DogAggressionDetector(model_path)
