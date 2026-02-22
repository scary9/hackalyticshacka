import { useParams, useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
} from 'recharts'
import './Result.css'

function ExcitementChart({ chartData }) {
  if (!chartData || chartData.length === 0) {
    return <div className="chart-placeholder"><p>No data available</p></div>
  }

  // Find the peak moment (highest score)
  const peakPoint = chartData.reduce((max, point) => 
    point.score > max.score ? point : max
  )

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart
        data={chartData}
        margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
      >
        <defs>
          <linearGradient id="excitementGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#646cff" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#646cff" stopOpacity={0.05} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" stroke="rgba(100, 100, 100, 0.2)" />
        <XAxis
          dataKey="time"
          stroke="#888"
          style={{ fontSize: '12px' }}
          label={{ value: 'Time (seconds)', position: 'insideBottomRight', offset: -5, fill: '#888' }}
        />
        <YAxis
          stroke="#888"
          style={{ fontSize: '12px' }}
          label={{ value: 'Hype Score', angle: -90, position: 'insideLeft', fill: '#888' }}
          domain={[0, 100]}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: 'rgba(20, 20, 40, 0.95)',
            border: '1px solid rgba(100, 108, 255, 0.3)',
            borderRadius: '6px',
            color: '#e0e0e0',
          }}
          labelStyle={{ color: '#a0a0a0' }}
          formatter={(value) => value.toFixed(1)}
        />
        <Area
          type="monotone"
          dataKey="score"
          stroke="#646cff"
          strokeWidth={2}
          fill="url(#excitementGradient)"
          dot={false}
        />
        <ReferenceLine
          x={peakPoint.time}
          stroke="#7c3aed"
          strokeDasharray="5 5"
          strokeWidth={2}
          label={{
            value: `Peak: ${peakPoint.score.toFixed(1)}`,
            position: 'top',
            fill: '#7c3aed',
            fontSize: 12,
            offset: 10,
          }}
        />
      </AreaChart>
    </ResponsiveContainer>
  )
}

export default function Result() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [copied, setCopied] = useState(false)

  useEffect(() => {
    if (!jobId) return

    const fetchResult = async () => {
      try {
        const response = await fetch(`/api/result/${jobId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch result')
        }

        const data = await response.json()
        console.log('Result data:', data)
        setResult(data.data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    fetchResult()
  }, [jobId])

  const handleDownload = async () => {
    try {
      const response = await fetch(`http://localhost:8000/api/download/${jobId}`)
      if (!response.ok) {
        throw new Error('Download failed')
      }

      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const link = document.createElement('a')
      link.href = url
      link.download = `highlight-${jobId}.mp4`
      document.body.appendChild(link)
      link.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(link)
    } catch (err) {
      console.error('Download error:', err)
    }
  }

  const handleCopyCaption = async () => {
    if (result?.caption) {
      try {
        await navigator.clipboard.writeText(result.caption)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Copy failed:', err)
      }
    }
  }

  const handleGenerateNew = () => {
    navigate('/')
  }

  if (loading) {
    return (
      <div className="result-container">
        <div className="loading-spinner"></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="result-container">
        <div className="error-state">
          <p className="error-title">Something went wrong</p>
          <p className="error-message">{error}</p>
          <button onClick={handleGenerateNew} className="retry-button">
            Try Again
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="result-container">
      <div className="result-content">
        <h1 className="result-title">Your Highlight is Ready!</h1>

        {result?.video_url && (
          <div className="video-section">
            <div className="video-wrapper">
              <video
                src={`http://localhost:8000${result.video_url}`}
                controls
                autoPlay
                loop
                className="video-player"
              ></video>
            </div>
          </div>
        )}

        {result?.hype_score !== undefined && (
          <div className="score-section">
            <div className="hype-badge">
              <div className="hype-score">{Math.round(result.hype_score)}</div>
              <div className="hype-label">Hype Score</div>
            </div>
          </div>
        )}

        {result?.caption && (
          <div className="caption-section">
            <h2 className="caption-title">AI-Generated Caption</h2>
            <div className="caption-box">
              <p className="caption-text">{result.caption}</p>
              <button
                onClick={handleCopyCaption}
                className={`copy-button ${copied ? 'copied' : ''}`}
              >
                {copied ? '✓ Copied!' : 'Copy for TikTok'}
              </button>
            </div>
          </div>
        )}

        {result?.chart_data && result.chart_data.length > 0 && (
          <div className="chart-section">
            <h2 className="chart-title">Excitement Curve</h2>
            <ExcitementChart chartData={result.chart_data} />
          </div>
        )}

        <div className="action-buttons">
          <button onClick={handleDownload} className="download-button">
            ⬇️ Download Video
          </button>
          <button onClick={handleGenerateNew} className="new-button">
            ✨ Generate Another
          </button>
        </div>

        <div className="job-info">
          <p className="job-id">Job ID: {jobId}</p>
        </div>
      </div>
    </div>
  )
}
