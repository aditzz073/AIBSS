# Dog Behavior Dashboard - Redesigned Backend

## Overview

The Dog Behavior Dashboard backend has been redesigned to support three distinct analysis modes:

1. **Image Analysis** - Static image analysis using pose estimation (unchanged)
2. **Video Analysis** - Frame-by-frame video processing with majority vote
3. **Live Feed Analysis** - Real-time frame analysis for webcam feeds

## Architecture

### Models

- **Image Analysis**: Uses `models/best.pt` with keypoint detection and behavioral feature extraction
- **Video/Live Analysis**: Uses `live_view/best.pt` with object detection and aggression scoring

### Key Components

```
backend/
├── app.py                          # Main FastAPI application
├── utils/
│   ├── inference.py               # Image analysis (pose estimation)
│   └── video_analysis.py          # Video/live analysis (object detection)
├── models/
│   └── best.pt                    # Image analysis model
├── live_view/
│   ├── best.pt                    # Video analysis model
│   └── test.py                    # Original aggression detection logic
└── test_redesigned_backend.py     # Comprehensive test suite
```

## API Endpoints

### 1. Image Analysis - `/analyze_image`
**Purpose**: Analyze static images using pose estimation
**Model**: `models/best.pt` + keypoint classification
**Method**: POST (multipart/form-data)

**Response Format**:
```json
{
    "prediction": "AGGRESSIVE|NON-AGGRESSIVE",
    "confidence": 0.87,
    "dog_detected": true,
    "bbox": [x1, y1, x2, y2],
    "processing_time": 1.25,
    "filename": "image.jpg"
}
```

### 2. Video Analysis - `/analyze_video`
**Purpose**: Analyze uploaded videos with frame-by-frame processing
**Model**: `live_view/best.pt` + aggression scoring
**Method**: POST (multipart/form-data)

**Response Format**:
```json
{
    "classification": "AGGRESSIVE|NON-AGGRESSIVE",
    "confidence": 0.87,
    "detections": [
        {
            "class": "dog biting child",
            "confidence": 0.92,
            "bbox": [x1, y1, x2, y2]
        }
    ],
    "processing_time": 15.3,
    "source": "video.mp4",
    "video_metadata": {
        "duration": 10.5,
        "fps": 30.0,
        "total_frames": 315,
        "frames_processed": 63,
        "frame_skip": 5
    },
    "frame_analysis": {
        "aggressive_votes": 12,
        "non_aggressive_votes": 51,
        "average_aggression_score": 0.23
    },
    "reason": "No significant aggressive behavior detected"
}
```

### 3. Live Feed Analysis - `/analyze_live`
**Purpose**: Real-time analysis of individual frames from live feed
**Model**: `live_view/best.pt` + aggression scoring
**Method**: POST (multipart/form-data)

**Response Format**:
```json
{
    "classification": "AGGRESSIVE|NON-AGGRESSIVE",
    "confidence": 0.87,
    "dog_detected": true,
    "detections": [
        {
            "class": "dog biting child",
            "confidence": 0.92,
            "bbox": [x1, y1, x2, y2]
        }
    ],
    "processing_time": 0.15,
    "timestamp": 1693824000.123,
    "iso_timestamp": "2023-09-04T15:30:00.123456",
    "source": "live_feed",
    "reason": "Critical: Dog biting child detected",
    "aggression_score": 0.92
}
```

### 4. Model Information - `/model/info`
**Purpose**: Get information about loaded models
**Method**: GET

**Response Format**:
```json
{
    "image_analysis": {
        "model_path": "/path/to/models/best.pt",
        "model_type": "YOLOv8 + Keypoint Classification",
        "classes": ["Aggressive", "Non-Aggressive"],
        "purpose": "Static image analysis with pose estimation",
        "status": "loaded"
    },
    "video_analysis": {
        "model_path": "/path/to/live_view/best.pt",
        "model_type": "YOLOv8 Object Detection",
        "classes": ["chasing dog", "child", "dog", "dog biting child", "running child"],
        "purpose": "Video and live feed analysis",
        "confidence_threshold": 0.25,
        "aggression_threshold": 0.5,
        "status": "loaded"
    },
    "system_status": "operational"
}
```

## Aggression Detection Logic

### Video/Live Feed Analysis

The new video analysis pipeline uses object detection with aggression scoring:

#### Class-Based Scoring:
- **dog biting child**: 1.0 (Critical)
- **chasing dog**: 0.8 (High Risk)
- **running child**: 0.6 (Medium Risk)
- **child**: 0.1 (Neutral)
- **dog**: 0.1 (Neutral)

#### Classification Rules:
- **AGGRESSIVE**: Aggression score ≥ 0.5
- **NON-AGGRESSIVE**: Aggression score < 0.5

#### Video Processing:
1. Extract frames (process every 5th frame for efficiency)
2. Analyze each frame individually
3. Apply majority vote across all frames
4. Calculate confidence based on winning class average

## Configuration

### Video Analysis Parameters:
- **Confidence Threshold**: 0.25 (minimum detection confidence)
- **Aggression Threshold**: 0.5 (classification boundary)
- **Max Frames**: 100 (limit for video processing)
- **Frame Skip**: 5 (process every 5th frame)

## Installation & Setup

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Model Files**:
   - Ensure `models/best.pt` exists (for image analysis)
   - Ensure `live_view/best.pt` exists (for video analysis)

3. **Start Server**:
   ```bash
   python app.py
   ```
   Or:
   ```bash
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```

## Testing

Run the comprehensive test suite:
```bash
python test_redesigned_backend.py
```

This tests:
- Health check
- Model initialization
- Image analysis functionality
- Live feed analysis functionality
- Video analysis functionality

## Error Handling

All endpoints include comprehensive error handling:
- File validation (MIME type checking)
- Model availability verification
- Processing error recovery
- Detailed error messages in responses

## Performance Considerations

### Video Analysis:
- Frame skipping reduces processing time
- Maximum frame limit prevents timeout
- Background cleanup of temporary files

### Live Feed:
- Optimized for low latency
- Minimal memory footprint
- Real-time processing capabilities

## CORS Configuration

CORS is enabled for all origins during development. For production:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Specify frontend URL
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

## Logging

All operations are logged with appropriate levels:
- INFO: Normal operations, results
- DEBUG: Frame processing details
- ERROR: Exceptions and failures
- WARNING: Non-critical issues

## Production Deployment

For production deployment:
1. Update CORS origins
2. Configure proper logging levels
3. Set up health monitoring
4. Consider GPU acceleration for video processing
5. Implement rate limiting for API endpoints

## Migration Notes

This redesign maintains backward compatibility:
- `/analyze_image` endpoint unchanged
- Response formats include legacy fields where applicable
- Existing frontend integration should work seamlessly
