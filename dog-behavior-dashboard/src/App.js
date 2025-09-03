import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Navbar from './components/Navbar/Navbar';
import HomePage from './pages/HomePage/HomePage';
import AnalysisPage from './pages/AnalysisPage/AnalysisPage';
import VideoAnalysisPage from './pages/VideoAnalysisPage/VideoAnalysisPage';
import DashboardPage from './pages/DashboardPage/DashboardPage';
import LiveFeedPage from './pages/LiveFeedPage/LiveFeedPage';
import HeatmapPage from './pages/HeatmapPage/HeatmapPage';
import AboutPage from './pages/AboutPage/AboutPage';
import './App.css';

function App() {
  return (
    <Router>
      <div className="App">
        <Navbar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/analysis" element={<AnalysisPage />} />
            <Route path="/video-analysis" element={<VideoAnalysisPage />} />
            <Route path="/dashboard" element={<DashboardPage />} />
            <Route path="/live" element={<LiveFeedPage />} />
            <Route path="/heatmap" element={<HeatmapPage />} />
            <Route path="/about" element={<AboutPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}

export default App;
