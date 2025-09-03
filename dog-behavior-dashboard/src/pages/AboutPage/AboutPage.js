import React from 'react';
import './AboutPage.css';

const AboutPage = () => {
  const features = [
    {
      id: 1,
      icon: "🎯",
      title: "Precise AI Detection",
      description: "Advanced YOLO pose detection combined with intelligent classification algorithms for accurate behavior analysis."
    },
    {
      id: 2,
      icon: "⚡",
      title: "Real-time Processing",
      description: "Lightning-fast analysis that processes video feeds instantly, providing immediate insights into dog behavior."
    },
    {
      id: 3,
      icon: "🧠",
      title: "Smart Classification",
      description: "Machine learning classifier trained to distinguish between calm and aggressive behaviors with high accuracy."
    },
    {
      id: 4,
      icon: "📊",
      title: "Comprehensive Analytics",
      description: "Detailed behavioral insights with visual analytics and historical pattern tracking for better understanding."
    },
    {
      id: 5,
      icon: "🔒",
      title: "Privacy Focused",
      description: "Your data remains secure with local processing options and privacy-first architecture design."
    },
    {
      id: 6,
      icon: "🌐",
      title: "Multi-platform",
      description: "Works across different devices and platforms, from mobile apps to web browsers and desktop applications."
    }
  ];

  const workflowSteps = [
    {
      number: "01",
      title: "Video Input",
      description: "Upload video files or connect live camera feeds to start the analysis process",
      icon: "📹",
      placeholder: "[Video Upload Interface Placeholder]"
    },
    {
      number: "02", 
      title: "YOLO Pose Detection",
      description: "Advanced computer vision identifies and tracks dog poses in real-time with high precision",
      icon: "🎯",
      placeholder: "[Pose Detection Visualization Placeholder]"
    },
    {
      number: "03",
      title: "Behavior Classification", 
      description: "AI classifier analyzes pose data to determine aggressive vs calm behavioral states",
      icon: "🧠",
      placeholder: "[Classification Results Placeholder]"
    },
    {
      number: "04",
      title: "Smart Insights",
      description: "Generate detailed reports and actionable insights for better dog behavior understanding",
      icon: "📊",
      placeholder: "[Analytics Dashboard Placeholder]"
    }
  ];

  const roadmapItems = [
    {
      phase: "Phase 1",
      title: "Enhanced AI Models",
      description: "Improved pose detection accuracy and expanded behavior classification categories",
      status: "In Progress"
    },
    {
      phase: "Phase 2", 
      title: "Mobile App Integration",
      description: "Native iOS and Android apps with offline processing capabilities",
      status: "Planned"
    },
    {
      phase: "Phase 3",
      title: "Multi-Dog Analysis",
      description: "Advanced algorithms to analyze behavior in multi-dog environments",
      status: "Research"
    },
    {
      phase: "Phase 4",
      title: "Predictive Analytics",
      description: "Behavioral pattern prediction and early warning systems",
      status: "Concept"
    }
  ];

  return (
    <div className="about-page">
      {/* Hero Section */}
      <section className="hero-section">
        <div className="hero-container">
          <div className="hero-left">
            <h1 className="hero-title">
              About Dog Behavior Dashboard
            </h1>
            <p className="hero-subtitle">
              An AI-powered platform that revolutionizes canine behavior analysis through advanced computer vision and machine learning. Unlike basic emotion detectors, our system provides precise, actionable insights into dog behavior patterns.
            </p>
            
            <div className="hero-stats">
              <div className="hero-stat">
                <div className="stat-number">94.7%</div>
                <div className="stat-label">Accuracy</div>
              </div>
              <div className="hero-stat">
                <div className="stat-number">Real-time</div>
                <div className="stat-label">Detection</div>
              </div>
              <div className="hero-stat">
                <div className="stat-number">AI-Powered</div>
                <div className="stat-label">Analysis</div>
              </div>
            </div>
          </div>
          
          <div className="hero-right">
            <div className="hero-image-container">
              <div className="background-shape"></div>
              <div className="dog-analysis-visual">
                <div className="main-visual">
                  <div className="visual-placeholder">
                    <span>🐕‍🦺</span>
                    <p>AI Analysis</p>
                  </div>
                </div>
                <div className="floating-indicator behavior-calm">
                  <span>😌</span>
                  <p>Calm</p>
                </div>
                <div className="floating-indicator behavior-alert">
                  <span>⚠️</span>
                  <p>Alert</p>
                </div>
                <div className="floating-indicator behavior-active">
                  <span>⚡</span>
                  <p>Active</p>
                </div>
                <div className="floating-element chart">📊</div>
                <div className="floating-element brain">🧠</div>
                <div className="floating-element target">🎯</div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Key Features Section */}
      <section className="features-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Key Features</h2>
            <p className="section-subtitle">
              Why Dog Behavior Dashboard stands out from traditional behavior monitoring solutions
            </p>
          </div>
          
          <div className="features-grid">
            {features.map((feature) => (
              <div key={feature.id} className="feature-card">
                <div className="feature-icon">{feature.icon}</div>
                <h3 className="feature-title">{feature.title}</h3>
                <p className="feature-description">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works Section */}
      <section className="workflow-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">How It Works</h2>
            <p className="section-subtitle">
              Our intelligent system processes dog behavior through four sophisticated steps
            </p>
          </div>

          <div className="workflow-steps">
            {workflowSteps.map((step, index) => (
              <div key={index} className="workflow-step">
                <div className="step-number">{step.number}</div>
                <div className="step-content">
                  <div className="step-header">
                    <div className="step-icon">{step.icon}</div>
                    <h3 className="step-title">{step.title}</h3>
                  </div>
                  <p className="step-description">{step.description}</p>
                  <div className="step-placeholder">
                    <div className="placeholder-content">
                      <span className="placeholder-icon">{step.icon}</span>
                      <p>{step.placeholder}</p>
                    </div>
                  </div>
                </div>
                {index < workflowSteps.length - 1 && <div className="step-connector"></div>}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Benefits Section */}
      <section className="benefits-section">
        <div className="container">
          <div className="benefits-content">
            <div className="benefits-left">
              <h2 className="benefits-title">
                Why Choose Our Solution?
              </h2>
              <div className="benefits-list">
                <div className="benefit-item">
                  <div className="benefit-icon">✨</div>
                  <div className="benefit-content">
                    <h3>Superior Accuracy</h3>
                    <p>Advanced YOLO architecture delivers 94.7% accuracy in behavior classification, significantly outperforming traditional methods.</p>
                  </div>
                </div>
                <div className="benefit-item">
                  <div className="benefit-icon">⚡</div>
                  <div className="benefit-content">
                    <h3>Real-time Analysis</h3>
                    <p>Process 30+ frames per second with instant behavioral state detection and immediate alert capabilities.</p>
                  </div>
                </div>
                <div className="benefit-item">
                  <div className="benefit-icon">🎯</div>
                  <div className="benefit-content">
                    <h3>Actionable Insights</h3>
                    <p>Beyond detection - get comprehensive behavior patterns, trends, and recommendations for better pet care.</p>
                  </div>
                </div>
              </div>
            </div>
            <div className="benefits-right">
              <div className="benefits-image-placeholder">
                <div className="placeholder-content">
                  <span className="placeholder-icon">📊</span>
                  <p>[Benefits Visualization Placeholder]</p>
                  <small>Replace with: Comparison chart or benefits infographic</small>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Future Scope Section */}
      <section className="roadmap-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Future Scope & Roadmap</h2>
            <p className="section-subtitle">
              Our vision for the future of canine behavior analysis and monitoring
            </p>
          </div>

          <div className="roadmap-timeline">
            {roadmapItems.map((item, index) => (
              <div key={index} className="roadmap-item">
                <div className="roadmap-marker">
                  <div className="marker-dot"></div>
                  <div className={`marker-status ${item.status.toLowerCase().replace(' ', '-')}`}>
                    {item.status}
                  </div>
                </div>
                <div className="roadmap-content">
                  <div className="roadmap-phase">{item.phase}</div>
                  <h3 className="roadmap-title">{item.title}</h3>
                  <p className="roadmap-description">{item.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Technology Stack */}
      <section className="technology-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Powered by Advanced Technology</h2>
          </div>
          
          <div className="tech-stack">
            <div className="tech-category">
              <h3>Computer Vision</h3>
              <div className="tech-items">
                <span className="tech-item">YOLOv8</span>
                <span className="tech-item">OpenCV</span>
                <span className="tech-item">Pose Estimation</span>
              </div>
            </div>
            <div className="tech-category">
              <h3>Machine Learning</h3>
              <div className="tech-items">
                <span className="tech-item">Random Forest</span>
                <span className="tech-item">TensorFlow</span>
                <span className="tech-item">PyTorch</span>
              </div>
            </div>
            <div className="tech-category">
              <h3>Frontend</h3>
              <div className="tech-items">
                <span className="tech-item">React.js</span>
                <span className="tech-item">WebRTC</span>
                <span className="tech-item">D3.js</span>
              </div>
            </div>
            <div className="tech-category">
              <h3>Infrastructure</h3>
              <div className="tech-items">
                <span className="tech-item">Node.js</span>
                <span className="tech-item">Docker</span>
                <span className="tech-item">AWS</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Stats */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">94.7%</div>
              <div className="stat-label">Detection Accuracy</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">30+</div>
              <div className="stat-label">FPS Processing</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">15,000+</div>
              <div className="stat-label">Training Videos</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">&lt;50ms</div>
              <div className="stat-label">Response Time</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
