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
              <Link to="/live" className="btn btn-secondary">
                <span>📹</span>
                Live Feed
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
    </div>
  );
};

export default HomePage;
