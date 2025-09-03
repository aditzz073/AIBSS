import React from 'react';
import './AboutPage.css';

const AboutPage = () => {
  const teamMembers = [
    {
      id: 1,
      name: "Dr. Sarah Johnson",
      role: "AI Research Lead",
      description: "PhD in Computer Vision with expertise in deep learning and behavioral analysis",
      avatar: "👩‍🔬"
    },
    {
      id: 2,
      name: "Michael Chen",
      role: "Machine Learning Engineer",
      description: "Specializes in YOLOv8 implementation and model optimization",
      avatar: "👨‍💻"
    },
    {
      id: 3,
      name: "Emily Rodriguez",
      role: "Data Scientist",
      description: "Expert in Random Forest algorithms and statistical analysis",
      avatar: "👩‍💼"
    },
    {
      id: 4,
      name: "David Park",
      role: "Full Stack Developer",
      description: "Frontend and backend development, system architecture design",
      avatar: "👨‍🎨"
    }
  ];

  return (
    <div className="about-page">
      <div className="container">
        {/* Header Section */}
        <div className="page-header">
          <h1>About Dog Behavior Detection</h1>
          <p className="lead">
            Advanced AI system for real-time dog behavior analysis using 
            state-of-the-art computer vision and machine learning techniques.
          </p>
        </div>

        {/* How It Works Section */}
        <div className="how-it-works-section">
          <h2 className="section-title">How the System Works</h2>
          
          <div className="process-flow">
            <div className="process-step">
              <div className="step-number">1</div>
              <div className="step-content">
                <h3>Video Input</h3>
                <p>Upload video files or connect to live camera feeds for real-time analysis</p>
                <div className="step-icon">📹</div>
              </div>
            </div>

            <div className="process-arrow">→</div>

            <div className="process-step">
              <div className="step-number">2</div>
              <div className="step-content">
                <h3>YOLOv8 Detection</h3>
                <p>Advanced object detection model identifies and tracks dogs in each frame</p>
                <div className="step-icon">🎯</div>
              </div>
            </div>

            <div className="process-arrow">→</div>

            <div className="process-step">
              <div className="step-number">3</div>
              <div className="step-content">
                <h3>Feature Extraction</h3>
                <p>Extract behavioral features including posture, movement patterns, and body language</p>
                <div className="step-icon">🔍</div>
              </div>
            </div>

            <div className="process-arrow">→</div>

            <div className="process-step">
              <div className="step-number">4</div>
              <div className="step-content">
                <h3>Random Forest Classification</h3>
                <p>Machine learning classifier analyzes features to determine calm vs aggressive behavior</p>
                <div className="step-icon">🧠</div>
              </div>
            </div>
          </div>
        </div>

        {/* Technical Details */}
        <div className="technical-section">
          <div className="tech-grid">
            <div className="tech-card">
              <h3>🎯 YOLOv8 Object Detection</h3>
              <ul>
                <li>Real-time object detection and tracking</li>
                <li>High accuracy dog identification</li>
                <li>Optimized for video processing</li>
                <li>Supports multiple dog detection</li>
              </ul>
            </div>

            <div className="tech-card">
              <h3>🌳 Random Forest Classifier</h3>
              <ul>
                <li>Ensemble learning for robust predictions</li>
                <li>Handles complex behavioral patterns</li>
                <li>Resistant to overfitting</li>
                <li>Interpretable feature importance</li>
              </ul>
            </div>

            <div className="tech-card">
              <h3>📊 Feature Engineering</h3>
              <ul>
                <li>Pose estimation and body language analysis</li>
                <li>Movement velocity and acceleration tracking</li>
                <li>Temporal pattern recognition</li>
                <li>Multi-frame context integration</li>
              </ul>
            </div>

            <div className="tech-card">
              <h3>⚡ Performance Optimization</h3>
              <ul>
                <li>GPU acceleration for real-time processing</li>
                <li>Efficient memory management</li>
                <li>Scalable architecture design</li>
                <li>Cloud deployment ready</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Applications Section */}
        <div className="applications-section">
          <h2 className="section-title">Applications</h2>
          <div className="applications-grid">
            <div className="application-card">
              <div className="app-icon">🏥</div>
              <h3>Veterinary Clinics</h3>
              <p>Monitor dog stress levels and aggressive behavior during medical examinations and treatments.</p>
            </div>

            <div className="application-card">
              <div className="app-icon">🏠</div>
              <h3>Pet Owners</h3>
              <p>Track your dog's behavior patterns at home to better understand their emotional states.</p>
            </div>

            <div className="application-card">
              <div className="app-icon">🎓</div>
              <h3>Dog Training</h3>
              <p>Analyze training sessions to optimize behavioral modification techniques and track progress.</p>
            </div>

            <div className="application-card">
              <div className="app-icon">🏢</div>
              <h3>Animal Shelters</h3>
              <p>Assess dog temperament for better adoption matching and staff safety protocols.</p>
            </div>
          </div>
        </div>

        {/* Team Section */}
        <div className="team-section">
          <h2 className="section-title">Meet Our Team</h2>
          <div className="team-grid">
            {teamMembers.map((member) => (
              <div key={member.id} className="team-card">
                <div className="team-avatar">{member.avatar}</div>
                <div className="team-info">
                  <h3>{member.name}</h3>
                  <h4>{member.role}</h4>
                  <p>{member.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stats Section */}
        <div className="stats-section">
          <h2 className="section-title">System Performance</h2>
          <div className="performance-stats">
            <div className="stat-item">
              <div className="stat-number">94.7%</div>
              <div className="stat-label">Accuracy Rate</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">30 FPS</div>
              <div className="stat-label">Real-time Processing</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">10,000+</div>
              <div className="stat-label">Training Videos</div>
            </div>
            <div className="stat-item">
              <div className="stat-number">0.05s</div>
              <div className="stat-label">Response Time</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutPage;
