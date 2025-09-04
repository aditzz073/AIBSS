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
  const [mapCenter, setMapCenter] = useState([12.9716, 77.5946]); // Default to Bangalore
  const [mapZoom, setMapZoom] = useState(11);
  const [userLocation, setUserLocation] = useState(null);
  const [locationLoading, setLocationLoading] = useState(false);
  const [showAddDataForm, setShowAddDataForm] = useState(false);
  const [newDetectionForm, setNewDetectionForm] = useState({
    lat: '',
    lon: '',
    risk: 0.5,
    label: 'Non-Aggressive'
  });

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

  // Get user's current location
  const getCurrentLocation = () => {
    setLocationLoading(true);
    
    if (!navigator.geolocation) {
      alert('Geolocation is not supported by this browser.');
      setLocationLoading(false);
      return;
    }

    navigator.geolocation.getCurrentPosition(
      (position) => {
        const { latitude, longitude } = position.coords;
        setUserLocation({ lat: latitude, lon: longitude });
        setMapCenter([latitude, longitude]);
        setMapZoom(13); // Zoom closer for user location
        setLocationLoading(false);
      },
      (error) => {
        console.error('Error getting location:', error);
        let errorMessage = 'Unable to retrieve your location.';
        
        switch(error.code) {
          case error.PERMISSION_DENIED:
            errorMessage = 'Location access denied. Please enable location permissions.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMessage = 'Location information is unavailable.';
            break;
          case error.TIMEOUT:
            errorMessage = 'Location request timed out.';
            break;
        }
        
        alert(errorMessage);
        setLocationLoading(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000 // 5 minutes
      }
    );
  };

  // Add new mock detection
  const addNewDetection = () => {
    const { lat, lon, risk, label } = newDetectionForm;
    
    // Validation
    if (!lat || !lon) {
      alert('Please enter valid latitude and longitude values.');
      return;
    }

    const latitude = parseFloat(lat);
    const longitude = parseFloat(lon);

    if (isNaN(latitude) || isNaN(longitude)) {
      alert('Please enter valid numeric coordinates.');
      return;
    }

    if (latitude < -90 || latitude > 90 || longitude < -180 || longitude > 180) {
      alert('Please enter valid coordinate ranges (lat: -90 to 90, lon: -180 to 180).');
      return;
    }

    const newDetection = {
      lat: latitude,
      lon: longitude,
      risk: parseFloat(risk),
      label: label,
      timestamp: new Date().toISOString(),
      userAdded: true // Flag to identify user-added detections
    };

    setDetections(prev => [...prev, newDetection]);
    
    // Reset form
    setNewDetectionForm({
      lat: '',
      lon: '',
      risk: 0.5,
      label: 'Non-Aggressive'
    });
    
    setShowAddDataForm(false);
    
    // Optional: Center map on new detection
    setMapCenter([latitude, longitude]);
    setMapZoom(15);
  };

  // Auto-fill coordinates with current location
  const useCurrentLocationForNewDetection = () => {
    if (userLocation) {
      setNewDetectionForm(prev => ({
        ...prev,
        lat: userLocation.lat.toFixed(6),
        lon: userLocation.lon.toFixed(6)
      }));
    } else {
      alert('Please get your current location first.');
    }
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
          <div className="stat-card total">
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

        <div className="control-buttons">
          <button 
            onClick={getCurrentLocation} 
            disabled={locationLoading}
            className="location-button"
          >
            {locationLoading ? 'Getting Location...' : '📍 My Location'}
          </button>
          
          <button 
            onClick={() => setShowAddDataForm(true)}
            className="add-data-button"
          >
            ➕ Add Detection
          </button>
        </div>

        <div className="filter-controls">
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
            center={mapCenter}
            zoom={mapZoom}
            style={{ height: '500px', width: '100%' }}
            className="heatmap-map"
            key={`${mapCenter[0]}-${mapCenter[1]}-${mapZoom}`} // Force re-render when center/zoom changes
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            {/* User location marker */}
            {userLocation && (
              <CircleMarker
                center={[userLocation.lat, userLocation.lon]}
                radius={12}
                pathOptions={{
                  color: '#2563eb',
                  fillColor: '#3b82f6',
                  fillOpacity: 0.8,
                  weight: 3,
                }}
              >
                <Popup>
                  <div className="map-popup">
                    <h4>📍 Your Location</h4>
                    <p><strong>Coordinates:</strong> {userLocation.lat.toFixed(6)}, {userLocation.lon.toFixed(6)}</p>
                  </div>
                </Popup>
                <Tooltip direction="top" offset={[0, -15]} opacity={1}>
                  <span>Your Current Location</span>
                </Tooltip>
              </CircleMarker>
            )}
            
            {filteredDetections.map((detection, index) => (
              <CircleMarker
                key={index}
                center={[detection.lat, detection.lon]}
                radius={getMarkerRadius(detection.risk)}
                pathOptions={{
                  color: getRiskColor(detection.risk),
                  fillColor: getRiskColor(detection.risk),
                  fillOpacity: 0.7,
                  weight: detection.userAdded ? 3 : 2, // Thicker border for user-added
                  dashArray: detection.userAdded ? '5,5' : null, // Dashed border for user-added
                }}
                eventHandlers={{
                  click: () => setSelectedDetection(detection),
                }}
              >
                <Popup>
                  <div className="map-popup">
                    <h4>Detection Details {detection.userAdded && '(User Added)'}</h4>
                    <p><strong>Risk Level:</strong> {getRiskLevel(detection.risk)} ({detection.risk.toFixed(2)})</p>
                    <p><strong>Behavior:</strong> {detection.label}</p>
                    <p><strong>Location:</strong> {detection.lat.toFixed(4)}, {detection.lon.toFixed(4)}</p>
                    <p><strong>Time:</strong> {new Date(detection.timestamp).toLocaleString()}</p>
                  </div>
                </Popup>
                
                <Tooltip direction="top" offset={[0, -10]} opacity={1}>
                  <span>Risk: {detection.risk.toFixed(1)} - {detection.label} {detection.userAdded && '(Custom)'}</span>
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
                      {detection.label} {detection.userAdded && '(Custom)'}
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
              <h3>Detection Details {selectedDetection.userAdded && '(User Added)'}</h3>
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

      {/* Add Detection Data Form Modal */}
      {showAddDataForm && (
        <div className="detection-modal" onClick={() => setShowAddDataForm(false)}>
          <div className="modal-content add-data-modal" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <h3>Add New Detection Data</h3>
              <button
                className="close-button"
                onClick={() => setShowAddDataForm(false)}
              >
                ×
              </button>
            </div>
            <div className="modal-body">
              <div className="form-section">
                <h4>Location Coordinates</h4>
                <div className="coordinate-inputs">
                  <div className="input-group">
                    <label>Latitude:</label>
                    <input
                      type="number"
                      step="any"
                      placeholder="e.g., 12.9716"
                      value={newDetectionForm.lat}
                      onChange={(e) => setNewDetectionForm(prev => ({
                        ...prev,
                        lat: e.target.value
                      }))}
                      className="coordinate-input"
                    />
                  </div>
                  <div className="input-group">
                    <label>Longitude:</label>
                    <input
                      type="number"
                      step="any"
                      placeholder="e.g., 77.5946"
                      value={newDetectionForm.lon}
                      onChange={(e) => setNewDetectionForm(prev => ({
                        ...prev,
                        lon: e.target.value
                      }))}
                      className="coordinate-input"
                    />
                  </div>
                </div>
                
                {userLocation && (
                  <button
                    onClick={useCurrentLocationForNewDetection}
                    className="use-location-button"
                  >
                    📍 Use My Current Location
                  </button>
                )}
              </div>

              <div className="form-section">
                <h4>Detection Details</h4>
                <div className="input-group">
                  <label>Risk Level (0.0 - 1.0):</label>
                  <input
                    type="range"
                    min="0"
                    max="1"
                    step="0.1"
                    value={newDetectionForm.risk}
                    onChange={(e) => setNewDetectionForm(prev => ({
                      ...prev,
                      risk: parseFloat(e.target.value)
                    }))}
                    className="risk-slider"
                  />
                  <div className="risk-display">
                    <span style={{color: getRiskColor(newDetectionForm.risk)}}>
                      {newDetectionForm.risk.toFixed(1)} - {getRiskLevel(newDetectionForm.risk)}
                    </span>
                  </div>
                </div>

                <div className="input-group">
                  <label>Behavior Type:</label>
                  <select
                    value={newDetectionForm.label}
                    onChange={(e) => setNewDetectionForm(prev => ({
                      ...prev,
                      label: e.target.value
                    }))}
                    className="behavior-select"
                  >
                    <option value="Non-Aggressive">Non-Aggressive</option>
                    <option value="Aggressive">Aggressive</option>
                  </select>
                </div>
              </div>

              <div className="form-actions">
                <button
                  onClick={() => setShowAddDataForm(false)}
                  className="cancel-button"
                >
                  Cancel
                </button>
                <button
                  onClick={addNewDetection}
                  className="add-button"
                >
                  Add Detection
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
      </div>
    </div>
  );
};export default HeatmapPage;
