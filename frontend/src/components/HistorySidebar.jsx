import React, { useState, useEffect } from 'react'
import { useAuth } from '../context/AuthContext'
import './HistorySidebar.css'

export default function HistorySidebar({ selectedScan, onSelectScan }) {
  const { tokens, user } = useAuth()
  const [history, setHistory] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    if (tokens && user) {
      fetchHistory()
    }
  }, [tokens, user])

  const fetchHistory = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await fetch('http://localhost:8000/history', {
        headers: {
          'Authorization': `Bearer ${tokens.access_token}`
        }
      })

      if (!response.ok) {
        throw new Error('Failed to fetch history')
      }

      const data = await response.json()
      setHistory(data.items || [])
    } catch (err) {
      setError('Failed to load history')
      console.error(err)
    } finally {
      setLoading(false)
    }
  }

  const formatDate = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  const getConfidenceColor = (confidence) => {
    if (confidence >= 75) return '#4caf50'
    if (confidence >= 50) return '#ff9800'
    return '#f44336'
  }

  return (
    <div className="history-sidebar">
      <div className="sidebar-header">
        <h3>Scan History</h3>
        <button
          className="refresh-btn"
          onClick={fetchHistory}
          title="Refresh history"
          disabled={loading}
        >
          ↻
        </button>
      </div>

      {user && (
        <div className="user-info-mini">
          <div className="user-avatar">
            {user.first_name.charAt(0).toUpperCase()}
          </div>
          <div className="user-details">
            <div className="user-name">{user.first_name} {user.last_name}</div>
            <div className="user-type">{user.user_type}</div>
          </div>
        </div>
      )}

      <div className="history-list-container">
        {loading && (
          <div className="loading-state">
            <div className="spinner"></div>
            Loading...
          </div>
        )}

        {error && (
          <div className="error-state">
            <p>{error}</p>
            <button onClick={fetchHistory} className="retry-btn">
              Retry
            </button>
          </div>
        )}

        {!loading && !error && history.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">📋</div>
            <p>No scans yet</p>
            <p className="empty-subtitle">Upload an image to get started</p>
          </div>
        )}

        {!loading && !error && history.length > 0 && (
          <div className="history-list">
            {history.map((scan) => (
              <div
                key={scan.id}
                className={`history-item ${selectedScan?.id === scan.id ? 'active' : ''}`}
                onClick={() => onSelectScan(scan)}
              >
                <div className="history-item-header">
                  <div className="prediction-badge" style={{
                    backgroundColor: scan.prediction === 'PNEUMONIA' ? '#f44336' : '#4caf50'
                  }}>
                    {scan.prediction}
                  </div>
                  <div className="confidence-indicator">
                    <span
                      className="confidence-dot"
                      style={{ backgroundColor: getConfidenceColor(scan.confidence) }}
                    ></span>
                    {scan.confidence}%
                  </div>
                </div>
                <div className="history-item-time">
                  {formatDate(scan.timestamp)}
                </div>
                <div className="history-item-probs">
                  <span>N: {scan.normal_prob}%</span>
                  <span>P: {scan.pneumonia_prob}%</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
