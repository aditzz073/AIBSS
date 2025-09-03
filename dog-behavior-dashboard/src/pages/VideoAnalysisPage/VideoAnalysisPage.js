import React, { useState, useRef } from 'react';
import './VideoAnalysisPage.css';
import { analyzeVideo } from '../../api';

const VideoAnalysisPage = () => {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedVideo(file);
      
      // Create video preview URL
      const videoURL = URL.createObjectURL(file);
      setVideoPreview(videoURL);
      
      // Reset analysis state
      setAnalysisResult(null);
      setError(null);
    }
  };

  const startAnalysis = async () => {
    if (!selectedVideo) return;
    
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await analyzeVideo(selectedVideo);
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message);
      console.error('Analysis failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedVideo(null);
    setVideoPreview(null);
    setAnalysisResult(null);
    setError(null);
    setIsAnalyzing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (videoPreview) {
      URL.revokeObjectURL(videoPreview);
    }
  };

  return (
    <div className="video-analysis-page">
      <div className="analysis-container">
        <div className="page-header">
          <h1 className="page-title">🎬 Video Analysis</h1>
          <p className="page-subtitle">
            Upload a video to analyze dog behavior patterns over time
          </p>
        </div>

        {!selectedVideo ? (
          <div className="upload-section">
            <div className="upload-card">
              <div className="upload-content">
                <div className="upload-icon">📹</div>
                <h3>Select a video file</h3>
                <p>Supported formats: MP4, AVI, MOV (max 100MB)</p>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="video/mp4,video/avi,video/mov,video/quicktime"
                  onChange={handleVideoUpload}
                  className="file-input"
                  id="video-upload"
                />
                <label htmlFor="video-upload" className="btn btn-primary">
                  Choose Video File
                </label>
              </div>
            </div>
          </div>
        ) : (
          <div className="analysis-content">
            <div className="video-section">
              <div className="video-card">
                <div className="video-header">
                  <h3>Video Preview</h3>
                  <button onClick={resetAnalysis} className="btn btn-secondary btn-sm">
                    Upload New Video
                  </button>
                </div>
                <div className="video-container">
                  <video 
                    controls 
                    width="100%" 
                    height="300"
                    src={videoPreview}
                  >
                    Your browser does not support the video tag.
                  </video>
                </div>
                <div className="video-info">
                  <p><strong>File:</strong> {selectedVideo.name}</p>
                  <p><strong>Size:</strong> {(selectedVideo.size / (1024 * 1024)).toFixed(2)} MB</p>
                </div>
                
                {!analysisResult && !isAnalyzing && (
                  <div className="analysis-actions">
                    <button 
                      onClick={startAnalysis} 
                      className="btn btn-primary"
                      disabled={isAnalyzing}
                    >
                      🔍 Start Analysis
                    </button>
                  </div>
                )}
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

                {isAnalyzing && (
                  <div className="loading-message">
                    <div className="loading-spinner"></div>
                    <p>Analyzing video...</p>
                    <small>This may take a few moments depending on video length</small>
                  </div>
                )}

                {analysisResult && !error && (
                  <div className="analysis-results">
                    <div className="result-card">
                      <div className={`result-header ${analysisResult.prediction?.toLowerCase() === 'aggressive' ? 'aggressive' : 'non-aggressive'}`}>
                        <div className="result-icon">
                          {analysisResult.prediction?.toLowerCase() === 'aggressive' ? '😠' : '😌'}
                        </div>
                        <div className="result-info">
                          <div className="result-label">Overall Behavior</div>
                          <div className="result-value">
                            {analysisResult.prediction || 'Unknown'}
                          </div>
                        </div>
                      </div>
                      
                      {analysisResult.confidence && (
                        <div className="confidence-section">
                          <div className="confidence-label">
                            Confidence: {Math.round(analysisResult.confidence * 100)}%
                          </div>
                          <div className="confidence-bar">
                            <div 
                              className="confidence-fill"
                              style={{ width: `${analysisResult.confidence * 100}%` }}
                            ></div>
                          </div>
                        </div>
                      )}

                      <div className="analysis-meta">
                        <p><strong>Analysis completed:</strong> {new Date().toLocaleString()}</p>
                        {analysisResult.frames_analyzed && (
                          <p><strong>Frames analyzed:</strong> {analysisResult.frames_analyzed}</p>
                        )}
                        {analysisResult.duration && (
                          <p><strong>Video duration:</strong> {analysisResult.duration}s</p>
                        )}
                      </div>
                    </div>

                    {analysisResult.detections && analysisResult.detections.length > 0 && (
                      <div className="detections-summary">
                        <h4>Detection Summary</h4>
                        <div className="detection-stats">
                          <div className="stat-card">
                            <div className="stat-number">
                              {analysisResult.detections.filter(d => d.behavior === 'aggressive').length}
                            </div>
                            <div className="stat-label">Aggressive Frames</div>
                          </div>
                          <div className="stat-card">
                            <div className="stat-number">
                              {analysisResult.detections.filter(d => d.behavior === 'non-aggressive').length}
                            </div>
                            <div className="stat-label">Non-Aggressive Frames</div>
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                )}

                {!analysisResult && !isAnalyzing && !error && (
                  <div className="no-data-message">
                    <div className="no-data-icon">📊</div>
                    <p>No analysis data yet</p>
                    <small>Click "Start Analysis" to begin processing the video</small>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        <div className="info-section">
          <div className="info-card">
            <h4>How it works</h4>
            <ol>
              <li>Upload a video file containing dog behavior</li>
              <li>Click "Start Analysis" to begin processing</li>
              <li>AI analyzes frames for behavior patterns</li>
              <li>View overall behavior classification and confidence</li>
            </ol>
          </div>
          
          <div className="info-card">
            <h4>Tips for best results</h4>
            <ul>
              <li>🎯 Ensure the dog is clearly visible in the video</li>
              <li>📹 Use good lighting and stable footage</li>
              <li>⏱️ Shorter videos (under 1 minute) process faster</li>
              <li>📱 MP4 format generally works best</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default VideoAnalysisPage;
