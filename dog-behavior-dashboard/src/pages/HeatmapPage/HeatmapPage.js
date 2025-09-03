import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, CircleMarker, Popup, Tooltip } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import { getDetections } from '../../api';
import './HeatmapPage.css';

const HeatmapPage = () => {
  const [detections, setDetections] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedDetection, setSelectedDetection] = useState(null);
  const [filterType, setFilterType] = useState('all'); // 'all', 'aggressive', 'non-aggressive'

  useEffect(() => {
    fetchDetections();
  }, []);

  const fetchDetections = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getDetections();
      setDetections(data);
    } catch (err) {
      setError(`Failed to load detection data: ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (risk) => {
    // Convert risk (0-1) to color intensity for map markers
    if (risk >= 0.8) return '#dc2626'; // Red for high risk
    if (risk >= 0.6) return '#ea580c'; // Orange-red
    if (risk >= 0.4) return '#d97706'; // Orange
    if (risk >= 0.2) return '#eab308'; // Yellow
    return '#16a34a'; // Green for low risk
  };

  const getMarkerRadius = (risk) => {
    // Make higher risk markers larger
    return Math.max(8, risk * 20);
  };

  const getRiskLevel = (risk) => {
    if (risk >= 0.8) return 'Very High';
    if (risk >= 0.6) return 'High';
    if (risk >= 0.4) return 'Medium';
    if (risk >= 0.2) return 'Low';
    return 'Very Low';
  };

  const filteredDetections = detections.filter(detection => {
    if (filterType === 'all') return true;
    if (filterType === 'aggressive') return detection.label === 'Aggressive';
    if (filterType === 'non-aggressive') return detection.label === 'Non-Aggressive';
    return true;
  });

  const aggressiveCount = detections.filter(d => d.label === 'Aggressive').length;
  const nonAggressiveCount = detections.filter(d => d.label === 'Non-Aggressive').length;

  if (loading) {
    return (
      <div className="heatmap-page">
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading detection data...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="heatmap-page">
        <div className="error-container">
          <div className="error-message">
            <h3>Error Loading Data</h3>
            <p>{error}</p>
            <button onClick={fetchDetections} className="retry-button">
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="heatmap-page">
      <div className="heatmap-container-wrapper">
        <div className="heatmap-header">
          <h1>🗺️ Dog Behavior Heatmap</h1>
          <p>Real-time detection data showing risk levels across different locations</p>
        </div>

      <div className="heatmap-controls">
        <div className="stats-container">
          <div className="stat-card">
            <h3>{detections.length}</h3>
            <p>Total Detections</p>
          </div>
          <div className="stat-card aggressive">
            <h3>{aggressiveCount}</h3>
            <p>Aggressive</p>
          </div>
          <div className="stat-card non-aggressive">
            <h3>{nonAggressiveCount}</h3>
            <p>Non-Aggressive</p>
          </div>
        </div>

        <div className="filter-controls">
          <label>Filter by type:</label>
          <select 
            value={filterType} 
            onChange={(e) => setFilterType(e.target.value)}
            className="filter-select"
          >
            <option value="all">All Detections</option>
            <option value="aggressive">Aggressive Only</option>
            <option value="non-aggressive">Non-Aggressive Only</option>
          </select>
        </div>
      </div>

      <div className="heatmap-legend">
        <h4>Risk Level Legend:</h4>
        <div className="legend-items">
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#16a34a'}}></div>
            <span>Very Low (0.0 - 0.2)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#eab308'}}></div>
            <span>Low (0.2 - 0.4)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#d97706'}}></div>
            <span>Medium (0.4 - 0.6)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#ea580c'}}></div>
            <span>High (0.6 - 0.8)</span>
          </div>
          <div className="legend-item">
            <div className="legend-color" style={{backgroundColor: '#dc2626'}}></div>
            <span>Very High (0.8 - 1.0)</span>
          </div>
        </div>
      </div>

      <div className="heatmap-container">
        <div className="map-wrapper">
          <MapContainer
            center={[12.9716, 77.5946]} // Bangalore coordinates
            zoom={11}
            style={{ height: '500px', width: '100%' }}
            className="heatmap-map"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            {filteredDetections.map((detection, index) => (
              <CircleMarker
                key={index}
                center={[detection.lat, detection.lon]}
                radius={getMarkerRadius(detection.risk)}
                pathOptions={{
                  color: getRiskColor(detection.risk),
                  fillColor: getRiskColor(detection.risk),
                  fillOpacity: 0.7,
                  weight: 2,
                }}
                eventHandlers={{
                  click: () => setSelectedDetection(detection),
                }}
              >
                <Popup>
                  <div className="map-popup">
                    <h4>Detection Details</h4>
                    <p><strong>Risk Level:</strong> {getRiskLevel(detection.risk)} ({detection.risk.toFixed(2)})</p>
                    <p><strong>Behavior:</strong> {detection.label}</p>
                    <p><strong>Location:</strong> {detection.lat.toFixed(4)}, {detection.lon.toFixed(4)}</p>
                    <p><strong>Time:</strong> {new Date(detection.timestamp).toLocaleString()}</p>
                  </div>
                </Popup>
                
                <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                  <span>Risk: {detection.risk.toFixed(1)} - {detection.label}</span>
                </Tooltip>
              </CircleMarker>
            ))}
          </MapContainer>
        </div>
      </div>

      <div className="detections-table">
        <h3>Detection Details</h3>
        <div className="table-container">
          <table>
            <thead>
              <tr>
                <th>Timestamp</th>
                <th>Location (Lat, Lon)</th>
                <th>Risk Level</th>
                <th>Label</th>
                <th>Risk Score</th>
              </tr>
            </thead>
            <tbody>
              {filteredDetections.map((detection, index) => (
                <tr
                  key={index}
                  className={`table-row ${detection.label.toLowerCase()}`}
                  onClick={() => setSelectedDetection(detection)}
                  style={{
                    backgroundColor: selectedDetection === detection ? '#f0f8ff' : 'transparent'
                  }}
                >
                  <td>{new Date(detection.timestamp).toLocaleString()}</td>
                  <td>
                    {detection.lat.toFixed(4)}, {detection.lon.toFixed(4)}
                  </td>
                  <td>
                    <span className={`risk-level ${getRiskLevel(detection.risk).toLowerCase().replace(' ', '-')}`}>
                      {getRiskLevel(detection.risk)}
                    </span>
                  </td>
                  <td>
                    <span className={`label ${detection.label.toLowerCase().replace(' ', '-')}`}>
                      {detection.label}
                    </span>
                  </td>
                  <td>
                    <div className="risk-bar">
                      <div
                        className="risk-fill"
                        style={{
                          width: `${detection.risk * 100}%`,
                          backgroundColor: getRiskColor(detection.risk)
                        }}
                      ></div>
                      <span className="risk-text">{detection.risk.toFixed(2)}</span>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {selectedDetection && (
        <div className="detection-modal" onClick={() => setSelectedDetection(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Detection Details</h3>
              <button
                className="close-button"
                onClick={() => setSelectedDetection(null)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="detail-row">
                <strong>Timestamp:</strong> {new Date(selectedDetection.timestamp).toLocaleString()}
              </div>
              <div className="detail-row">
                <strong>Location:</strong> {selectedDetection.lat.toFixed(6)}, {selectedDetection.lon.toFixed(6)}
              </div>
              <div className="detail-row">
                <strong>Risk Score:</strong> 
                <span style={{color: getRiskColor(selectedDetection.risk), fontWeight: 'bold'}}>
                  {selectedDetection.risk.toFixed(2)} ({getRiskLevel(selectedDetection.risk)})
                </span>
              </div>
              <div className="detail-row">
                <strong>Behavior:</strong> 
                <span className={`label ${selectedDetection.label.toLowerCase().replace(' ', '-')}`}>
                  {selectedDetection.label}
                </span>
              </div>
            </div>
          </div>
          </div>
        )}
      </div>
    </div>
  );
};export default HeatmapPage;
