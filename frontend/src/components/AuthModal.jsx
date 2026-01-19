import React, { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import './AuthModal.css'

export default function AuthModal({ isOpen, onClose }) {
  const { login, register, error: authError } = useAuth()
  const [isSignUp, setIsSignUp] = useState(false)
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    firstName: '',
    lastName: '',
    userType: 'other'
  })
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  const userTypes = [
    { value: 'student', label: 'Student' },
    { value: 'researcher', label: 'Researcher' },
    { value: 'doctor', label: 'Doctor' },
    { value: 'nurse', label: 'Nurse' },
    { value: 'other', label: 'Other' }
  ]

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
    setError('')
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      if (isSignUp) {
        await register(
          formData.email,
          formData.password,
          formData.firstName,
          formData.lastName,
          formData.userType
        )
      } else {
        await login(formData.email, formData.password)
      }
      onClose()
    } catch (err) {
      setError(err.message || 'An error occurred')
    } finally {
      setLoading(false)
    }
  }

  const toggleMode = () => {
    setIsSignUp(!isSignUp)
    setError('')
    setFormData({
      email: '',
      password: '',
      firstName: '',
      lastName: '',
      userType: 'other'
    })
  }

  if (!isOpen) return null

  return (
    <div className="auth-modal-overlay" onClick={onClose}>
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        <button className="close-btn" onClick={onClose}>×</button>
        
        <div className="auth-container">
          <h2>{isSignUp ? 'Create Account' : 'Login to MED-VISION'}</h2>
          <p className="auth-subtitle">
            {isSignUp ? 'Join our medical imaging platform' : 'Access your scan history and upload new images'}
          </p>

          <form onSubmit={handleSubmit} className="auth-form">
            {isSignUp && (
              <>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="firstName">First Name</label>
                    <input
                      type="text"
                      id="firstName"
                      name="firstName"
                      value={formData.firstName}
                      onChange={handleChange}
                      required={isSignUp}
                      placeholder="John"
                    />
                  </div>
                  <div className="form-group">
                    <label htmlFor="lastName">Last Name</label>
                    <input
                      type="text"
                      id="lastName"
                      name="lastName"
                      value={formData.lastName}
                      onChange={handleChange}
                      required={isSignUp}
                      placeholder="Doe"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label htmlFor="userType">I am a</label>
                  <select
                    id="userType"
                    name="userType"
                    value={formData.userType}
                    onChange={handleChange}
                    className="user-type-select"
                  >
                    {userTypes.map(type => (
                      <option key={type.value} value={type.value}>
                        {type.label}
                      </option>
                    ))}
                  </select>
                </div>
              </>
            )}

            <div className="form-group">
              <label htmlFor="email">Email Address</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                required
                placeholder="your@email.com"
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                type="password"
                id="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                required
                placeholder={isSignUp ? "At least 6 characters" : "••••••••"}
                minLength={isSignUp ? 6 : undefined}
              />
            </div>

            {(error || authError) && (
              <div className="error-box">
                {error || authError}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="submit-btn"
            >
              {loading ? (isSignUp ? 'Creating Account...' : 'Logging in...') : (isSignUp ? 'Create Account' : 'Login')}
            </button>
          </form>

          <div className="auth-toggle">
            <span>
              {isSignUp ? 'Already have an account? ' : "Don't have an account? "}
            </span>
            <button
              type="button"
              onClick={toggleMode}
              className="toggle-btn"
            >
              {isSignUp ? 'Login' : 'Sign Up'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
