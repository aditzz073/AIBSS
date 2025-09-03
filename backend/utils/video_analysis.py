"""
Video Analysis Module for Dog Behavior Dashboard
Processes video files and live frames using OpenCV and YOLO for aggression detection.
Based on the logic from live_view/test.py with enhanced functionality.
"""

import cv2
import numpy as np
from ultralytics import YOLO
from fastapi import UploadFile
import tempfile
import logging
import time
import os
from typing import Dict, List, Tuple, Optional
from pathlib import Path

# Configure logging
logger = logging.getLogger(__name__)

class VideoAggressionDetector:
    """
    Enhanced aggression detector for video analysis using YOLO + OpenCV.
    Based on live_view/test.py logic with production-ready improvements.
    """
    
    def __init__(self, model_path: str):
        """
        Initialize the video aggression detector with trained YOLO model.
        
        Args:
            model_path: Path to the trained YOLO model (best.pt from live_view/)
        """
        self.model_path = model_path
        self.model = None
        self.load_model()
        
        # Class names from data.yaml in live_view/
        self.class_names = ['chasing dog', 'child', 'dog', 'dog biting child', 'running child']
        
        # Aggression scoring weights based on detected classes
        self.aggressive_classes = {
            'dog biting child': 1.0,     # Highest aggression indicator
            'chasing dog': 0.8,          # High aggression indicator  
            'running child': 0.6         # Medium aggression (child running away)
        }
        
        self.neutral_classes = {
            'child': 0.1,                # Neutral presence
            'dog': 0.1                   # Neutral presence
        }
        
        # Configuration
        self.confidence_threshold = 0.25
        self.aggression_threshold = 0.5  # Threshold for aggressive classification
        
    def load_model(self):
        """Load the YOLO model for aggression detection."""
        try:
            self.model = YOLO(self.model_path)
            logger.info(f"Video YOLO model loaded successfully from {self.model_path}")
        except Exception as e:
            logger.error(f"Error loading video YOLO model: {str(e)}")
            raise
    
    def analyze_frame(self, frame: np.ndarray) -> Dict:
        """
        Analyze a single frame for dog aggression using YOLO detection + scoring logic.
        
        Args:
            frame: OpenCV frame (numpy array)
            
        Returns:
            dict: Analysis result with classification, confidence, and detections
        """
        start_time = time.time()
        
        try:
            # Run YOLO detection on frame
            results = self.model.predict(source=frame, conf=self.confidence_threshold, verbose=False)
            
            if not results or len(results) == 0 or results[0].boxes is None:
                processing_time = time.time() - start_time
                return {
                    "classification": "NON-AGGRESSIVE",
                    "confidence": 0.0,
                    "dog_detected": False,
                    "detections": [],
                    "processing_time": processing_time,
                    "reason": "No objects detected"
                }
            
            # Process detections
            detections = []
            aggression_score = 0.0
            dog_detected = False
            max_detection_confidence = 0.0
            
            boxes = results[0].boxes
            for box, conf, cls in zip(boxes.xyxy, boxes.conf, boxes.cls):
                class_id = int(cls)
                class_name = self.class_names[class_id]
                confidence = float(conf)
                bbox = box.tolist()  # [x1, y1, x2, y2]
                
                detection = {
                    "class": class_name,
                    "confidence": round(confidence, 3),
                    "bbox": bbox
                }
                detections.append(detection)
                
                # Track highest detection confidence
                max_detection_confidence = max(max_detection_confidence, confidence)
                
                # Check if dog is detected
                if 'dog' in class_name.lower():
                    dog_detected = True
                
                # Calculate aggression score
                if class_name in self.aggressive_classes:
                    weight = self.aggressive_classes[class_name]
                    aggression_score += confidence * weight
                    logger.debug(f"Aggressive indicator: {class_name} (confidence: {confidence:.3f})")
                elif class_name in self.neutral_classes:
                    logger.debug(f"Neutral object: {class_name} (confidence: {confidence:.3f})")
            
            # Determine final classification
            if aggression_score >= self.aggression_threshold:
                classification = "AGGRESSIVE"
                prediction = "Aggressive"
                reason = self._get_aggression_reason(detections)
            else:
                classification = "NON-AGGRESSIVE"
                prediction = "Non-Aggressive"
                reason = "No significant aggressive behavior detected"
            
            processing_time = time.time() - start_time
            
            return {
                "classification": classification,
                "prediction": prediction,  # Added for frontend compatibility
                "confidence": round(max(aggression_score, max_detection_confidence), 3),
                "dog_detected": dog_detected,
                "detections": detections,
                "processing_time": processing_time,
                "reason": reason,
                "aggression_score": round(aggression_score, 3)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing frame: {str(e)}")
            processing_time = time.time() - start_time
            return {
                "classification": "ERROR",
                "confidence": 0.0,
                "dog_detected": False,
                "detections": [],
                "processing_time": processing_time,
                "error": str(e)
            }
    
    def _get_aggression_reason(self, detections: List[Dict]) -> str:
        """
        Generate detailed reason for aggressive classification.
        
        Args:
            detections: List of detection dictionaries
            
        Returns:
            str: Human-readable reason for classification
        """
        aggressive_objects = []
        for det in detections:
            if det['class'] in self.aggressive_classes:
                aggressive_objects.append(det['class'])
        
        if 'dog biting child' in aggressive_objects:
            return "Critical: Dog biting child detected"
        elif 'chasing dog' in aggressive_objects:
            return "High risk: Dog chasing behavior detected"
        elif 'running child' in aggressive_objects:
            return "Concern: Child running (possibly fleeing)"
        else:
            return "Multiple risk indicators present"
    
    def analyze_video_file(self, file: UploadFile, max_frames: int = 200, frame_skip: int = 2) -> Dict:
        """
        Analyze uploaded video file using frame-by-frame processing with majority vote.
        
        Args:
            file: FastAPI UploadFile containing video
            max_frames: Maximum number of frames to process
            frame_skip: Process every Nth frame (for efficiency)
            
        Returns:
            dict: Comprehensive video analysis results
        """
        start_time = time.time()
        temp_path = None
        
        try:
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
                contents = file.file.read()
                tmp_file.write(contents)
                temp_path = tmp_file.name
            
            # Open video with OpenCV
            cap = cv2.VideoCapture(temp_path)
            
            if not cap.isOpened():
                return {
                    "classification": "ERROR",
                    "confidence": 0.0,
                    "detections": [],
                    "processing_time": time.time() - start_time,
                    "source": file.filename,
                    "error": "Could not open video file"
                }
            
            # Video metadata
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            duration = total_frames / fps if fps > 0 else 0
            
            logger.info(f"Processing video: {file.filename} ({total_frames} frames, {fps:.1f} FPS, {duration:.1f}s)")
            
            frame_results = []
            frame_count = 0
            processed_frames = 0
            
            while True:
                ret, frame = cap.read()
                if not ret or processed_frames >= max_frames:
                    break
                
                # Process every Nth frame for efficiency
                if frame_count % frame_skip == 0:
                    result = self.analyze_frame(frame)
                    frame_results.append(result)
                    processed_frames += 1
                    
                    # Log progress for long videos
                    if processed_frames % 20 == 0:
                        logger.info(f"Processed {processed_frames} frames...")
                
                frame_count += 1
            
            cap.release()
            
            if not frame_results:
                total_processing_time = time.time() - start_time
                return {
                    "classification": "NO DETECTION",
                    "confidence": 0.0,
                    "detections": [],
                    "processing_time": total_processing_time,
                    "source": file.filename,
                    "frames_processed": 0
                }
            
            # Aggregate results using majority vote and confidence averaging
            aggressive_votes = 0
            non_aggressive_votes = 0
            all_detections = []
            aggressive_confidences = []
            non_aggressive_confidences = []
            total_aggression_score = 0.0
            
            for result in frame_results:
                all_detections.extend(result.get("detections", []))
                
                if result.get("aggression_score", 0) > 0:
                    total_aggression_score += result["aggression_score"]
                
                if result["classification"] == "AGGRESSIVE":
                    aggressive_votes += 1
                    aggressive_confidences.append(result["confidence"])
                elif result["classification"] == "NON-AGGRESSIVE":
                    non_aggressive_votes += 1
                    non_aggressive_confidences.append(result["confidence"])
            
            # Determine final classification
            if aggressive_votes > non_aggressive_votes:
                final_classification = "AGGRESSIVE"
                prediction_format = "Aggressive"
                final_confidence = np.mean(aggressive_confidences) if aggressive_confidences else 0.0
                reason = f"Aggressive behavior detected in {aggressive_votes}/{len(frame_results)} frames"
            elif non_aggressive_votes > aggressive_votes:
                final_classification = "NON-AGGRESSIVE"
                prediction_format = "Non-Aggressive"
                final_confidence = np.mean(non_aggressive_confidences) if non_aggressive_confidences else 0.0
                reason = "No significant aggressive behavior detected"
            else:
                # Tie - decide based on higher average confidence or aggression score
                avg_agg_conf = np.mean(aggressive_confidences) if aggressive_confidences else 0.0
                avg_non_agg_conf = np.mean(non_aggressive_confidences) if non_aggressive_confidences else 0.0
                avg_aggression_score = total_aggression_score / len(frame_results)
                
                if avg_agg_conf >= avg_non_agg_conf or avg_aggression_score >= self.aggression_threshold:
                    final_classification = "AGGRESSIVE"
                    prediction_format = "Aggressive"
                    final_confidence = avg_agg_conf
                    reason = f"Tie resolved by confidence/aggression score"
                else:
                    final_classification = "NON-AGGRESSIVE"
                    prediction_format = "Non-Aggressive"
                    final_confidence = avg_non_agg_conf
                    reason = "Tie resolved - no clear aggressive behavior"
            
            # Compile unique detections for summary
            unique_classes = list(set([det["class"] for det in all_detections]))
            sample_detections = []
            for class_name in unique_classes:
                class_detections = [det for det in all_detections if det["class"] == class_name]
                if class_detections:
                    # Take detection with highest confidence for this class
                    best_detection = max(class_detections, key=lambda x: x["confidence"])
                    sample_detections.append(best_detection)
            
            total_processing_time = time.time() - start_time
            
            logger.info(f"Video analysis complete: {final_classification} "
                       f"(Agg: {aggressive_votes}, Non-Agg: {non_aggressive_votes}, "
                       f"Conf: {final_confidence:.3f})")
            
            return {
                "classification": final_classification,
                "prediction": prediction_format,  # Added for frontend compatibility
                "confidence": round(final_confidence, 3),
                "detections": sample_detections,
                "processing_time": total_processing_time,
                "source": file.filename,
                "video_metadata": {
                    "duration": duration,
                    "fps": fps,
                    "total_frames": total_frames,
                    "frames_processed": len(frame_results),
                    "frame_skip": frame_skip
                },
                "frame_analysis": {
                    "aggressive_votes": aggressive_votes,
                    "non_aggressive_votes": non_aggressive_votes,
                    "average_aggression_score": round(total_aggression_score / len(frame_results), 3)
                },
                "reason": reason
            }
            
        except Exception as e:
            logger.error(f"Error analyzing video: {str(e)}")
            return {
                "classification": "ERROR",
                "confidence": 0.0,
                "detections": [],
                "processing_time": time.time() - start_time,
                "source": file.filename if file else "unknown",
                "error": str(e)
            }
        
        finally:
            # Clean up temporary file
            if temp_path and os.path.exists(temp_path):
                try:
                    os.unlink(temp_path)
                except Exception as e:
                    logger.warning(f"Failed to clean up temp file {temp_path}: {e}")
    
    def analyze_live_frame(self, file: UploadFile) -> Dict:
        """
        Analyze a single frame from live feed (optimized for real-time processing).
        
        Args:
            file: FastAPI UploadFile containing single frame image
            
        Returns:
            dict: Real-time analysis result
        """
        try:
            # Read image file
            contents = file.file.read()
            nparr = np.frombuffer(contents, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                return {
                    "classification": "ERROR",
                    "confidence": 0.0,
                    "dog_detected": False,
                    "detections": [],
                    "error": "Could not decode frame"
                }
            
            # Analyze frame with timestamp for live feed
            result = self.analyze_frame(frame)
            result["timestamp"] = time.time()
            result["source"] = "live_feed"
            
            return result
            
        except Exception as e:
            logger.error(f"Error analyzing live frame: {str(e)}")
            return {
                "classification": "ERROR",
                "confidence": 0.0,
                "dog_detected": False,
                "detections": [],
                "timestamp": time.time(),
                "source": "live_feed",
                "error": str(e)
            }


# Global video detector instance
video_detector: Optional[VideoAggressionDetector] = None

def get_video_detector() -> Optional[VideoAggressionDetector]:
    """Get the global video detector instance."""
    return video_detector

def initialize_video_detector(model_path: str):
    """Initialize the global video detector instance."""
    global video_detector
    video_detector = VideoAggressionDetector(model_path)
    logger.info("Video detector initialized successfully")
