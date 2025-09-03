import React, { useState, useRef } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './AnalysisPage.css';

// Mock data for demonstration
const generateMockData = () => {
  const data = [];
  for (let i = 0; i < 100; i++) {
    data.push({
      frame: i,
      behavior: Math.random() > 0.7 ? 1 : 0, // 30% chance of aggressive behavior
      timestamp: i * 0.033 // Assuming 30 FPS
    });
  }
  return data;
};

const AnalysisPage = () => {
  const [selectedVideo, setSelectedVideo] = useState(null);
  const [videoPreview, setVideoPreview] = useState(null);
  const [analysisData, setAnalysisData] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisComplete, setAnalysisComplete] = useState(false);
  const fileInputRef = useRef(null);

  const handleVideoUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedVideo(file);
      
      // Create video preview URL
      const videoURL = URL.createObjectURL(file);
      setVideoPreview(videoURL);
      
      // Reset analysis state
      setAnalysisComplete(false);
      setAnalysisData([]);
    }
  };

  const startAnalysis = () => {
    if (!selectedVideo) return;
    
    setIsAnalyzing(true);
    
    // Simulate analysis process
    setTimeout(() => {
      const mockData = generateMockData();
      setAnalysisData(mockData);
      setIsAnalyzing(false);
      setAnalysisComplete(true);
    }, 3000);
  };

  const resetAnalysis = () => {
    setSelectedVideo(null);
    setVideoPreview(null);
    setAnalysisData([]);
    setAnalysisComplete(false);
    setIsAnalyzing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  const getAnalysisSummary = () => {
    if (!analysisData.length) return { calm: 0, aggressive: 0, total: 0 };
    
    const aggressive = analysisData.filter(d => d.behavior === 1).length;
    const calm = analysisData.length - aggressive;
    
    return {
      calm,
      aggressive,
      total: analysisData.length,
      aggressivePercentage: ((aggressive / analysisData.length) * 100).toFixed(1),
      calmPercentage: ((calm / analysisData.length) * 100).toFixed(1)
    };
  };

  const summary = getAnalysisSummary();

  return (
    <div className="analysis-page">
      <div className="container">
        <div className="page-header">
          <h1>Video Analysis</h1>
          <p>Upload a video to analyze dog behavior patterns</p>
        </div>

        {!selectedVideo ? (
          <div className="upload-section">
            <div className="upload-area">
              <div className="upload-content">
                <div className="upload-icon">📹</div>
                <h3>Select a video file</h3>
                <p>Supported formats: MP4, AVI, MOV</p>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="video/*"
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
            <div className="analysis-grid">
              <div className="video-section">
                <div className="card">
                  <div className="card-header">
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
                </div>
              </div>

              <div className="results-section">
                <div className="card">
                  <h3>Detection Results</h3>
                  {!analysisComplete && !isAnalyzing && (
                    <div className="analysis-placeholder">
                      <p>Click "Start Analysis" to begin processing the video.</p>
                      <button onClick={startAnalysis} className="btn btn-success">
                        Start Analysis
                      </button>
                    </div>
                  )}

                  {isAnalyzing && (
                    <div className="analysis-loading">
                      <div className="loader"></div>
                      <p>Analyzing video... This may take a few moments.</p>
                      <div className="progress-steps">
                        <div className="step active">🎯 Detecting dogs</div>
                        <div className="step active">🧠 Analyzing behavior</div>
                        <div className="step">📊 Generating report</div>
                      </div>
                    </div>
                  )}

                  {analysisComplete && (
                    <div className="analysis-results">
                      <div className="summary-cards">
                        <div className="summary-card calm">
                          <div className="summary-icon">😌</div>
                          <div className="summary-data">
                            <div className="summary-number">{summary.calm}</div>
                            <div className="summary-label">Calm Frames</div>
                            <div className="summary-percentage">{summary.calmPercentage}%</div>
                          </div>
                        </div>
                        <div className="summary-card aggressive">
                          <div className="summary-icon">😠</div>
                          <div className="summary-data">
                            <div className="summary-number">{summary.aggressive}</div>
                            <div className="summary-label">Aggressive Frames</div>
                            <div className="summary-percentage">{summary.aggressivePercentage}%</div>
                          </div>
                        </div>
                      </div>

                      <div className="real-time-status">
                        <h4>Current Status: <span className="status-calm">Calm Behavior Detected</span></h4>
                        <p>Last updated: {new Date().toLocaleTimeString()}</p>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>

            {analysisComplete && (
              <div className="chart-section">
                <div className="card">
                  <h3>Behavior Timeline</h3>
                  <p>Behavior detection over time (0 = Calm, 1 = Aggressive)</p>
                  <div className="chart-container">
                    <ResponsiveContainer width="100%" height={300}>
                      <LineChart data={analysisData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis 
                          dataKey="frame" 
                          label={{ value: 'Frame Number', position: 'insideBottom', offset: -5 }}
                        />
                        <YAxis 
                          domain={[-0.1, 1.1]}
                          ticks={[0, 1]}
                          label={{ value: 'Behavior', angle: -90, position: 'insideLeft' }}
                        />
                        <Tooltip 
                          formatter={(value) => [value === 1 ? 'Aggressive' : 'Calm', 'Behavior']}
                          labelFormatter={(frame) => `Frame: ${frame}`}
                        />
                        <Line 
                          type="stepAfter" 
                          dataKey="behavior" 
                          stroke="#007bff" 
                          strokeWidth={2}
                          dot={false}
                        />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AnalysisPage;
