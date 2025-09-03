import React, { useState, useRef } from 'react';
import './AnalysisPage.css';
import { analyzeImage } from '../../api';

const AnalysisPage = () => {
  const [selectedImage, setSelectedImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [error, setError] = useState(null);
  const fileInputRef = useRef(null);

  const handleImageUpload = (event) => {
    const file = event.target.files[0];
    if (file) {
      setSelectedImage(file);
      
      // Create image preview URL
      const imageURL = URL.createObjectURL(file);
      setImagePreview(imageURL);
      
      // Reset analysis state
      setAnalysisResult(null);
      setError(null);
      
      // Auto-start analysis
      analyzeImageFile(file);
    }
  };

  const analyzeImageFile = async (file) => {
    setIsAnalyzing(true);
    setError(null);
    
    try {
      const result = await analyzeImage(file);
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message);
      console.error('Analysis failed:', err);
    } finally {
      setIsAnalyzing(false);
    }
  };

  const resetAnalysis = () => {
    setSelectedImage(null);
    setImagePreview(null);
    setAnalysisResult(null);
    setError(null);
    setIsAnalyzing(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
    }
  };

  return (
    <div className="analysis-page">
      <div className="analysis-container">
        <div className="page-header">
          <h1 className="page-title">� Image Analysis</h1>
          <p className="page-subtitle">
            Upload an image to analyze dog behavior using AI
          </p>
        </div>

        {!selectedImage ? (
          <div className="upload-section">
            <div className="upload-card">
              <div className="upload-content">
                <div className="upload-icon">�</div>
                <h3>Select an image file</h3>
                <p>Supported formats: JPEG, PNG, WebP (max 10MB)</p>
                <input
                  type="file"
                  ref={fileInputRef}
                  accept="image/jpeg,image/jpg,image/png,image/webp"
                  onChange={handleImageUpload}
                  className="file-input"
                  id="image-upload"
                />
                <label htmlFor="image-upload" className="btn btn-primary">
                  Choose Image File
                </label>
              </div>
            </div>
          </div>
        ) : (
          <div className="analysis-content">
            <div className="image-section">
              <div className="image-card">
                <div className="image-header">
                  <h3>Image Preview</h3>
                  <button onClick={resetAnalysis} className="btn btn-secondary btn-sm">
                    Upload New Image
                  </button>
                </div>
                <div className="image-container">
                  <img 
                    src={imagePreview}
                    alt="Selected for analysis"
                    className="preview-image"
                  />
                </div>
                <div className="image-info">
                  <p><strong>File:</strong> {selectedImage.name}</p>
                  <p><strong>Size:</strong> {(selectedImage.size / (1024 * 1024)).toFixed(2)} MB</p>
                  <p><strong>Type:</strong> {selectedImage.type}</p>
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

                {isAnalyzing && (
                  <div className="loading-message">
                    <div className="loading-spinner"></div>
                    <p>Analyzing image...</p>
                    <small>This may take a few moments</small>
                  </div>
                )}

                {analysisResult && !error && (
                  <div className="analysis-results">
                    <div className={`result-card ${analysisResult.prediction?.toLowerCase() === 'aggressive' ? 'aggressive' : 'non-aggressive'}`}>
                      <div className={`result-header ${analysisResult.prediction?.toLowerCase() === 'aggressive' ? 'aggressive' : 'non-aggressive'}`}>
                        <div className="result-icon">
                          {analysisResult.prediction?.toLowerCase() === 'aggressive' ? '😠' : '😌'}
                        </div>
                        <div className="result-info">
                          <div className="result-label">Behavior Classification</div>
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
                        {analysisResult.processing_time && (
                          <p><strong>Processing time:</strong> {analysisResult.processing_time.toFixed(2)}s</p>
                        )}
                      </div>
                    </div>

                    {analysisResult.bounding_box && (
                      <div className="bounding-box-info">
                        <h4>Detection Details</h4>
                        <p>✅ Dog detected in image</p>
                        <p><strong>Location:</strong> {JSON.stringify(analysisResult.bounding_box)}</p>
                      </div>
                    )}
                  </div>
                )}

                {!analysisResult && !isAnalyzing && !error && selectedImage && (
                  <div className="no-data-message">
                    <div className="no-data-icon">🔍</div>
                    <p>Processing image...</p>
                    <small>Analysis starts automatically when you upload an image</small>
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
              <li>Upload an image containing a dog</li>
              <li>AI automatically analyzes the behavior</li>
              <li>Get instant classification and confidence score</li>
              <li>See bounding box if dog is detected</li>
            </ol>
          </div>
          
          <div className="info-card">
            <h4>Tips for best results</h4>
            <ul>
              <li>🎯 Ensure the dog is clearly visible</li>
              <li>� Use good lighting conditions</li>
              <li>� Higher resolution images work better</li>
              <li>� Single dog per image is optimal</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalysisPage;
