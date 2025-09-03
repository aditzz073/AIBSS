import React from 'react';
import { Link } from 'react-router-dom';
import './HomePage.css';

const HomePage = () => {
  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-left">
            <h1 className="hero-title">
              AI-powered Dog Behavior Detection.
            </h1>
            <p className="hero-subtitle">
              Advanced machine learning technology to detect and analyze dog behavior patterns in real-time. Keep your pets safe with intelligent monitoring.
            </p>
            
            <div className="hero-search">
              <div className="search-container">
                <svg className="search-icon" width="20" height="20" viewBox="0 0 24 24" fill="none">
                  <path d="m21 21-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607z" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <input 
                  type="text" 
                  placeholder="Search for dog breeds, behaviors, or training tips..." 
                  className="search-input"
                />
                <button className="search-button">Search</button>
              </div>
            </div>
            
            <div className="hero-buttons">
              <Link to="/analysis" className="btn btn-primary">
                <span>🎥</span>
                Start Analysis
              </Link>
              <Link to="/dashboard" className="btn btn-secondary">
                <span>📊</span>
                View Dashboard
              </Link>
            </div>
          </div>
          
          <div className="hero-right">
            <div className="hero-image-container">
              <div className="background-shape"></div>
              <div className="dog-illustrations">
                <div className="dog-image main-dog">
                  <div className="dog-placeholder">
                    <span>🐕</span>
                    <p>Happy Dog</p>
                  </div>
                </div>
                <div className="dog-image small-dog-1">
                  <div className="dog-placeholder">
                    <span>🐾</span>
                  </div>
                </div>
                <div className="dog-image small-dog-2">
                  <div className="dog-placeholder">
                    <span>🦴</span>
                  </div>
                </div>
                <div className="floating-element heart">💖</div>
                <div className="floating-element star">⭐</div>
                <div className="floating-element paw">🐾</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="stats-section">
        <div className="stats-container">
          <div className="stat-item">
            <div className="stat-number">98.5%</div>
            <div className="stat-label">Accuracy</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">10,000+</div>
            <div className="stat-label">Videos Processed</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">Real-time</div>
            <div className="stat-label">Detection</div>
          </div>
        </div>
      </section>

      {/* Features Preview */}
      <section className="features-preview">
        <div className="features-container">
          <h2 className="features-title">Why Choose DogCare AI?</h2>
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">🎯</div>
              <h3>Precise Detection</h3>
              <p>Advanced AI algorithms ensure accurate behavior classification with minimal false positives.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">⚡</div>
              <h3>Real-time Monitoring</h3>
              <p>Instant alerts and live analysis keep you informed about your dog's behavior patterns.</p>
            </div>
            <div className="feature-card">
              <div className="feature-icon">�</div>
              <h3>Easy to Use</h3>
              <p>Simple interface designed for pet owners, trainers, and veterinarians alike.</p>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default HomePage;
