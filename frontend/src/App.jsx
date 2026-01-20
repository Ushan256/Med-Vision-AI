import React, { useState, useEffect } from 'react'
import axios from 'axios'
import './App.css'
import { useAuth } from './context/AuthContext'
import AuthModal from './components/AuthModal'
import HistorySidebar from './components/HistorySidebar'
import ConfidenceMeter from './components/ConfidenceMeter'
import InteractiveHeatmap from './components/InteractiveHeatmap'
import MedicalDisclaimer from './components/MedicalDisclaimer'

function App() {
  const { user, tokens, logout, isAuthenticated } = useAuth()
  
  const [authModalOpen, setAuthModalOpen] = useState(false)
  const [file, setFile] = useState(null)
  const [preview, setPreview] = useState(null)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [darkMode, setDarkMode] = useState(false)
  const [selectedScan, setSelectedScan] = useState(null)

  // Open auth modal if not authenticated
  useEffect(() => {
    if (!isAuthenticated && !authModalOpen) {
      setAuthModalOpen(true)
    }
  }, [isAuthenticated])

  // Load dark mode preference
  useEffect(() => {
    const savedDarkMode = localStorage.getItem('darkMode') === 'true'
    setDarkMode(savedDarkMode)
    applyDarkMode(savedDarkMode)
  }, [])

  const applyDarkMode = (isDark) => {
    if (isDark) {
      document.documentElement.setAttribute('data-theme', 'dark')
    } else {
      document.documentElement.removeAttribute('data-theme')
    }
  }

  const toggleDarkMode = () => {
    const newDarkMode = !darkMode
    setDarkMode(newDarkMode)
    localStorage.setItem('darkMode', newDarkMode)
    applyDarkMode(newDarkMode)
  }

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0]
    if (selectedFile) {
      setFile(selectedFile)
      setError(null)
      setResult(null)
      setSelectedScan(null)
      
      // Create preview
      const reader = new FileReader()
      reader.onloadend = () => {
        setPreview(reader.result)
      }
      reader.readAsDataURL(selectedFile)
    }
  }

const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Please select an image file');
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    // Dynamic URL: Uses Vercel environment variable or defaults to your HF Space
    const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://ushan256-med-vision-ai.hf.space';

    try {
      const response = await axios.post(`${API_BASE_URL}/predict`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
          'Authorization': `Bearer ${tokens.access_token}`
        },
      });
      setResult(response.data);
    } catch (err) {
      // Professional Error Handling: Checks if the server is "sleeping" (Cold Start)
      const isNetworkError = !err.response;
      const errorMessage = isNetworkError 
        ? 'Cannot connect to AI server. It might be waking up—please try again in 30 seconds.' 
        : (err.response?.data?.detail || 'An error occurred while processing the image');
      
      setError(errorMessage);
      console.error('API Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = () => {
    setFile(null)
    setPreview(null)
    setResult(null)
    setError(null)
    setSelectedScan(null)
    const fileInput = document.getElementById('file-input')
    if (fileInput) fileInput.value = ''
  }

  const handleSelectScan = (scan) => {
    setSelectedScan(scan)
    setFile(null)
    setPreview(null)
    setResult({
      prediction: scan.prediction,
      confidence: scan.confidence,
      probabilities: {
        NORMAL: scan.normal_prob,
        PNEUMONIA: scan.pneumonia_prob
      },
      heatmap: scan.heatmap_base64,
      original_image: scan.original_image_base64
    })
  }

  if (!isAuthenticated) {
    return (
      <>
        <AuthModal isOpen={authModalOpen} onClose={() => setAuthModalOpen(true)} />
      </>
    )
  }

  return (
    <div className="app">
      <div className="app-container">
        {/* Sidebar */}
        <HistorySidebar 
          selectedScan={selectedScan}
          onSelectScan={handleSelectScan}
        />

        {/* Main content */}
        <div className="main-wrapper">
          <header className="app-header">
            <div className="header-left">
              <h1 className="app-title">MED-VISION</h1>
              <p className="app-subtitle">Chest X-Ray Pneumonia Classification</p>
            </div>
            
            <div className="header-right">
              <button
                className="theme-toggle"
                onClick={toggleDarkMode}
                title={darkMode ? 'Light Mode' : 'Dark Mode'}
              >
                {darkMode ? '☀️' : '🌙'}
              </button>

              {user && (
                <div className="user-menu">
                  <div className="user-avatar">{user.first_name.charAt(0).toUpperCase()}</div>
                  <div className="user-dropdown">
                    <div className="dropdown-header">
                      <strong>{user.first_name} {user.last_name}</strong>
                      <small>{user.user_type}</small>
                    </div>
                    <div className="dropdown-divider"></div>
                    <button onClick={logout} className="logout-btn">
                      Logout
                    </button>
                  </div>
                </div>
              )}
            </div>
          </header>

          {/* Content area */}
          <div className="content-area">
            {!result && !selectedScan && (
              <>
                {/* Upload section */}
                <div className="upload-card">
                  <div className="upload-header">
                    <h2>Upload X-Ray Image</h2>
                    <p className="upload-subtitle">JPG, PNG, or other image formats</p>
                  </div>

                  <form onSubmit={handleSubmit} className="upload-form">
                    <div className="file-input-wrapper">
                      <input
                        id="file-input"
                        type="file"
                        accept="image/*"
                        onChange={handleFileChange}
                        className="file-input"
                      />
                      <label htmlFor="file-input" className="file-label">
                        <div className="file-label-content">
                          <span className="file-icon">📁</span>
                          <span className="file-text">
                            {file ? file.name : 'Click to upload or drag and drop'}
                          </span>
                        </div>
                      </label>
                    </div>

                    {preview && (
                      <div className="preview-container">
                        <div className="preview-label">Preview</div>
                        <img src={preview} alt="Preview" className="preview-image" />
                      </div>
                    )}

                    {error && (
                      <div className="error-message">
                        <span className="error-icon">⚠️</span>
                        <p>{error}</p>
                      </div>
                    )}

                    <div className="button-group">
                      <button
                        type="submit"
                        disabled={!file || loading}
                        className="btn btn-primary"
                      >
                        {loading ? (
                          <>
                            <span className="spinner-mini"></span>
                            Analyzing...
                          </>
                        ) : (
                          '🔍 Analyze Image'
                        )}
                      </button>
                      {file && (
                        <button
                          type="button"
                          onClick={handleReset}
                          className="btn btn-secondary"
                        >
                          Reset
                        </button>
                      )}
                    </div>
                  </form>
                </div>

                {/* Info cards */}
                <div className="info-grid">
                  <div className="info-card">
                    <div className="info-icon">🩺</div>
                    <h3>Accurate Detection</h3>
                    <p>Advanced deep learning model for pneumonia classification</p>
                  </div>
                  <div className="info-card">
                    <div className="info-icon">🧠</div>
                    <h3>Explainable AI</h3>
                    <p>Grad-CAM heatmaps show regions the AI focuses on</p>
                  </div>
                  <div className="info-card">
                    <div className="info-icon">📊</div>
                    <h3>Confidence Scores</h3>
                    <p>Get detailed probability breakdown for all classes</p>
                  </div>
                </div>
              </>
            )}

            {(result || selectedScan) && (
              <div className="results-grid">
                {/* Left: Image display */}
                <div className="results-image-section">
                  <div className="results-card">
                    <h3>X-Ray Image</h3>
                    {result?.original_image && (
                      <InteractiveHeatmap
                        originalImage={result.original_image}
                        heatmapImage={result.heatmap}
                      />
                    )}
                  </div>
                </div>

                {/* Right: Results display */}
                <div className="results-info-section">
                  <div className="results-card">
                    <div className="results-header">
                      <h2>Analysis Results</h2>
                      {!selectedScan && (
                        <button
                          onClick={handleReset}
                          className="btn btn-small btn-secondary"
                        >
                          New Scan
                        </button>
                      )}
                    </div>

                    <div className="prediction-result">
                      <div className="prediction-badge-large">
                        <span className={`badge ${result?.prediction.toLowerCase()}`}>
                          {result?.prediction}
                        </span>
                      </div>

                      <ConfidenceMeter confidence={result?.confidence} />

                      <div className="probabilities-section">
                        <h3>Class Probabilities</h3>
                        <div className="probability-bars">
                          {result?.probabilities && Object.entries(result.probabilities).map(([className, prob]) => (
                            <div key={className} className="probability-bar-item">
                              <div className="bar-label">
                                <span className="bar-class">{className}</span>
                                <span className="bar-value">{prob}%</span>
                              </div>
                              <div className="bar-bg">
                                <div
                                  className={`bar-fill ${className.toLowerCase()}`}
                                  style={{ width: `${prob}%` }}
                                ></div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>

                      {selectedScan && (
                        <div className="scan-meta">
                          <span className="meta-label">Scanned:</span>
                          <span className="meta-value">
                            {new Date(selectedScan.timestamp).toLocaleString()}
                          </span>
                        </div>
                      )}
                    </div>
                  </div>

                  <MedicalDisclaimer />
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}

export default App

