import React, { useState } from 'react'
import './InteractiveHeatmap.css'

export default function InteractiveHeatmap({ originalImage, heatmapImage }) {
  const [showHeatmap, setShowHeatmap] = useState(true)
  const [heatmapOpacity, setHeatmapOpacity] = useState(0.7)

  return (
    <div className="interactive-heatmap">
      <div className="heatmap-controls">
        <div className="controls-left">
          <label className="toggle-switch">
            <input
              type="checkbox"
              checked={showHeatmap}
              onChange={(e) => setShowHeatmap(e.target.checked)}
            />
            <span className="slider"></span>
            <span className="label-text">
              {showHeatmap ? 'Heatmap On' : 'Heatmap Off'}
            </span>
          </label>
        </div>

        {showHeatmap && (
          <div className="controls-right">
            <label className="opacity-control">
              <span>Opacity:</span>
              <input
                type="range"
                min="0"
                max="100"
                value={heatmapOpacity * 100}
                onChange={(e) => setHeatmapOpacity(e.target.value / 100)}
                className="opacity-slider"
              />
              <span className="opacity-value">{Math.round(heatmapOpacity * 100)}%</span>
            </label>
          </div>
        )}
      </div>

      <div className="heatmap-display">
        <div className="heatmap-container">
          {originalImage && (
            <img
              src={originalImage}
              alt="Original X-ray"
              className="heatmap-base"
            />
          )}
          {showHeatmap && heatmapImage && (
            <img
              src={heatmapImage}
              alt="Grad-CAM Heatmap"
              className="heatmap-overlay"
              style={{ opacity: heatmapOpacity }}
            />
          )}
        </div>

        <div className="heatmap-info">
          <p className="info-text">
            {showHeatmap ? (
              <>
                <strong>Grad-CAM Visualization:</strong> The overlay shows regions the AI focuses on for its prediction.
                <br />
                <em>Adjust opacity or toggle to compare with original image.</em>
              </>
            ) : (
              <>
                <strong>Original X-ray:</strong> Toggle heatmap on to see AI focus areas.
              </>
            )}
          </p>
        </div>
      </div>
    </div>
  )
}
