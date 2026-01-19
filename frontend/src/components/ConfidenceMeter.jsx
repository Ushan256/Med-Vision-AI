import React from 'react'
import './ConfidenceMeter.css'

const ConfidenceMeter = ({ confidence }) => {
  const getConfidenceColor = (conf) => {
    if (conf >= 80) return '#28a745' // Green
    if (conf >= 60) return '#ffc107' // Yellow
    return '#dc3545' // Red
  }

  const getConfidenceLabel = (conf) => {
    if (conf >= 90) return 'Very High'
    if (conf >= 80) return 'High'
    if (conf >= 70) return 'Moderate'
    if (conf >= 60) return 'Low-Moderate'
    return 'Low'
  }

  const color = getConfidenceColor(confidence)
  const label = getConfidenceLabel(confidence)

  return (
    <div className="confidence-meter">
      <div className="confidence-header">
        <span className="confidence-label">Confidence Level:</span>
        <span className="confidence-percentage" style={{ color }}>
          {confidence}%
        </span>
        <span className="confidence-status" style={{ color }}>
          ({label})
        </span>
      </div>
      <div className="progress-bar-container">
        <div
          className="progress-bar"
          style={{
            width: `${confidence}%`,
            backgroundColor: color,
          }}
        >
          <div className="progress-bar-fill" />
        </div>
      </div>
      <div className="confidence-scale">
        <span>0%</span>
        <span>50%</span>
        <span>100%</span>
      </div>
    </div>
  )
}

export default ConfidenceMeter
