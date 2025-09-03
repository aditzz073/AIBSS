import React, { useState, useRef, useCallback, useEffect } from 'react';
import Webcam from 'react-webcam';
import './LiveFeedPage.css';
import { analyzeLiveFrame } from '../../api';

const LiveFeedPage = () => {
  const webcamRef = useRef(null);
  const [isStreaming, setIsStreaming] = useState(false);
  const [prediction, setPrediction] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const [analysisInterval, setAnalysisInterval] = useState(null);
  const [webcamReady, setWebcamReady] = useState(false);

  // Webcam constraints
  const videoConstraints = {
    width: 640,
    height: 480,
    facingMode: 'user'
  };

  // Capture frame from webcam and send to backend
  const captureAndAnalyze = useCallback(async () => {
    console.log('🔍 captureAndAnalyze called, isStreaming:', isStreaming, 'webcamReady:', webcamReady);
    
    if (!webcamRef.current || !isStreaming || !webcamReady) {
      console.log('❌ Webcam not ready:', { 
        webcamRef: !!webcamRef.current, 
        isStreaming, 
        webcamReady 
      });
      return;
    }

    try {
      setIsAnalyzing(true);
      console.log('📸 Capturing frame...');
      
      // Capture screenshot from webcam
      const imageSrc = webcamRef.current.getScreenshot();
      
      if (!imageSrc) {
        throw new Error('Failed to capture frame from webcam');
      }
      
      console.log('✅ Frame captured, size:', imageSrc.length);

      // Convert base64 to File object
      const response = await fetch(imageSrc);
      const blob = await response.blob();
      const file = new File([blob], 'webcam-frame.jpg', { type: 'image/jpeg' });
      
      console.log('📤 Sending to API, file size:', file.size);

      // Send frame to backend
      const result = await analyzeLiveFrame(file);
      
      console.log('📥 Live feed API response:', result); // Debug log
      
      setPrediction({
        behavior: result.classification || result.prediction || 'Unknown',
        confidence: result.confidence || 0,
        timestamp: new Date().toLocaleTimeString(),
        processing_time: result.processing_time,
        reason: result.reason,
        detections: result.detections || [],
        dog_detected: result.dog_detected,
        error: false
      });

      console.log('✅ Prediction set successfully');

    } catch (err) {
      console.error('❌ Error analyzing frame:', err);
      setPrediction({
        behavior: 'Analysis Error',
        confidence: 0,
        timestamp: new Date().toLocaleTimeString(),
        error: true,
        errorMessage: err.message
      });
    } finally {
      setIsAnalyzing(false);
    }
  }, [isStreaming, webcamReady]);

  // Start webcam stream and analysis
  const startWebcam = useCallback(() => {
    console.log('🎬 Starting webcam...');
    setIsStreaming(true);
    setError(null);
    setWebcamReady(false);
    
    console.log('✅ Webcam stream started, waiting for ready state...');
  }, []);

  // Set up analysis interval when webcam becomes ready
  useEffect(() => {
    if (isStreaming && webcamReady && !analysisInterval) {
      console.log('⏰ Setting up interval for analysis every 3 seconds');
      const interval = setInterval(() => {
        console.log('🔄 Interval triggered, calling captureAndAnalyze');
        captureAndAnalyze();
      }, 3000);
      setAnalysisInterval(interval);
      console.log('✅ Analysis interval started, interval ID:', interval);
    }
  }, [isStreaming, webcamReady, analysisInterval, captureAndAnalyze]);

  // Stop webcam stream and analysis
  const stopWebcam = useCallback(() => {
    setIsStreaming(false);
    setWebcamReady(false);
    setPrediction(null);
    setIsAnalyzing(false);
    setError(null);
    
    if (analysisInterval) {
      clearInterval(analysisInterval);
      setAnalysisInterval(null);
    }
  }, [analysisInterval]);

  // Handle webcam user media error
  const handleUserMediaError = useCallback((error) => {
    console.error('Webcam error:', error);
    setError('Unable to access webcam. Please ensure you have granted camera permissions.');
    setIsStreaming(false);
    setWebcamReady(false);
  }, []);

  // Handle when webcam stream is loaded and ready
  const handleWebcamReady = useCallback(() => {
    console.log('📹 Webcam stream is ready');
    setWebcamReady(true);
    setError(null);
  }, []);

  // Cleanup on component unmount
  useEffect(() => {
    return () => {
      if (analysisInterval) {
        clearInterval(analysisInterval);
      }
    };
  }, [analysisInterval]);

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
          <div className="webcam-section">
            <div className="webcam-card">
              <div className="webcam-container">
                {isStreaming ? (
                  <Webcam
                    ref={webcamRef}
                    audio={false}
                    screenshotFormat="image/jpeg"
                    videoConstraints={videoConstraints}
                    onUserMediaError={handleUserMediaError}
                    onUserMedia={handleWebcamReady}
                    className="webcam-feed"
                  />
                ) : (
                  <div className="webcam-placeholder">
                    <div className="placeholder-icon">📹</div>
                    <p>Webcam feed will appear here</p>
                  </div>
                )}
                
                {isAnalyzing && (
                  <div className="analyzing-overlay">
                    <div className="analyzing-spinner"></div>
                    <span>Analyzing...</span>
                  </div>
                )}
                
                {isStreaming && !webcamReady && (
                  <div className="analyzing-overlay">
                    <div className="analyzing-spinner"></div>
                    <span>Starting webcam...</span>
                  </div>
                )}
              </div>

              <div className="webcam-controls">
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
          </div>
          
          <div className="results-section">
            <div className="results-card">
              <h3 className="results-title">Analysis Results</h3>
              
              {error && (
                <div className="error-message">
                  <div className="error-icon">⚠️</div>
                  <p>{error}</p>
                  <button onClick={() => setError(null)} className="btn btn-secondary btn-sm">
                    Dismiss
                  </button>
                </div>
              )}

              {prediction && !error && (
                <div className="analysis-results">
                  <div className={`result-card ${prediction.behavior?.toLowerCase() === 'aggressive' ? 'aggressive' : 'non-aggressive'}`}>
                    <div className={`result-header ${prediction.behavior?.toLowerCase() === 'aggressive' ? 'aggressive' : 'non-aggressive'}`}>
                      <div className="result-icon">
                        {prediction.error ? '❌' :
                         prediction.behavior?.toLowerCase() === 'aggressive' ? '😠' : 
                         prediction.behavior?.toLowerCase() === 'non-aggressive' ? '😌' : '🤔'}
                      </div>
                      <div className="result-info">
                        <div className="result-label">Behavior Classification</div>
                        <div className="result-value">
                          {prediction.behavior}
                        </div>
                      </div>
                    </div>
                    
                    {prediction.confidence > 0 && !prediction.error && (
                      <div className="confidence-section">
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

                    {prediction.reason && (
                      <div className="reason-section">
                        <div className="reason-label">Analysis:</div>
                        <div className="reason-text">{prediction.reason}</div>
                      </div>
                    )}

                    {prediction.detections && prediction.detections.length > 0 && (
                      <div className="detections-section">
                        <div className="detections-label">Objects Detected:</div>
                        <div className="detections-list">
                          {prediction.detections.map((detection, index) => (
                            <div key={index} className="detection-item">
                              <span className="detection-class">{detection.class}</span>
                              <span className="detection-confidence">
                                {Math.round(detection.confidence * 100)}%
                              </span>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="analysis-meta">
                      <p><strong>Last updated:</strong> {prediction.timestamp}</p>
                      {prediction.dog_detected !== undefined && (
                        <p><strong>Dog detected:</strong> {prediction.dog_detected ? 'Yes' : 'No'}</p>
                      )}
                      {prediction.processing_time && (
                        <p><strong>Processing time:</strong> {prediction.processing_time.toFixed(3)}s</p>
                      )}
                      {prediction.error && prediction.errorMessage && (
                        <p className="error-detail"><strong>Error:</strong> {prediction.errorMessage}</p>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {!prediction && !error && isStreaming && (
                <div className="waiting-message">
                  <div className="waiting-icon">🔄</div>
                  <p>Waiting for analysis results...</p>
                  <small>Analysis starts automatically every 3 seconds</small>
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
        </div>

        <div className="info-section">
          <div className="info-card">
            <h4>How it works</h4>
            <ol>
              <li>Click "Start Live Feed" to access your camera</li>
              <li>Position your dog in front of the camera</li>
              <li>AI analyzes behavior every 3 seconds automatically</li>
              <li>View real-time predictions and confidence scores</li>
            </ol>
          </div>
          
          <div className="info-card">
            <h4>Tips for best results</h4>
            <ul>
              <li>🎯 Ensure your dog is clearly visible in the frame</li>
              <li>💡 Use good lighting conditions</li>
              <li>📐 Keep the camera steady for best analysis</li>
              <li>🐕 Single dog in frame works best</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default LiveFeedPage;
