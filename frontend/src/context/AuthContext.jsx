import React, { createContext, useContext, useState, useEffect } from 'react'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [tokens, setTokens] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  // Load tokens and user from localStorage on mount
  useEffect(() => {
    const storedTokens = localStorage.getItem('tokens')
    const storedUser = localStorage.getItem('user')
    
    if (storedTokens && storedUser) {
      try {
        setTokens(JSON.parse(storedTokens))
        setUser(JSON.parse(storedUser))
      } catch (e) {
        console.error('Failed to load stored auth data:', e)
        localStorage.removeItem('tokens')
        localStorage.removeItem('user')
      }
    }
    
    setLoading(false)
  }, [])

  const register = async (email, password, firstName, lastName, userType) => {
    try {
      setError(null)
      
      // Check if backend is reachable
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
      
      const response = await fetch('http://localhost:8000/auth/register', {
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

      if (!response.ok) {
        let errorMessage = 'Registration failed'
        try {
          const data = await response.json()
          errorMessage = data.detail || errorMessage
        } catch (e) {
          errorMessage = `Server error: ${response.status} ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token
      })
      setUser(data.user)
      
      localStorage.setItem('tokens', JSON.stringify({
        access_token: data.access_token,
        refresh_token: data.refresh_token
      }))
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return data
    } catch (err) {
      let errorMessage = err.message
      if (err.name === 'AbortError') {
        errorMessage = 'Request timeout. Please check if the backend server is running on port 8000.'
      } else if (err.message === 'Failed to fetch') {
        errorMessage = 'Unable to connect to server. Please ensure the backend is running on http://localhost:8000'
      }
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }

  const login = async (email, password) => {
    try {
      setError(null)
      
      // Check if backend is reachable
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 10000) // 10 second timeout
      
      const response = await fetch('http://localhost:8000/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
        signal: controller.signal
      })
      
      clearTimeout(timeoutId)

      if (!response.ok) {
        let errorMessage = 'Login failed'
        try {
          const data = await response.json()
          errorMessage = data.detail || errorMessage
        } catch (e) {
          errorMessage = `Server error: ${response.status} ${response.statusText}`
        }
        throw new Error(errorMessage)
      }

      const data = await response.json()
      setTokens({
        access_token: data.access_token,
        refresh_token: data.refresh_token
      })
      setUser(data.user)
      
      localStorage.setItem('tokens', JSON.stringify({
        access_token: data.access_token,
        refresh_token: data.refresh_token
      }))
      localStorage.setItem('user', JSON.stringify(data.user))
      
      return data
    } catch (err) {
      let errorMessage = err.message
      if (err.name === 'AbortError') {
        errorMessage = 'Request timeout. Please check if the backend server is running on port 8000.'
      } else if (err.message === 'Failed to fetch') {
        errorMessage = 'Unable to connect to server. Please ensure the backend is running on http://localhost:8000'
      }
      setError(errorMessage)
      throw new Error(errorMessage)
    }
  }

  const logout = async () => {
    // Clear tokens from localStorage immediately
    setUser(null)
    setTokens(null)
    setError(null)
    localStorage.removeItem('tokens')
    localStorage.removeItem('user')
    
    // Optionally call backend logout endpoint (if implemented)
    // This would invalidate tokens on the server side
    try {
      const storedTokens = localStorage.getItem('tokens')
      if (storedTokens) {
        const tokens = JSON.parse(storedTokens)
        await fetch('http://localhost:8000/auth/logout', {
          method: 'POST',
          headers: { 
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${tokens.access_token}`
          }
        }).catch(() => {
          // Ignore errors - token is already cleared locally
        })
      }
    } catch (e) {
      // Ignore errors - cleanup is done
    }
  }

  const refreshAccessToken = async () => {
    if (!tokens?.refresh_token) return false
    
    try {
      const response = await fetch('http://localhost:8000/auth/refresh', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: tokens.refresh_token })
      })

      if (!response.ok) {
        logout()
        return false
      }

      const data = await response.json()
      const newTokens = {
        access_token: data.access_token,
        refresh_token: data.refresh_token
      }
      setTokens(newTokens)
      localStorage.setItem('tokens', JSON.stringify(newTokens))
      return true
    } catch (err) {
      logout()
      return false
    }
  }

  const value = {
    user,
    tokens,
    loading,
    error,
    register,
    login,
    logout,
    refreshAccessToken,
    isAuthenticated: !!user
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
