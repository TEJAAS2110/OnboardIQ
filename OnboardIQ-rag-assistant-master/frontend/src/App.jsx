import { useState, useEffect, useCallback } from 'react'
import './App.css'
import ChatInterface from './components/chat/ChatInterface'
import { listDocuments, API_BASE_URL } from './services/api'

function App() {
  const [stats, setStats] = useState({
    totalDocs: 0,
    totalChunks: 0,
  })
  const [uploadKey, setUploadKey] = useState(0)
  const [isOnline, setIsOnline] = useState(true)
  const [toast, setToast] = useState(null)

  // Toast notification helper
  const showToast = useCallback((message, type = 'info') => {
    setToast({ message, type })
    setTimeout(() => setToast(null), 4000)
  }, [])

  useEffect(() => {
    loadStats()
    checkHealth()
  }, [uploadKey])

  const loadStats = async () => {
    try {
      const data = await listDocuments()
      setStats({
        totalDocs: data.total_documents,
        totalChunks: data.total_chunks,
      })
      setIsOnline(true)
    } catch (error) {
      console.error('Error loading stats:', error)
      setIsOnline(false)
    }
  }

  const checkHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`)
      setIsOnline(response.ok)
    } catch {
      setIsOnline(false)
    }
  }

  const handleFileUpload = async (event) => {
    const file = event.target.files[0]
    if (!file) return

    const maxSize = 10 * 1024 * 1024 // 10MB
    if (file.size > maxSize) {
      showToast('File too large! Maximum size is 10MB', 'error')
      return
    }

    const uploadBtn = document.querySelector('.upload-btn')
    const originalText = uploadBtn.textContent
    uploadBtn.textContent = '⏳ Uploading...'
    uploadBtn.disabled = true

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await fetch(`${API_BASE_URL}/documents/upload`, {
        method: 'POST',
        body: formData,
      })
      
      if (response.ok) {
        const result = await response.json()
        showToast(
          `Document uploaded! ${result.file_name} — ${result.chunks_created} chunks created`,
          'success'
        )
        setUploadKey(prev => prev + 1)
      } else {
        const error = await response.json()
        showToast('Upload failed: ' + (error.detail || 'Unknown error'), 'error')
      }
    } catch (error) {
      console.error('Upload error:', error)
      showToast('Connection error. Make sure backend is running.', 'error')
      setIsOnline(false)
    } finally {
      uploadBtn.textContent = originalText
      uploadBtn.disabled = false
      event.target.value = '' // Reset input
    }
  }

  const handleRefresh = () => {
    setUploadKey(prev => prev + 1)
    loadStats()
    showToast('Statistics refreshed', 'info')
  }

  return (
    <div className="app-container">
      {/* Toast notification */}
      {toast && (
        <div className={`toast toast-${toast.type}`}>
          <span className="toast-icon">
            {toast.type === 'success' ? '✅' : toast.type === 'error' ? '❌' : 'ℹ️'}
          </span>
          {toast.message}
          <button className="toast-close" onClick={() => setToast(null)}>×</button>
        </div>
      )}

      <div className="sidebar">
        <div>
          <h1 className="app-title">🎯 OnboardIQ</h1>
          <p className="app-subtitle">Intelligent Knowledge Assistant</p>
        </div>

        <div className="stats-card neon-glow">
          <h3>📊 Knowledge Base</h3>
          <div className="stat-item">
            <span className="stat-label">Documents</span>
            <span className="stat-value">{stats.totalDocs}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">Knowledge Chunks</span>
            <span className="stat-value">{stats.totalChunks}</span>
          </div>
          <div className="stat-item">
            <span className="stat-label">System Status</span>
            <span className="stat-value">{isOnline ? '🟢 Online' : '🔴 Offline'}</span>
          </div>
        </div>

        <div className="quick-actions">
          <button 
            className="action-btn"
            onClick={() => window.open(`${API_BASE_URL}/docs`, '_blank')}
            title="View API Documentation"
          >
            📊 API Documentation
          </button>
          <button 
            className="action-btn"
            onClick={handleRefresh}
            title="Refresh statistics"
          >
            🔄 Refresh Statistics
          </button>
          <button 
            className="action-btn"
            onClick={() => {
              if (confirm('Clear all chat history? This cannot be undone.')) {
                window.location.reload()
              }
            }}
            title="Clear chat history"
          >
            🗑️ Clear Chat
          </button>
        </div>

        <div className="upload-section">
          <input
            type="file"
            id="file-upload"
            style={{ display: 'none' }}
            onChange={handleFileUpload}
            accept=".pdf,.docx,.txt,.md,.html"
          />
          <button
            className="upload-btn"
            onClick={() => document.getElementById('file-upload').click()}
          >
            📤 Upload Document
          </button>
          <p style={{ fontSize: '10px', color: 'rgba(255,255,255,0.4)', marginTop: '8px', textAlign: 'center' }}>
            Supports: PDF, DOCX, TXT, MD, HTML (Max 10MB)
          </p>
        </div>

        <div className="footer-section">
          <p style={{ fontSize: '11px', color: 'rgba(255,255,255,0.4)', textAlign: 'center' }}>
            <strong>OnboardIQ v1.0</strong><br/>
            Powered by Advanced RAG<br/>
            Hybrid Search • Multi-Language • Citations
          </p>
        </div>
      </div>

      <div className="main-content">
        <ChatInterface key={uploadKey} isOnline={isOnline} showToast={showToast} />
      </div>
    </div>
  )
}

export default App