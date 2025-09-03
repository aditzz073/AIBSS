import React, { useState } from 'react';
import './DashboardPage.css';

// Mock data for detection runs
const mockDetectionRuns = [
  {
    id: 1,
    timestamp: '2024-03-15 14:30:22',
    videoName: 'dog_park_video.mp4',
    aggressivePercentage: 15.2,
    calmPercentage: 84.8,
    totalFrames: 1250,
    duration: '2:15'
  },
  {
    id: 2,
    timestamp: '2024-03-15 12:45:10',
    videoName: 'backyard_behavior.mp4',
    aggressivePercentage: 32.7,
    calmPercentage: 67.3,
    totalFrames: 890,
    duration: '1:45'
  },
  {
    id: 3,
    timestamp: '2024-03-15 10:20:55',
    videoName: 'training_session.mp4',
    aggressivePercentage: 8.3,
    calmPercentage: 91.7,
    totalFrames: 2100,
    duration: '3:30'
  },
  {
    id: 4,
    timestamp: '2024-03-14 16:15:33',
    videoName: 'street_walk.mp4',
    aggressivePercentage: 45.6,
    calmPercentage: 54.4,
    totalFrames: 1680,
    duration: '2:48'
  },
  {
    id: 5,
    timestamp: '2024-03-14 14:20:18',
    videoName: 'home_monitoring.mp4',
    aggressivePercentage: 12.1,
    calmPercentage: 87.9,
    totalFrames: 3600,
    duration: '6:00'
  },
  {
    id: 6,
    timestamp: '2024-03-14 11:30:45',
    videoName: 'vet_visit.mp4',
    aggressivePercentage: 78.4,
    calmPercentage: 21.6,
    totalFrames: 450,
    duration: '0:45'
  },
  {
    id: 7,
    timestamp: '2024-03-13 15:45:12',
    videoName: 'playground_test.mp4',
    aggressivePercentage: 22.8,
    calmPercentage: 77.2,
    totalFrames: 1920,
    duration: '3:12'
  },
  {
    id: 8,
    timestamp: '2024-03-13 13:10:30',
    videoName: 'feeding_time.mp4',
    aggressivePercentage: 5.7,
    calmPercentage: 94.3,
    totalFrames: 720,
    duration: '1:12'
  }
];

const ITEMS_PER_PAGE = 5;

const DashboardPage = () => {
  const [currentPage, setCurrentPage] = useState(1);
  const [sortConfig, setSortConfig] = useState({ key: 'timestamp', direction: 'desc' });

  // Sort data
  const sortedData = [...mockDetectionRuns].sort((a, b) => {
    if (sortConfig.direction === 'asc') {
      return a[sortConfig.key] > b[sortConfig.key] ? 1 : -1;
    }
    return a[sortConfig.key] < b[sortConfig.key] ? 1 : -1;
  });

  // Pagination
  const totalPages = Math.ceil(sortedData.length / ITEMS_PER_PAGE);
  const startIndex = (currentPage - 1) * ITEMS_PER_PAGE;
  const paginatedData = sortedData.slice(startIndex, startIndex + ITEMS_PER_PAGE);

  const handleSort = (key) => {
    setSortConfig(prevConfig => ({
      key,
      direction: prevConfig.key === key && prevConfig.direction === 'desc' ? 'asc' : 'desc'
    }));
  };

  const handlePageChange = (page) => {
    setCurrentPage(page);
  };

  const formatDate = (timestamp) => {
    return new Date(timestamp).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const getStatusClass = (aggressivePercentage) => {
    if (aggressivePercentage < 20) return 'status-low';
    if (aggressivePercentage < 50) return 'status-medium';
    return 'status-high';
  };

  const calculateAverages = () => {
    const total = mockDetectionRuns.length;
    const avgAggressive = mockDetectionRuns.reduce((sum, run) => sum + run.aggressivePercentage, 0) / total;
    const avgCalm = mockDetectionRuns.reduce((sum, run) => sum + run.calmPercentage, 0) / total;
    const totalFrames = mockDetectionRuns.reduce((sum, run) => sum + run.totalFrames, 0);
    
    return {
      avgAggressive: avgAggressive.toFixed(1),
      avgCalm: avgCalm.toFixed(1),
      totalFrames,
      totalRuns: total
    };
  };

  const stats = calculateAverages();

  return (
    <div className="dashboard-page">
      <div className="container">
        <div className="page-header">
          <h1>Detection Dashboard</h1>
          <p>Overview of all video analysis runs and behavioral insights</p>
        </div>

        {/* Statistics Cards */}
        <div className="stats-section">
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">📊</div>
              <div className="stat-content">
                <div className="stat-number">{stats.totalRuns}</div>
                <div className="stat-label">Total Analyses</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">😌</div>
              <div className="stat-content">
                <div className="stat-number">{stats.avgCalm}%</div>
                <div className="stat-label">Avg. Calm Behavior</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">😠</div>
              <div className="stat-content">
                <div className="stat-number">{stats.avgAggressive}%</div>
                <div className="stat-label">Avg. Aggressive Behavior</div>
              </div>
            </div>
            
            <div className="stat-card">
              <div className="stat-icon">🎞️</div>
              <div className="stat-content">
                <div className="stat-number">{stats.totalFrames.toLocaleString()}</div>
                <div className="stat-label">Total Frames Analyzed</div>
              </div>
            </div>
          </div>
        </div>

        {/* Data Table */}
        <div className="table-section">
          <div className="card">
            <div className="card-header">
              <h2>Detection History</h2>
              <div className="table-info">
                Showing {startIndex + 1}-{Math.min(startIndex + ITEMS_PER_PAGE, sortedData.length)} of {sortedData.length} results
              </div>
            </div>
            
            <div className="table-container">
              <table className="data-table">
                <thead>
                  <tr>
                    <th onClick={() => handleSort('timestamp')} className="sortable">
                      Timestamp
                      {sortConfig.key === 'timestamp' && (
                        <span className="sort-indicator">
                          {sortConfig.direction === 'desc' ? ' ↓' : ' ↑'}
                        </span>
                      )}
                    </th>
                    <th onClick={() => handleSort('videoName')} className="sortable">
                      Video Name
                      {sortConfig.key === 'videoName' && (
                        <span className="sort-indicator">
                          {sortConfig.direction === 'desc' ? ' ↓' : ' ↑'}
                        </span>
                      )}
                    </th>
                    <th>Duration</th>
                    <th onClick={() => handleSort('aggressivePercentage')} className="sortable">
                      Aggressive %
                      {sortConfig.key === 'aggressivePercentage' && (
                        <span className="sort-indicator">
                          {sortConfig.direction === 'desc' ? ' ↓' : ' ↑'}
                        </span>
                      )}
                    </th>
                    <th onClick={() => handleSort('calmPercentage')} className="sortable">
                      Calm %
                      {sortConfig.key === 'calmPercentage' && (
                        <span className="sort-indicator">
                          {sortConfig.direction === 'desc' ? ' ↓' : ' ↑'}
                        </span>
                      )}
                    </th>
                    <th>Frames</th>
                    <th>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {paginatedData.map((run) => (
                    <tr key={run.id}>
                      <td className="timestamp-cell">
                        {formatDate(run.timestamp)}
                      </td>
                      <td className="video-name-cell">
                        <span className="video-icon">📹</span>
                        {run.videoName}
                      </td>
                      <td>{run.duration}</td>
                      <td className="percentage-cell aggressive">
                        {run.aggressivePercentage}%
                      </td>
                      <td className="percentage-cell calm">
                        {run.calmPercentage}%
                      </td>
                      <td>{run.totalFrames.toLocaleString()}</td>
                      <td>
                        <span className={`status-badge ${getStatusClass(run.aggressivePercentage)}`}>
                          {run.aggressivePercentage < 20 ? 'Low Risk' : 
                           run.aggressivePercentage < 50 ? 'Medium Risk' : 'High Risk'}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div className="pagination">
                <button 
                  onClick={() => handlePageChange(currentPage - 1)}
                  disabled={currentPage === 1}
                  className="btn btn-secondary"
                >
                  ← Previous
                </button>
                
                <div className="page-numbers">
                  {[...Array(totalPages)].map((_, index) => {
                    const page = index + 1;
                    return (
                      <button
                        key={page}
                        onClick={() => handlePageChange(page)}
                        className={`page-number ${currentPage === page ? 'active' : ''}`}
                      >
                        {page}
                      </button>
                    );
                  })}
                </div>
                
                <button 
                  onClick={() => handlePageChange(currentPage + 1)}
                  disabled={currentPage === totalPages}
                  className="btn btn-secondary"
                >
                  Next →
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;
