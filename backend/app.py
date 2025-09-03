from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import uvicorn

from utils.inference import initialize_detector, get_detector
from utils.video_analysis import initialize_video_detector, get_video_detector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the YOLO models on startup."""
    try:
        # Initialize image analysis model (existing functionality)
        image_model_path = Path(__file__).parent / "models" / "best.pt"
        if not image_model_path.exists():
            logger.error(f"Image model file not found at {image_model_path}")
            raise FileNotFoundError(f"Image model file not found at {image_model_path}")
        
        logger.info("Initializing image analysis YOLO model...")
        initialize_detector(str(image_model_path))
        logger.info("Image model initialized successfully!")
        
        # Initialize video analysis model (new functionality)
        video_model_path = Path(__file__).parent / "live_view" / "best.pt"
        if not video_model_path.exists():
            logger.error(f"Video model file not found at {video_model_path}")
            raise FileNotFoundError(f"Video model file not found at {video_model_path}")
        
        logger.info("Initializing video analysis YOLO model...")
        initialize_video_detector(str(video_model_path))
        logger.info("Video model initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize models: {str(e)}")
        raise
    
    yield

# Initialize FastAPI app
app = FastAPI(
    title="Dog Behavior Analysis API",
    description="API for detecting and classifying dog aggression using YOLOv8",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "message": "Dog Behavior Analysis API is running"}

@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...)):
    """
    Analyze an uploaded image for dog aggression.
    
    Args:
        file: Image file to analyze
        
    Returns:
        JSON response with analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an image (JPEG, PNG, etc.)"
            )
        
        logger.info(f"Analyzing image: {file.filename}")
        
        # Get detector and analyze image
        detector = get_detector()
        if detector is None:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        result = detector.analyze_image(file)
        
        # Log the result
        logger.info(f"Image analysis result: {result}")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_image: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze_video")
async def analyze_video(file: UploadFile = File(...)):
    """
    Analyze an uploaded video for dog aggression using OpenCV frame processing.
    Uses the new video analysis pipeline based on live_view/test.py logic.
    
    Args:
        file: Video file to analyze (MP4, AVI, etc.)
        
    Returns:
        JSON response with comprehensive video analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be a video (MP4, AVI, MOV, etc.)"
            )
        
        logger.info(f"Analyzing video: {file.filename}")
        
        # Get video detector and analyze
        video_detector = get_video_detector()
        if video_detector is None:
            raise HTTPException(status_code=500, detail="Video analysis model not initialized")
        
        result = video_detector.analyze_video_file(file)
        
        # Log the result
        logger.info(f"Video analysis result: {result['classification']} (confidence: {result['confidence']})")
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_video: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.post("/analyze_live")
async def analyze_live_frame(file: UploadFile = File(...)):
    """
    Analyze a single frame from live webcam feed for dog aggression.
    Optimized for real-time processing using the new video analysis pipeline.
    
    Args:
        file: Single frame image from webcam/live feed
        
    Returns:
        JSON response with real-time analysis results for the frame
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an image frame (JPEG, PNG)"
            )
        
        logger.debug(f"Analyzing live frame: {file.filename}")
        
        # Get video detector for live frame analysis
        video_detector = get_video_detector()
        if video_detector is None:
            raise HTTPException(status_code=500, detail="Live analysis model not initialized")
        
        result = video_detector.analyze_live_frame(file)
        
        # Add ISO timestamp for frontend
        import datetime
        result["iso_timestamp"] = datetime.datetime.now().isoformat()
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_live: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/detections")
async def get_detections():
    """
    Get detection data for heatmap visualization.
    
    Returns:
        JSON response with detection data including lat, lon, risk, label, timestamp
    """
    try:
        # TODO: Replace with real detection data from database
        # For now, returning mock data for testing
        import datetime
        import random
        
        # Generate mock detection data with realistic timestamps
        mock_detections = []
        
        # Base coordinates for Bangalore area
        base_lat = 12.9716
        base_lon = 77.5946
        
        # Generate 10-15 random detections
        num_detections = random.randint(10, 15)
        
        for i in range(num_detections):
            # Random location within ~5km radius of Bangalore center
            lat_offset = random.uniform(-0.05, 0.05)
            lon_offset = random.uniform(-0.05, 0.05)
            
            # Random risk score
            risk = random.uniform(0.1, 0.95)
            
            # Label based on risk (higher risk more likely to be aggressive)
            label = "Aggressive" if risk > 0.5 else "Non-Aggressive"
            
            # Random timestamp within last 2 hours
            minutes_ago = random.randint(5, 120)
            timestamp = datetime.datetime.now() - datetime.timedelta(minutes=minutes_ago)
            
            detection = {
                "lat": round(base_lat + lat_offset, 6),
                "lon": round(base_lon + lon_offset, 6),
                "risk": round(risk, 2),
                "label": label,
                "timestamp": timestamp.isoformat()
            }
            
            mock_detections.append(detection)
        
        logger.info(f"Returning {len(mock_detections)} detection records")
        
        return JSONResponse(content=mock_detections)
        
    except Exception as e:
        logger.error(f"Error getting detections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded models."""
    try:
        # Image analysis model info
        image_detector = get_detector()
        image_info = None
        if image_detector is not None:
            image_info = {
                "model_path": image_detector.model_path,
                "model_type": "YOLOv8 + Keypoint Classification",
                "classes": ["Aggressive", "Non-Aggressive"],
                "purpose": "Static image analysis with pose estimation",
                "status": "loaded"
            }
        
        # Video analysis model info
        video_detector = get_video_detector()
        video_info = None
        if video_detector is not None:
            video_info = {
                "model_path": video_detector.model_path,
                "model_type": "YOLOv8 Object Detection",
                "classes": video_detector.class_names,
                "purpose": "Video and live feed analysis",
                "confidence_threshold": video_detector.confidence_threshold,
                "aggression_threshold": video_detector.aggression_threshold,
                "status": "loaded"
            }
        
        return {
            "image_analysis": image_info,
            "video_analysis": video_info,
            "system_status": "operational" if image_info and video_info else "partial"
        }
        
    except Exception as e:
        logger.error(f"Error getting model info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Dog Behavior Analysis API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "analyze_image": "/analyze_image (Static image analysis with pose estimation)",
            "analyze_video": "/analyze_video (Video analysis with frame processing)",
            "analyze_live": "/analyze_live (Real-time live feed analysis)",
            "detections": "/detections (Detection data for heatmap)",
            "model_info": "/model/info (Model information)"
        },
        "docs": "/docs"
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )
