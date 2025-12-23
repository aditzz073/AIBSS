from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from pathlib import Path
import logging
import uvicorn
import datetime
import random

from utils.inference import initialize_detector, get_detector
from utils.video_analysis import initialize_video_detector, get_video_detector

# --------------------------------------------------
# Logging configuration
# --------------------------------------------------
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent

# --------------------------------------------------
# Lifespan: model initialization
# --------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        # ---------- Image model (REQUIRED) ----------
        image_model_path = BASE_DIR / "models" / "best.pt"
        if not image_model_path.exists():
            raise FileNotFoundError(
                f"Image model not found at {image_model_path}"
            )

        logger.info("Initializing image analysis model...")
        initialize_detector(str(image_model_path))
        logger.info("Image model loaded successfully")

        # ---------- Video model (OPTIONAL) ----------
        video_model_path = BASE_DIR / "live_view" / "best.pt"
        if video_model_path.exists():
            logger.info("Initializing video analysis model...")
            initialize_video_detector(str(video_model_path))
            logger.info("Video model loaded successfully")
        else:
            logger.warning(
                f"Video model not found at {video_model_path}. "
                "Video endpoints will be disabled."
            )

    except Exception as e:
        logger.error(f"Startup failed: {e}")
        raise

    yield

# --------------------------------------------------
# FastAPI app
# --------------------------------------------------
app = FastAPI(
    title="Dog Behavior Analysis API",
    description="YOLOv8-based dog aggression detection",
    version="1.0.0",
    lifespan=lifespan
)

# --------------------------------------------------
# CORS
# --------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],   # tighten for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# Health
# --------------------------------------------------
@app.get("/health")
async def health_check():
    return {"status": "ok"}

# --------------------------------------------------
# Image analysis
# --------------------------------------------------
@app.post("/analyze_image")
async def analyze_image(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    detector = get_detector()
    if detector is None:
        raise HTTPException(status_code=500, detail="Image model not initialized")

    result = detector.analyze_image(file)
    return JSONResponse(content=result)

# --------------------------------------------------
# Video analysis
# --------------------------------------------------
@app.post("/analyze_video")
async def analyze_video(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("video/"):
        raise HTTPException(status_code=400, detail="Invalid video file")

    video_detector = get_video_detector()
    if video_detector is None:
        raise HTTPException(
            status_code=503,
            detail="Video model not available"
        )

    result = video_detector.analyze_video_file(file)
    return JSONResponse(content=result)

# --------------------------------------------------
# Live frame analysis
# --------------------------------------------------
@app.post("/analyze_live")
async def analyze_live_frame(file: UploadFile = File(...)):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid image file")

    video_detector = get_video_detector()
    if video_detector is None:
        raise HTTPException(
            status_code=503,
            detail="Live analysis unavailable"
        )

    result = video_detector.analyze_live_frame(file)
    result["timestamp"] = datetime.datetime.now().isoformat()
    return JSONResponse(content=result)

# --------------------------------------------------
# Heatmap data (mock)
# --------------------------------------------------
@app.get("/detections")
async def get_detections():
    base_lat, base_lon = 12.9716, 77.5946
    detections = []

    for _ in range(random.randint(10, 15)):
        detections.append({
            "lat": round(base_lat + random.uniform(-0.05, 0.05), 6),
            "lon": round(base_lon + random.uniform(-0.05, 0.05), 6),
            "risk": round(random.uniform(0.1, 0.95), 2),
            "label": "Aggressive",
            "timestamp": datetime.datetime.now().isoformat()
        })

    return detections

# --------------------------------------------------
# Model info
# --------------------------------------------------
@app.get("/model/info")
async def model_info():
    return {
        "image_model_loaded": get_detector() is not None,
        "video_model_loaded": get_video_detector() is not None
    }

# --------------------------------------------------
# Root
# --------------------------------------------------
@app.get("/")
async def root():
    return {
        "message": "Dog Behavior Analysis API",
        "docs": "/docs"
    }

# --------------------------------------------------
# Entry point
# --------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
