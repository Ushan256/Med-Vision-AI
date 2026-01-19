import React from 'react'
import './MedicalDisclaimer.css'

const MedicalDisclaimer = () => {
  return (
    <footer className="medical-disclaimer">
      <div className="disclaimer-content">
        <div className="disclaimer-icon">⚠️</div>
        <p className="disclaimer-text">
          <strong>Medical Disclaimer:</strong> This is an AI prototype for research purposes and should not be used for clinical diagnosis.
        </p>
      </div>
    </footer>
  )
}

export default MedicalDisclaimer
