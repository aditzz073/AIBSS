from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os
from pathlib import Path
import uvicorn

from utils.inference import initialize_detector, get_detector

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the YOLO model on startup."""
    try:
        model_path = Path(__file__).parent / "models" / "best.pt"
        if not model_path.exists():
            logger.error(f"Model file not found at {model_path}")
            raise FileNotFoundError(f"Model file not found at {model_path}")
        
        logger.info("Initializing YOLO model...")
        initialize_detector(str(model_path))
        logger.info("Model initialized successfully!")
        
    except Exception as e:
        logger.error(f"Failed to initialize model: {str(e)}")
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
    Analyze an uploaded video for dog aggression using majority vote across frames.
    
    Args:
        file: Video file to analyze
        
    Returns:
        JSON response with analysis results
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('video/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be a video (MP4, AVI, etc.)"
            )
        
        logger.info(f"Analyzing video: {file.filename}")
        
        # Get detector and analyze video
        detector = get_detector()
        if detector is None:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        result = detector.analyze_video(file)
        
        # Log the result
        logger.info(f"Video analysis result: {result}")
        
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
    This endpoint is designed for continuous frame analysis from frontend.
    
    Args:
        file: Single frame image from webcam
        
    Returns:
        JSON response with analysis results for the frame
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400, 
                detail="File must be an image frame"
            )
        
        logger.debug(f"Analyzing live frame: {file.filename}")
        
        # Get detector and analyze frame
        detector = get_detector()
        if detector is None:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        result = detector.analyze_image(file)
        
        # For live feed, we might want to include timestamp
        import datetime
        result["timestamp"] = datetime.datetime.now().isoformat()
        
        return JSONResponse(content=result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in analyze_live: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/model/info")
async def get_model_info():
    """Get information about the loaded model."""
    try:
        detector = get_detector()
        if detector is None:
            raise HTTPException(status_code=500, detail="Model not initialized")
        
        return {
            "model_path": detector.model_path,
            "model_type": "YOLOv8",
            "classes": ["Aggressive", "Non-Aggressive"],
            "status": "loaded"
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
            "analyze_image": "/analyze_image",
            "analyze_video": "/analyze_video",
            "analyze_live": "/analyze_live",
            "model_info": "/model/info"
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
