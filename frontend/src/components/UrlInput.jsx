import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './UrlInput.css'

export default function UrlInput() {
  const [url, setUrl] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setLoading(true)

    if (!url.trim()) {
      setError('Please enter a valid URL')
      setLoading(false)
      return
    }

    try {
      const response = await fetch('/api/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ url: url.trim() }),
      })

      if (!response.ok) {
        const data = await response.json()
        throw new Error(data.detail || 'Failed to generate highlight')
      }

      const data = await response.json()
      console.log('API response:', data)
      
      const jobId = data.data.job_id
      console.log('navigating to jobId:', jobId)
      setLoading(false)

      setUrl('')
      navigate(`/processing/${jobId}`)
    } catch (err) {
      setError(err.message || 'An error occurred. Please try again.')
      setLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="url-input-form">
      <div className="url-input-container">
        <input
          type="url"
          placeholder="Paste your YouTube or Twitch stream URL"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          disabled={loading}
          className="url-input-field"
          required
        />
        <button
          type="submit"
          disabled={loading}
          className="submit-button"
        >
          {loading ? (
            <>
              <span className="spinner"></span>
              Generating...
            </>
          ) : (
            'Generate Highlight'
          )}
        </button>
      </div>
      {error && <div className="error-message">{error}</div>}
    </form>
  )
}
