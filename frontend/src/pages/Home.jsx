import UrlInput from '../components/UrlInput'
import './Home.css'

export default function Home() {
  return (
    <div className="home-container">
      <div className="home-content">
        <div className="hero-section">
          <h1 className="hero-title">Stream Highlight Generator</h1>
          <p className="hero-subtitle">
            Transform any YouTube or Twitch stream into a viral TikTok-ready highlight in seconds
          </p>
          <p className="hero-description">
            Our AI analyzes the entire stream to find the most exciting moment, 
            applies cinematic effects, and generates a punchy caption—all automatically.
          </p>
        </div>

        <div className="input-section">
          <h2 className="input-label">Paste your stream URL</h2>
          <UrlInput />
        </div>

        <div className="features-section">
          <div className="feature-grid">
            <div className="feature-card">
              <div className="feature-icon">📊</div>
              <h3 className="feature-title">Smart Detection</h3>
              <p className="feature-text">
                AI analyzes heatmap data and audio energy to find the peak moment
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">🎬</div>
              <h3 className="feature-title">Cinematic Effects</h3>
              <p className="feature-text">
                Automatic zoom, slow-motion, and professional color grading
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">📱</div>
              <h3 className="feature-title">TikTok Ready</h3>
              <p className="feature-text">
                Vertical 9:16 format, 15 seconds, optimized for all platforms
              </p>
            </div>

            <div className="feature-card">
              <div className="feature-icon">✍️</div>
              <h3 className="feature-title">AI Captions</h3>
              <p className="feature-text">
                Platform-native captions generated based on stream context
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
