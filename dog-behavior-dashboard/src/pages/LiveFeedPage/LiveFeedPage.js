import React, { useState, useRef, useEffect, useCallback } from 'react';
import './LiveFeedPage.css';

const LiveFeedPage = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [stream, setStream] = useState(null);
  const intervalRef = useRef(null);

  // Start webcam stream
  const startWebcam = useCallback(async () => {
    try {
      setError(null);
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 640 },
          height: { ideal: 480 },
          facingMode: 'user'
        },
        audio: false
      });

      if (videoRef.current) {
        videoRef.current.srcObject = mediaStream;
        setStream(mediaStream);
        setIsStreaming(true);

        // Start analyzing frames every 2 seconds
        intervalRef.current = setInterval(captureAndAnalyze, 2000);
      }
    } catch (err) {
      console.error('Error accessing webcam:', err);
      setError('Unable to access webcam. Please ensure you have granted camera permissions.');
    }
  }, []);

  // Stop webcam stream
  const stopWebcam = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
    }
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
    setIsStreaming(false);
    setPrediction(null);
    setIsAnalyzing(false);
  }, [stream]);

  // Capture frame from video and send to backend
  const captureAndAnalyze = useCallback(async () => {
    if (!videoRef.current || !canvasRef.current || !isStreaming) {
      return;
    }

    try {
      setIsAnalyzing(true);
      const video = videoRef.current;
      const canvas = canvasRef.current;
      const ctx = canvas.getContext('2d');

      // Set canvas dimensions to match video
      canvas.width = video.videoWidth || 640;
      canvas.height = video.videoHeight || 480;

      // Draw current video frame to canvas
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convert canvas to base64 JPEG
      const dataUrl = canvas.toDataURL('image/jpeg', 0.8);
      const base64Data = dataUrl.split(',')[1];

      // Send frame to backend
      const response = await fetch('/analyze_frame', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          frame: base64Data,
          timestamp: new Date().toISOString()
        })
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const result = await response.json();
      setPrediction({
        behavior: result.prediction || result.behavior || 'Unknown',
        confidence: result.confidence || 0,
        timestamp: new Date().toLocaleTimeString()
      });

    } catch (err) {
      console.error('Error analyzing frame:', err);
      setPrediction({
        behavior: 'Analysis Error',
        confidence: 0,
        timestamp: new Date().toLocaleTimeString(),
        error: true
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [isStreaming]);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      stopWebcam();
    };
  }, [stopWebcam]);

  return (
    <div className="live-feed-page">
      <div className="live-feed-container">
        <div className="page-header">
          <h1 className="page-title">🎥 Live Feed Analysis</h1>
          <p className="page-subtitle">
            Real-time dog behavior detection using your webcam
          </p>
        </div>

        <div className="feed-content">
          <div className="video-card">
            <div className="video-container">
              <video
                ref={videoRef}
                autoPlay
                playsInline
                muted
                className={`video-feed ${isStreaming ? 'streaming' : ''}`}
              />
              {!isStreaming && (
                <div className="video-placeholder">
                  <div className="placeholder-icon">📷</div>
                  <p>Click "Start Live Feed" to begin</p>
                </div>
              )}
              {isAnalyzing && (
                <div className="analyzing-overlay">
                  <div className="spinner"></div>
                  <span>Analyzing...</span>
                </div>
              )}
            </div>

            <div className="video-controls">
              {!isStreaming ? (
                <button 
                  onClick={startWebcam}
                  className="btn btn-primary"
                  disabled={isAnalyzing}
                >
                  <span>▶️</span>
                  Start Live Feed
                </button>
              ) : (
                <button 
                  onClick={stopWebcam}
                  className="btn btn-secondary"
                >
                  <span>⏹️</span>
                  Stop Feed
                </button>
              )}
            </div>
          </div>

          <div className="results-card">
            <h3 className="results-title">Analysis Results</h3>
            
            {error && (
              <div className="error-message">
                <div className="error-icon">⚠️</div>
                <p>{error}</p>
              </div>
            )}

            {prediction && !error && (
              <div className="prediction-result">
                <div className="prediction-main">
                  <div className="behavior-badge">
                    <span className="behavior-emoji">
                      {prediction.behavior === 'Calm' ? '😌' : 
                       prediction.behavior === 'Aggressive' ? '😠' :
                       prediction.behavior === 'Playful' ? '😊' :
                       prediction.behavior === 'Anxious' ? '😰' : '🤔'}
                    </span>
                    <span className="behavior-text">
                      {prediction.behavior}
                    </span>
                  </div>
                  
                  {prediction.confidence > 0 && (
                    <div className="confidence-meter">
                      <div className="confidence-label">
                        Confidence: {Math.round(prediction.confidence * 100)}%
                      </div>
                      <div className="confidence-bar">
                        <div 
                          className="confidence-fill"
                          style={{ width: `${prediction.confidence * 100}%` }}
                        ></div>
                      </div>
                    </div>
                  )}
                </div>
                
                <div className="prediction-meta">
                  <span className="timestamp">
                    Last updated: {prediction.timestamp}
                  </span>
                </div>

                {prediction.error && (
                  <div className="prediction-error">
                    Unable to connect to analysis server
                  </div>
                )}
              </div>
            )}

            {!prediction && !error && isStreaming && (
              <div className="waiting-message">
                <div className="pulse-icon">🔄</div>
                <p>Waiting for analysis results...</p>
                <small>Analysis starts automatically every 2 seconds</small>
              </div>
            )}

            {!prediction && !error && !isStreaming && (
              <div className="no-data-message">
                <div className="no-data-icon">📊</div>
                <p>No analysis data yet</p>
                <small>Start the live feed to see results</small>
              </div>
            )}
          </div>
        </div>

        <div className="info-section">
          <div className="info-card">
            <h4>How it works</h4>
            <ol>
              <li>Click "Start Live Feed" to access your camera</li>
              <li>Position your dog in front of the camera</li>
              <li>AI analyzes behavior every 2 seconds automatically</li>
              <li>View real-time predictions and confidence scores</li>
            </ol>
          </div>
          
          <div className="info-card">
            <h4>Supported Behaviors</h4>
            <ul>
              <li>😌 Calm - Relaxed, peaceful state</li>
              <li>😊 Playful - Active, engaging behavior</li>
              <li>😰 Anxious - Stressed or worried</li>
              <li>😠 Aggressive - Alert or defensive</li>
            </ul>
          </div>
        </div>

        {/* Hidden canvas for frame capture */}
        <canvas
          ref={canvasRef}
          style={{ display: 'none' }}
        />
      </div>
    </div>
  );
};

export default LiveFeedPage;
