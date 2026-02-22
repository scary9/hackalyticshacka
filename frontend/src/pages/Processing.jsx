import { useParams } from 'react-router-dom'
import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import './Processing.css'

export default function Processing() {
  const { jobId } = useParams()
  const navigate = useNavigate()
  const [status, setStatus] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    if (!jobId) return

    const pollStatus = async () => {
      try {
        const response = await fetch(`/api/status/${jobId}`)
        if (!response.ok) {
          throw new Error('Failed to fetch status')
        }

        const data = await response.json()
        setStatus(data.data)

        if (data.data.status === 'complete') {
          setTimeout(() => {
            navigate(`/result/${jobId}`)
          }, 500)
        }
      } catch (err) {
        setError(err.message)
      }
    }

    const interval = setInterval(pollStatus, 2000)
    pollStatus()

    return () => clearInterval(interval)
  }, [jobId, navigate])

  const stages = [
    { name: 'Fetching', key: 'fetching' },
    { name: 'Analyzing', key: 'analyzing' },
    { name: 'Rendering', key: 'rendering' },
    { name: 'Captioning', key: 'captioning' },
  ]

  const getStageStatus = (stageKey) => {
    if (!status) return 'pending'

    if (status.current_stage === stageKey) return 'active'
    if (status.completed_stages?.includes(stageKey)) return 'completed'
    return 'pending'
  }

  return (
    <div className="processing-container">
      <div className="processing-content">
        <h1 className="processing-title">Generating Your Highlight</h1>
        <p className="processing-subtitle">Job ID: {jobId}</p>

        <div className="stages-container">
          {stages.map((stage, index) => {
            const stageStatus = getStageStatus(stage.key)
            return (
              <div key={stage.key} className="stage-wrapper">
                <div className={`stage-pill ${stageStatus}`}>
                  <div className="stage-icon">
                    {stageStatus === 'completed' ? '✓' : stageStatus === 'active' ? '○' : '○'}
                  </div>
                  <span className="stage-name">{stage.name}</span>
                </div>
                {index < stages.length - 1 && <div className="stage-connector"></div>}
              </div>
            )
          })}
        </div>

        {status && (
          <div className="status-details">
            <p className="status-current">
              Current: <strong>{status.current_stage?.replace('_', ' ').toUpperCase()}</strong>
            </p>
            {status.progress && (
              <div className="progress-bar-container">
                <div className="progress-bar">
                  <div
                    className="progress-fill"
                    style={{ width: `${status.progress}%` }}
                  ></div>
                </div>
                <p className="progress-text">{status.progress}%</p>
              </div>
            )}
          </div>
        )}

        {error && (
          <div className="error-container">
            <p className="error-text">Error: {error}</p>
          </div>
        )}

        <div className="spinner-large"></div>
      </div>
    </div>
  )
}
