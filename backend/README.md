# Dog Behavior Analysis API

A FastAPI backend for detecting and classifying dog aggression using YOLOv8.

## Features

- **Health Check**: `/health` - Check API status
- **Image Analysis**: `/analyze_image` - Analyze single images for dog aggression
- **Video Analysis**: `/analyze_video` - Analyze videos using majority vote across frames
- **Live Feed**: `/analyze_live` - Analyze frames from live webcam feed
- **Model Info**: `/model/info` - Get information about the loaded model

## Setup

1. **Install Dependencies**:
   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. **Ensure Model File**:
   Make sure `models/best.pt` exists in the backend directory.

3. **Run the Server**:
   ```bash
   uvicorn app:app --reload --host 0.0.0.0 --port 8000
   ```

## API Endpoints

### GET /health
Returns server status.

**Response**:
```json
{
  "status": "ok",
  "message": "Dog Behavior Analysis API is running"
}
```

### POST /analyze_image
Analyze an uploaded image for dog aggression.

**Request**: Multipart form data with image file
**Response**:
```json
{
  "result": "Aggressive",
  "confidence": 0.96,
  "filename": "dog.jpg",
  "dog_detected": true,
  "bbox": [100, 50, 300, 250]
}
```

### POST /analyze_video
Analyze an uploaded video using majority vote across frames.

**Request**: Multipart form data with video file
**Response**:
```json
{
  "result": "Aggressive",
  "confidence": 0.87,
  "filename": "clip.mp4",
  "dog_detected": true,
  "frames_analyzed": 10,
  "aggressive_votes": 7,
  "non_aggressive_votes": 3
}
```

### POST /analyze_live
Analyze a single frame from live feed.

**Request**: Multipart form data with image frame
**Response**:
```json
{
  "result": "Non-Aggressive",
  "confidence": 0.92,
  "filename": "frame.jpg",
  "dog_detected": true,
  "bbox": [150, 75, 400, 300],
  "timestamp": "2025-09-03T10:30:45.123456"
}
```

## Example Usage

### Python Client Example

```python
import requests

# Health check
response = requests.get("http://localhost:8000/health")
print(response.json())

# Analyze image
with open("dog_image.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/analyze_image", files=files)
    result = response.json()
    print(f"Result: {result['result']}, Confidence: {result['confidence']}")

# Analyze video
with open("dog_video.mp4", "rb") as f:
    files = {"file": f}
    response = requests.post("http://localhost:8000/analyze_video", files=files)
    result = response.json()
    print(f"Video Result: {result['result']}, Confidence: {result['confidence']}")
```

### cURL Examples

```bash
# Health check
curl -X GET "http://localhost:8000/health"

# Analyze image
curl -X POST "http://localhost:8000/analyze_image" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@dog_image.jpg"

# Analyze video
curl -X POST "http://localhost:8000/analyze_video" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@dog_video.mp4"
```

## Development

- **Interactive API Documentation**: Visit `http://localhost:8000/docs` after starting the server
- **Alternative Documentation**: Visit `http://localhost:8000/redoc`

## Notes

- The API includes CORS middleware for frontend integration
- Video analysis processes every 5th frame for efficiency (max 50 frames)
- All responses include proper error handling and logging
- The model is loaded once at startup for optimal performance
