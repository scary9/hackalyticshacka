# Stream Highlight Generator — GitHub Copilot Prompt

## Project Overview
You are assisting in building an **automated stream highlight generator delivered as a full-stack website**. The system takes a YouTube or Twitch stream URL, detects the most exciting moment using heatmap and audio analysis, clips it, applies cinematic effects, and generates a TikTok-ready 15-second vertical video with an AI-written caption. The entire experience is delivered through a modern, responsive web application with a React frontend and a Python FastAPI backend.

---

## Project Structure
The project is divided into 3 sections:

### Section 1: Data Intelligence
- Fetch and parse the most-replayed heatmap data from a YouTube or Twitch URL using `yt-dlp`
- Analyze audio energy spikes using `librosa` to detect hype moments
- Build a composite hype score combining heatmap peaks and audio signal weights
- Log all timestamps, hype scores, and metadata to a JSON or CSV file for evaluation
- Visualize the excitement curve using `matplotlib` or `plotly`

### Section 2: Video Processing
- Extract the highest-scoring 20-second raw clip using `yt-dlp` and `ffmpeg`
- Apply cinematic effects using `moviepy` or `ffmpeg-python`:
  - Slow-motion on the peak moment
  - Zoom punch-in effect
  - Color grading / contrast enhancement
- Auto-generate subtitles using OpenAI `Whisper` running locally
- Crop and render final output to 9:16 vertical format (1080x1920) for TikTok/Reels/Shorts
- Run output quality sanity checks: validate duration is ~15 seconds, resolution is correct, file size is non-zero

### Section 3: AI Packaging via MCP
- Use MCP (Model Context Protocol) to orchestrate tool calls across the pipeline
- Expose video tools (yt-dlp, ffmpeg), analytics functions, and GenAI caption generation as MCP tools
- Call an LLM (GPT-3.5 or Claude via API) to generate a short, punchy, platform-native TikTok caption based on the clip context
- Display a "Hype Score" confidence metric alongside the output
- Stream pipeline progress back to the frontend via WebSockets or Server-Sent Events so the user sees live status updates
- Log all prompt versions and GenAI outputs for quality tracking and rollback

---

## Website Architecture

### Folder Structure
```
project/
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UrlInput.jsx         # URL input bar with submit button
│   │   │   ├── ProgressTracker.jsx  # Live pipeline stage tracker
│   │   │   ├── ExcitementChart.jsx  # Heatmap curve visualization
│   │   │   ├── VideoPlayer.jsx      # 9:16 video player with download
│   │   │   └── HypeScoreBadge.jsx   # Animated score badge
│   │   ├── pages/
│   │   │   ├── Home.jsx             # Hero + URL input
│   │   │   ├── Processing.jsx       # Progress tracking page
│   │   │   └── Result.jsx           # Video, score, caption output
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── index.html
│   └── vite.config.js
├── backend/
│   ├── main.py                      # FastAPI app entry point
│   ├── routes/
│   │   ├── generate.py              # POST /api/generate
│   │   ├── status.py                # GET /api/status/{job_id}
│   │   ├── result.py                # GET /api/result/{job_id}
│   │   └── download.py              # GET /api/download/{job_id}
│   ├── pipeline/
│   │   ├── heatmap.py               # Heatmap fetching and parsing
│   │   ├── audio.py                 # Audio energy analysis
│   │   ├── scorer.py                # Composite hype scoring
│   │   ├── video.py                 # ffmpeg clip extraction and effects
│   │   ├── captions.py              # Whisper subtitle generation
│   │   └── caption_gen.py           # LLM caption generation
│   ├── tracking/
│   │   └── mlflow_logger.py         # MLflow evaluate integration
│   └── outputs/                     # Rendered video files served statically
```

---

### Frontend Code Instructions

**App.jsx** — use React Router with three routes: `/` (Home), `/processing/:jobId` (Processing), `/result/:jobId` (Result). Store jobId in state and navigate programmatically after form submit.

**UrlInput.jsx** — render a dark-themed input field and a "Generate Highlight" button. On submit, call `POST /api/generate` with the URL, get back the jobId, and navigate to `/processing/:jobId`. Disable the button and show a spinner while the request is in flight.

**ProgressTracker.jsx** — poll `GET /api/status/:jobId` every 2 seconds using `setInterval` inside a `useEffect`. Display four stage pills: Fetching → Analyzing → Rendering → Captioning. Highlight the active stage with a pulsing animation and check completed stages. When status returns `complete`, navigate to `/result/:jobId` automatically. Cancel the interval on component unmount.

**ExcitementChart.jsx** — accept `chartData` as a prop (array of `{time, score}` objects). Render a `recharts` AreaChart with a gradient fill. Mark the peak moment with a vertical `ReferenceLine` and a label. X-axis is time in seconds, Y-axis is hype score 0-100.

**VideoPlayer.jsx** — render a `<video>` element with `autoPlay`, `controls`, and `loop`. Force 9:16 aspect ratio with Tailwind: `className="w-full aspect-[9/16] max-w-sm mx-auto"`. Include a download button that triggers `GET /api/download/:jobId`.

**HypeScoreBadge.jsx** — display the hype score as a large number with a colored ring. Use green for 80+, yellow for 50-79, red for below 50. Animate the number counting up from 0 to the final score on mount using `useState` and `setInterval`.

**Result.jsx** — fetch result data from `GET /api/result/:jobId` on mount. Render ExcitementChart at the top, VideoPlayer in the center, HypeScoreBadge and the AI caption below. Caption should be in a copyable text box with a "Copy for TikTok" button.

---

### Backend Code Instructions

**main.py** — initialize FastAPI app, add CORS middleware allowing all origins for hackathon, mount `/outputs` as a StaticFiles directory, and include all routers from the routes folder.

**routes/generate.py** — accept `{ "url": str }` in the request body. Generate a UUID as the job ID. Store initial job state `{ "status": "fetching", "progress": 0 }` in a global in-memory dict keyed by job ID. Kick off `run_pipeline(job_id, url)` as a FastAPI BackgroundTask. Return `{ "job_id": job_id }` immediately.

**routes/status.py** — look up the job ID in the in-memory dict and return `{ "status": str, "progress": int }`. If job ID not found return 404.

**routes/result.py** — return `{ "hype_score": float, "caption": str, "video_url": str, "chart_data": list }` for a completed job. If job is not yet complete return `{ "status": "processing" }`.

**routes/download.py** — return a `FileResponse` pointing to the output video file path for the given job ID.

**pipeline/heatmap.py** — use `yt-dlp` to extract the heatmap markers from the video metadata. Parse into a list of `{ "time_seconds": float, "intensity": float }` dicts. Update job status to `"fetching"` at start and `"analyzing"` when done.

**pipeline/audio.py** — download the audio track using `yt-dlp`, load with `librosa.load`, compute RMS energy with `librosa.feature.rms`, and return a time-series array normalized 0-100.

**pipeline/scorer.py** — combine heatmap intensity and audio energy arrays into a composite score. Weight heatmap at 60% and audio at 40% by default. Return the timestamp of the highest scoring window and the score value. Update job status to `"rendering"`.

**pipeline/video.py** — use `ffmpeg-python` to download and cut the clip at the target timestamp. Apply slow-motion (0.7x speed) on the peak 3 seconds, zoom punch-in using `zoompan` filter, and color grade with `eq` filter. Render to 1080x1920 (9:16). Update job status to `"captioning"` when done.

**pipeline/captions.py** — run `whisper.load_model("base")` and transcribe the clip audio. Burn subtitles into the video using `ffmpeg` subtitle filter. Save final output to `/outputs/{job_id}.mp4`.

**pipeline/caption_gen.py** — call the LLM API with a strict prompt: `"You are a TikTok content writer. Write a single punchy caption under 150 characters for a gaming highlight clip. Use hype language. Include 2-3 relevant emojis. No hashtags. Example: 'He actually pulled it off 😤🔥 the clutch of the year'. Example: 'No way that just happened 💀 unreal clip'. Caption:"`. Retry once if response exceeds 150 characters.

**tracking/mlflow_logger.py** — wrap each completed pipeline run in `mlflow.start_run()`. Log all params, metrics, and artifacts as defined in the MLflow Evaluate section. Expose a single `log_run(run_data: dict)` function that the pipeline calls at the end.

---

### Full Stack Communication
- Frontend polls `GET /api/status/{job_id}` every 2 seconds to update the progress UI
- On completion, frontend fetches result and renders the video player and caption automatically
- All errors from the backend must return structured JSON: `{ "status": "error", "error": "human readable message" }`
- Job state is stored in a global in-memory Python dict for hackathon simplicity — note this resets on server restart

---

## Tech Stack
- **Frontend:** React, Vite, Tailwind CSS, recharts
- **Backend:** Python 3.10+, FastAPI, Uvicorn
- **Data & Analytics:** `yt-dlp`, `librosa`, `pandas`
- **Video Processing:** `ffmpeg-python`, `moviepy`
- **Speech-to-Text:** `openai-whisper` (local, free)
- **GenAI:** OpenAI API or Anthropic Claude API (GPT-3.5 tier for cost efficiency)
- **Agent Orchestration:** MCP tool-calling or LangChain
- **Experiment Tracking:** `mlflow` with `mlflow.evaluate` for custom metric scoring
- **Version Control:** Git + DVC for versioning video assets

---

## Quality Management Rules
- Always validate the hype score exceeds a minimum confidence threshold before proceeding to video rendering
- If no strong highlight is found, return a graceful message rather than outputting a low-quality clip
- Retry GenAI caption generation if output exceeds character limit or fails tone check
- Log every pipeline run with: source URL, detected timestamp, hype score, model/prompt version, output path
- Display reasoning trace to the user so the system is explainable, not a black box

---

## MLflow Evaluate Integration
- Use `mlflow.evaluate` to score every pipeline run against custom metrics — do not just log parameters passively
- Define the following custom metrics for `mlflow.evaluate`:
  - `hype_score` — composite score (0-100) combining heatmap peak height and audio energy
  - `detection_confidence` — how far the winning moment scored above the threshold
  - `caption_length` — character count of the generated TikTok caption (target: 80-150 chars)
  - `render_success` — binary 1/0 based on output file validation checks
- Log every experiment run with `mlflow.start_run()` wrapping the full pipeline execution
- Use `mlflow.log_params` to record: source URL, hype score weights, LLM model version, prompt version
- Use `mlflow.log_metrics` to record: hype score, detection confidence, render time in seconds
- Use `mlflow.log_artifact` to store: the output video file, the excitement curve chart, and the run log JSON
- Spin up the MLflow UI locally with `mlflow ui` so judges can browse all experiment runs as a live dashboard
- When comparing prompt versions for caption generation, use `mlflow.evaluate` with a custom `caption_quality` scorer that checks tone keywords (hype words present), length compliance, and platform fit

```python
# Example MLflow evaluate usage
import mlflow

def evaluate_pipeline_run(run_data: dict):
    with mlflow.start_run():
        mlflow.log_params({
            "source_url": run_data["url"],
            "llm_model": run_data["model"],
            "prompt_version": run_data["prompt_version"]
        })
        mlflow.log_metrics({
            "hype_score": run_data["hype_score"],
            "detection_confidence": run_data["confidence"],
            "render_time_seconds": run_data["render_time"]
        })
        mlflow.log_artifact(run_data["output_video_path"])
        mlflow.log_artifact(run_data["excitement_curve_path"])
```

---

## Cost vs Quality Guidelines
- Run Whisper locally — never call a paid ASR API
- Use GPT-3.5 or a local Llama 3 model (via Ollama) for caption generation — GPT-4 is unnecessary for this task
- Cache heatmap and audio analysis results so repeat URL lookups don't re-process
- All video processing should use ffmpeg (free) — avoid paid video APIs
- Target cost of <$0.01 per clip in production

---

## MCP Tool Definitions to Implement
```python
# Tool 1: fetch_heatmap(url: str) -> dict
# Fetches and parses most-replayed heatmap data from a stream URL

# Tool 2: analyze_audio(file_path: str) -> dict
# Returns audio energy time-series and detected spike timestamps

# Tool 3: score_moment(heatmap: dict, audio: dict) -> float
# Returns composite hype score between 0-100

# Tool 4: render_clip(url: str, timestamp: float, duration: int) -> str
# Downloads, clips, and applies cinematic effects, returns output file path

# Tool 5: generate_caption(clip_context: str, platform: str) -> str
# Calls LLM to generate a platform-native caption for the clip
```

---

## Copilot Behavior Instructions
- Always write modular, single-responsibility functions
- Add docstrings to every function explaining inputs, outputs, and purpose
- Include try/except error handling on all external API calls and ffmpeg commands
- When suggesting ffmpeg commands, always include `-y` flag to auto-overwrite outputs
- When writing LLM prompts, always specify: platform (TikTok), tone (hype, punchy, short), max character count, and include 2 example outputs in the prompt
- Prefer free/local tools over paid APIs wherever quality is not significantly impacted
- Always wrap pipeline execution in `mlflow.start_run()` and log params, metrics, and artifacts at the end
- Use `mlflow.evaluate` with custom scorers for any function that produces a measurable quality output
- When building React components, use Tailwind utility classes only — no custom CSS files
- All FastAPI routes must return consistent JSON response shapes with `status`, `data`, and `error` fields
- Video player on the result page must enforce 9:16 aspect ratio to match TikTok format
- Never block the FastAPI main thread with video processing — always use background tasks

---

## Demo Flow (for judges)
1. Judge opens the website in a browser and sees a clean hero page with a URL input
2. They paste a YouTube or Twitch stream URL and click "Generate Highlight"
3. A live progress tracker shows each stage: Fetching → Analyzing → Rendering → Captioning
4. The heatmap excitement curve animates onto the screen showing where the peak was detected
5. The cinematic 15-second clip appears in a 9:16 video player and auto-plays
6. The Hype Score badge and AI-generated TikTok caption display below the video
7. Judge clicks "Download for TikTok" and gets the file instantly

---

## VS Code Setup & Execution Guide

### Step 1 — Project Scaffolding
When asked to scaffold the project, Copilot must generate ALL of the following files with working starter code before anything else:

**Run these commands in the VS Code terminal to bootstrap:**
```bash
# Create project root
mkdir stream-highlight-generator && cd stream-highlight-generator

# Scaffold React frontend
npm create vite@latest frontend -- --template react
cd frontend
npm install
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
npm install recharts react-router-dom
cd ..

# Scaffold Python backend
mkdir -p backend/routes backend/pipeline backend/tracking backend/outputs
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install fastapi uvicorn python-multipart yt-dlp librosa ffmpeg-python openai-whisper mlflow anthropic pandas numpy
cd ..
```

### Step 2 — Environment Variables
Create a `.env` file in `/backend` with:
```
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
MLFLOW_TRACKING_URI=./mlruns
```
Create a `.env` file in `/frontend` with:
```
VITE_API_BASE_URL=http://localhost:8000
```

### Step 3 — VS Code Launch Configuration
Create `.vscode/launch.json` in the project root with this exact content so both servers can be launched with F5:
```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "FastAPI Backend",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": ["main:app", "--reload", "--port", "8000"],
      "cwd": "${workspaceFolder}/backend",
      "envFile": "${workspaceFolder}/backend/.env"
    },
    {
      "name": "React Frontend",
      "type": "node",
      "request": "launch",
      "runtimeExecutable": "npm",
      "runtimeArgs": ["run", "dev"],
      "cwd": "${workspaceFolder}/frontend"
    }
  ],
  "compounds": [
    {
      "name": "Full Stack",
      "configurations": ["FastAPI Backend", "React Frontend"]
    }
  ]
}
```

### Step 4 — VS Code Tasks (optional but recommended)
Create `.vscode/tasks.json` to run both servers from the terminal panel:
```json
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Backend",
      "type": "shell",
      "command": "cd backend && source venv/bin/activate && uvicorn main:app --reload --port 8000",
      "group": "build",
      "presentation": { "panel": "dedicated", "reveal": "always" }
    },
    {
      "label": "Start Frontend",
      "type": "shell",
      "command": "cd frontend && npm run dev",
      "group": "build",
      "presentation": { "panel": "dedicated", "reveal": "always" }
    },
    {
      "label": "Start MLflow UI",
      "type": "shell",
      "command": "cd backend && source venv/bin/activate && mlflow ui --port 5000",
      "group": "build",
      "presentation": { "panel": "dedicated", "reveal": "always" }
    }
  ]
}
```

### Step 5 — Tailwind Config
Copilot must update `frontend/tailwind.config.js` to include:
```js
export default {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: { extend: {} },
  plugins: [],
}
```
And add these two lines to `frontend/src/index.css`:
```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### Step 6 — Running the Project
Once set up, the project runs in three steps:
1. Open VS Code, press `Ctrl+Shift+P` → `Tasks: Run Task` → `Start Backend` (runs on http://localhost:8000)
2. Press `Ctrl+Shift+P` → `Tasks: Run Task` → `Start Frontend` (runs on http://localhost:5173)
3. Optionally press `Ctrl+Shift+P` → `Tasks: Run Task` → `Start MLflow UI` (runs on http://localhost:5000)

OR use the compound launch config: press F5 and select **"Full Stack"** to start both servers simultaneously.

### Step 7 — Required VS Code Extensions
Install these extensions for the best experience:
- `ms-python.python` — Python language support
- `ms-python.vscode-pylance` — Python intellisense
- `dbaeumer.vscode-eslint` — JS/React linting
- `esbenp.prettier-vscode` — code formatting
- `bradlc.vscode-tailwindcss` — Tailwind class autocomplete
- `GitHub.copilot` — Copilot autocomplete
- `GitHub.copilot-chat` — Copilot chat panel

---

## First Files Copilot Should Generate
When starting from scratch, always generate files in this exact order:
1. `backend/main.py` — FastAPI app with CORS, static files, and all routers included
2. `backend/routes/generate.py` — POST endpoint that starts the pipeline
3. `backend/routes/status.py` — GET endpoint for job polling
4. `backend/pipeline/heatmap.py` — heatmap fetching logic
5. `backend/pipeline/scorer.py` — composite hype scoring
6. `frontend/src/App.jsx` — React Router setup with all three routes
7. `frontend/src/pages/Home.jsx` — hero page with URL input
8. `frontend/src/components/UrlInput.jsx` — input component with API call
9. `frontend/src/pages/Processing.jsx` — polling progress tracker
10. `frontend/src/pages/Result.jsx` — video player and caption display

Generate each file completely — never use placeholder comments like `// TODO` or `pass` in place of real implementation.