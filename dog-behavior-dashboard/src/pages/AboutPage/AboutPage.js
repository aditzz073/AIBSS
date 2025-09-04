import React from 'react';
import './AboutPage.css';

const AboutPage = () => {
  const features = [
    {
      id: 1,
      icon: "🎯",
      title: "Dual-Model AI Detection",
      description: "Advanced YOLOv8 architecture with specialized models: one for static image analysis with pose estimation, and another for real-time video processing with object detection."
    },
    {
      id: 2,
      icon: "⚡",
      title: "Real-time Video Analysis",
      description: "Lightning-fast video processing with frame-by-frame analysis, majority vote algorithms, and comprehensive behavioral pattern detection."
    },
    {
      id: 3,
      icon: "🧠",
      title: "Multi-Class Recognition",
      description: "Intelligent classification system that detects 5 distinct classes: dog biting child, chasing dog, running child, child, and dog behaviors."
    },
    {
      id: 4,
      icon: "📊",
      title: "Interactive Analytics",
      description: "Beautiful heatmap visualization with OpenStreetMap integration, real-time statistics, and comprehensive behavioral insights dashboard."
    },
    {
      id: 5,
      icon: "🔒",
      title: "Local Processing",
      description: "Privacy-first architecture with local model inference, ensuring your data remains secure without external API dependencies."
    },
    {
      id: 6,
      icon: "🌐",
      title: "Full-Stack Solution",
      description: "Complete system with FastAPI backend, React frontend, live webcam integration, and cross-platform compatibility."
    }
  ];

  const workflowSteps = [
    {
      number: "01",
      title: "Video/Image Input",
      description: "Upload video files, images, or connect live camera feeds through our modern React interface",
      icon: "📹",
      placeholder: "[Multi-format Input Interface]"
    },
    {
      number: "02", 
      title: "Dual-Model Processing",
      description: "Route to specialized YOLOv8 models: pose estimation for images or object detection for videos/live feeds",
      icon: "🎯",
      placeholder: "[Intelligent Model Routing]"
    },
    {
      number: "03",
      title: "Behavioral Classification", 
      description: "Advanced algorithms analyze patterns and classify behaviors with confidence scoring and detailed reasoning",
      icon: "🧠",
      placeholder: "[Classification Results with Confidence]"
    },
    {
      number: "04",
      title: "Visual Analytics",
      description: "Interactive heatmaps, real-time statistics, and comprehensive dashboards for actionable insights",
      icon: "📊",
      placeholder: "[Interactive Analytics Dashboard]"
    }
  ];

  const roadmapItems = [
    {
      phase: "Phase 1 - Completed",
      title: "Dual-Model Architecture",
      description: "Successfully implemented specialized YOLOv8 models for image analysis and video processing with FastAPI backend",
      status: "Complete"
    },
    {
      phase: "Phase 2 - In Progress", 
      title: "Enhanced UI/UX",
      description: "Beautiful modern design with interactive heatmaps, real-time analytics, and responsive web interface",
      status: "Complete"
    },
    {
      phase: "Phase 3 - Planning",
      title: "YOLOv11 Migration",
      description: "Upgrade to latest YOLO architecture for improved accuracy and performance optimization",
      status: "Planned"
    },
    {
      phase: "Phase 4 - Future",
      title: "Advanced Analytics",
      description: "Predictive behavioral modeling, multi-dog scene analysis, and cloud deployment options",
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
              An AI-powered platform featuring dual YOLOv8 models for comprehensive canine behavior analysis. Our system combines static image analysis with pose estimation and real-time video processing for accurate behavioral detection and classification.
            </p>
            
            <div className="hero-stats">
              <div className="hero-stat">
                <div className="stat-number">Dual-AI</div>
                <div className="stat-label">Models</div>
              </div>
              <div className="hero-stat">
                <div className="stat-number">Real-time</div>
                <div className="stat-label">Processing</div>
              </div>
              <div className="hero-stat">
                <div className="stat-number">5 Classes</div>
                <div className="stat-label">Detection</div>
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
                Why Choose Our Dual-Model Solution?
              </h2>
              <div className="benefits-list">
                <div className="benefit-item">
                  <div className="benefit-icon">✨</div>
                  <div className="benefit-content">
                    <h3>Dual-Model Architecture</h3>
                    <p>Specialized YOLOv8 models optimized for different use cases: static image analysis with pose estimation and real-time video processing with object detection.</p>
                  </div>
                </div>
                <div className="benefit-item">
                  <div className="benefit-icon">⚡</div>
                  <div className="benefit-content">
                    <h3>Real-time Processing</h3>
                    <p>FastAPI backend processes video frames with sub-100ms latency, supporting live webcam feeds and batch video analysis with majority vote algorithms.</p>
                  </div>
                </div>
                <div className="benefit-item">
                  <div className="benefit-icon">🎯</div>
                  <div className="benefit-content">
                    <h3>Comprehensive Detection</h3>
                    <p>Advanced multi-class detection system identifies 5 distinct behaviors: dog biting child, chasing dog, running child, child, and dog with confidence scoring.</p>
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
              <h3>AI Models</h3>
              <div className="tech-items">
                <span className="tech-item">YOLOv8</span>
                <span className="tech-item">Ultralytics</span>
                <span className="tech-item">OpenCV</span>
                <span className="tech-item">NumPy</span>
              </div>
            </div>
            <div className="tech-category">
              <h3>Backend</h3>
              <div className="tech-items">
                <span className="tech-item">FastAPI</span>
                <span className="tech-item">Python 3.13</span>
                <span className="tech-item">Uvicorn</span>
                <span className="tech-item">Pillow</span>
              </div>
            </div>
            <div className="tech-category">
              <h3>Frontend</h3>
              <div className="tech-items">
                <span className="tech-item">React 19</span>
                <span className="tech-item">React Router</span>
                <span className="tech-item">Recharts</span>
                <span className="tech-item">React Webcam</span>
              </div>
            </div>
            <div className="tech-category">
              <h3>Visualization</h3>
              <div className="tech-items">
                <span className="tech-item">Leaflet.js</span>
                <span className="tech-item">OpenStreetMap</span>
                <span className="tech-item">Interactive Maps</span>
                <span className="tech-item">CSS3</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Current Implementation Status */}
      <section className="implementation-section">
        <div className="container">
          <div className="section-header">
            <h2 className="section-title">Current Implementation Status</h2>
            <p className="section-subtitle">
              Live system with fully operational components ready for use
            </p>
          </div>
          
          <div className="implementation-grid">
            <div className="implementation-card active">
              <div className="status-icon">✅</div>
              <h3>FastAPI Backend</h3>
              <p>Running on port 8001 with dual YOLOv8 models loaded and operational</p>
              <div className="status-badge operational">Operational</div>
            </div>
            
            <div className="implementation-card active">
              <div className="status-icon">✅</div>
              <h3>React Frontend</h3>
              <p>Modern React 19 interface with responsive design and interactive components</p>
              <div className="status-badge operational">Operational</div>
            </div>
            
            <div className="implementation-card active">
              <div className="status-icon">✅</div>
              <h3>Image Analysis</h3>
              <p>YOLOv8 + pose estimation model for static image behavioral analysis</p>
              <div className="status-badge operational">Operational</div>
            </div>
            
            <div className="implementation-card active">
              <div className="status-icon">✅</div>
              <h3>Video Processing</h3>
              <p>Real-time video analysis with object detection and majority vote algorithms</p>
              <div className="status-badge operational">Operational</div>
            </div>
            
            <div className="implementation-card active">
              <div className="status-icon">✅</div>
              <h3>Live Feed Support</h3>
              <p>Webcam integration with sub-100ms processing for real-time monitoring</p>
              <div className="status-badge operational">Operational</div>
            </div>
            
            <div className="implementation-card active">
              <div className="status-icon">✅</div>
              <h3>Interactive Heatmaps</h3>
              <p>Leaflet.js maps with OpenStreetMap integration and behavioral data visualization</p>
              <div className="status-badge operational">Operational</div>
            </div>
          </div>
        </div>
      </section>

      {/* Performance Stats */}
      <section className="stats-section">
        <div className="container">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-number">2</div>
              <div className="stat-label">AI Models</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">5</div>
              <div className="stat-label">Detection Classes</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">Real-time</div>
              <div className="stat-label">Processing</div>
            </div>
            <div className="stat-card">
              <div className="stat-number">&lt;100ms</div>
              <div className="stat-label">Response Time</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};

export default AboutPage;
