import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import UploadFile
import tempfile
import logging
from typing import Dict, Tuple
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DogAggressionDetector:
    def __init__(self, model_path: str):
        """Initialize the YOLO model for dog aggression detection."""
        self.model_path = model_path
        self.model = None
        self.load_model()
        
    def load_model(self):
        """Load the YOLOv8 model."""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a single frame for dog aggression.
        
        Args:
            frame: numpy array representing the image frame
            
        Returns:
            dict: Analysis result with prediction, confidence, and detection info
        """
        try:
            # Run YOLO inference
            results = self.model(frame, verbose=False)
            
            if not results or len(results) == 0:
                return {
                    "result": "No Detection",
                    "confidence": 0.0,
                    "dog_detected": False,
                    "bbox": None
                }
            
            # Get the first result (assuming single image)
            result = results[0]
            
            # Check if any detections were made
            if result.boxes is None or len(result.boxes) == 0:
                return {
                    "result": "No Detection",
                    "confidence": 0.0,
                    "dog_detected": False,
                    "bbox": None
                }
            
            # Get the detection with highest confidence
            confidences = result.boxes.conf.cpu().numpy()
            classes = result.boxes.cls.cpu().numpy()
            boxes = result.boxes.xyxy.cpu().numpy()
            
            # Find the detection with highest confidence
            max_conf_idx = np.argmax(confidences)
            max_confidence = float(confidences[max_conf_idx])
            predicted_class = int(classes[max_conf_idx])
            bbox = boxes[max_conf_idx].tolist()
            
            # Map class index to label
            # Assuming class 0 = aggressive, class 1 = non_aggressive
            class_names = {0: "Aggressive", 1: "Non-Aggressive"}
            result_label = class_names.get(predicted_class, "Unknown")
            
            logger.info(f"Detection: {result_label} with confidence {max_confidence:.3f}")
            
            return {
                "result": result_label,
                "confidence": round(max_confidence, 3),
                "dog_detected": True,
                "bbox": bbox
            }
            
        except Exception as e:
            logger.error(f"Error in frame analysis: {str(e)}")
            return {
                "result": "Error",
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
                    "result": "Invalid Image",
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
                "result": "Error",
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
                        "result": "Invalid Video",
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
                        "result": "No Detection",
                        "confidence": 0.0,
                        "filename": file.filename,
                        "dog_detected": False,
                        "frames_analyzed": frame_count
                    }
                
                # Majority vote logic
                aggressive_votes = sum(1 for r in frame_results if r["result"] == "Aggressive")
                non_aggressive_votes = sum(1 for r in frame_results if r["result"] == "Non-Aggressive")
                
                # Calculate average confidence for the winning class
                if aggressive_votes > non_aggressive_votes:
                    final_result = "Aggressive"
                    confidences = [r["confidence"] for r in frame_results if r["result"] == "Aggressive"]
                elif non_aggressive_votes > aggressive_votes:
                    final_result = "Non-Aggressive"
                    confidences = [r["confidence"] for r in frame_results if r["result"] == "Non-Aggressive"]
                else:
                    # Tie - go with higher average confidence
                    agg_conf = np.mean([r["confidence"] for r in frame_results if r["result"] == "Aggressive"])
                    non_agg_conf = np.mean([r["confidence"] for r in frame_results if r["result"] == "Non-Aggressive"])
                    
                    if agg_conf >= non_agg_conf:
                        final_result = "Aggressive"
                        confidences = [r["confidence"] for r in frame_results if r["result"] == "Aggressive"]
                    else:
                        final_result = "Non-Aggressive"
                        confidences = [r["confidence"] for r in frame_results if r["result"] == "Non-Aggressive"]
                
                avg_confidence = np.mean(confidences) if confidences else 0.0
                
                logger.info(f"Video analysis complete: {final_result} (Agg: {aggressive_votes}, Non-Agg: {non_aggressive_votes})")
                
                return {
                    "result": final_result,
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
                "result": "Error",
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
