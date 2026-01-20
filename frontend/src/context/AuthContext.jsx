import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

// PRESTIGE FIX: One central place for your API link
const API_BASE_URL = process.env.REACT_APP_API_URL || 'https://ushan256-med-vision-ai.hf.space';

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [tokens, setTokens] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    const storedTokens = localStorage.getItem('tokens')
    const storedUser = localStorage.getItem('user')
    
    if (storedTokens && storedUser) {
      try {
        setTokens(JSON.parse(storedTokens))
        setUser(JSON.parse(storedUser))
      } catch (e) {
        localStorage.removeItem('tokens')
        localStorage.removeItem('user')
      }
    }
    setLoading(false)
  }, [])

  const register = async (email, password, firstName, lastName, userType) => {
    try {
      setError(null)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // Increased to 15s for Cloud wake-up
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          email,
          password,
          first_name: firstName,
          last_name: lastName,
          user_type: userType
        }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      if (!response.ok) throw new Error('Registration failed')

      const data = await response.json()
      setTokens({ access_token: data.access_token, refresh_token: data.refresh_token })
      setUser(data.user)
      localStorage.setItem('tokens', JSON.stringify({ access_token: data.access_token, refresh_token: data.refresh_token }))
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    } catch (err) {
      // REALITY CHECK: Generic error messages for production
      let errorMessage = err.message === 'Failed to fetch' 
        ? 'Cannot connect to AI server. It might be waking up—please try again.' 
        : err.message;
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }

  const login = async (email, password) => {
    try {
      setError(null)
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000)
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)
      if (!response.ok) throw new Error('Invalid email or password')

      const data = await response.json()
      setTokens({ access_token: data.access_token, refresh_token: data.refresh_token })
      setUser(data.user)
      localStorage.setItem('tokens', JSON.stringify({ access_token: data.access_token, refresh_token: data.refresh_token }))
      localStorage.setItem('user', JSON.stringify(data.user))
      return data
    } catch (err) {
      let errorMessage = err.message === 'Failed to fetch' 
        ? 'Server is currently warming up. Please wait 30 seconds and try again.' 
        : err.message;
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }

  const logout = async () => {
    const currentTokens = tokens;
    setUser(null)
    setTokens(null)
    localStorage.removeItem('tokens')
    localStorage.removeItem('user')
    
    if (currentTokens) {
      fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${currentTokens.access_token}`
        }
      }).catch(() => {})
    }
  }

  const refreshAccessToken = async () => {
    if (!tokens?.refresh_token) return false
    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: tokens.refresh_token })
      })
      if (!response.ok) { logout(); return false; }
      const data = await response.json()
      const newTokens = { access_token: data.access_token, refresh_token: data.refresh_token }
      setTokens(newTokens)
      localStorage.setItem('tokens', JSON.stringify(newTokens))
      return true
    } catch (err) {
      logout(); return false;
    }
  }

  return (
    <AuthContext.Provider value={{ user, tokens, loading, error, register, login, logout, refreshAccessToken, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth must be used within an AuthProvider')
  return context
}
