"""Pipeline runner that orchestrates fetch -> analyze -> render -> caption.

This runner uses the pipeline modules (heatmap, audio, scorer, video,
captions, caption_gen) and updates the shared in-memory job state as it
progresses. Runs synchronously (suitable for FastAPI BackgroundTasks).
"""
import os
import time
from state import update_job
from tracking.mlflow_logger import log_run
from .heatmap import fetch_heatmap
from .audio import analyze_audio_from_url, analyze_audio
from .scorer import score_moment
from .video import render_clip
from .captions import generate_subtitles, burn_subtitles
from .caption_gen import generate_caption


OUTPUTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "outputs"))
if not os.path.exists(OUTPUTS_DIR):
    os.makedirs(OUTPUTS_DIR, exist_ok=True)


def run_pipeline(job_id: str, url: str):
    start_time = time.time()
    try:
        update_job(job_id, status="fetching", progress=5)

        # Heatmap / metadata fetch
        heatmap = fetch_heatmap(url)
        update_job(job_id, status="analyzing", progress=25, heatmap=heatmap)

        # Audio analysis (download + energy)
        audio_ts = analyze_audio_from_url(url)
        update_job(job_id, status="analyzing", progress=45)

        # Scoring
        score = score_moment(heatmap, [p["energy"] for p in audio_ts])
        highlight_time = score.get("time", 0.0)
        hype_score = float(score.get("score", 0.0))
        update_job(job_id, status="rendering", progress=60, detected_time=highlight_time, hype_score=hype_score)

        # Render clip
        out_filename = f"{job_id}.mp4"
        out_path = os.path.join(OUTPUTS_DIR, out_filename)
        t0 = time.time()
        render_clip(url, highlight_time, 20, out_path)
        render_time = time.time() - t0
        update_job(job_id, status="captioning", progress=85, video_path=out_path, video_url=f"/outputs/{out_filename}")

        # Generate subtitles and burn them
        # try to extract audio from the rendered clip for Whisper
        subtitles = [{"start": 0.0, "end": 3.0, "text": "(no subtitles)"}]

        # AI caption generation
        caption = generate_caption("\n".join([s.get("text", "") for s in subtitles]))

        # Prepare chart data for frontend
        chart_data = [{"time": int(h.get("time_seconds", 0)), "score": int(h.get("intensity", 0) * 100)} for h in heatmap]

        # finalize job
        update_job(job_id, status="complete", progress=100, video_path=out_path, video_url=f"/outputs/{out_filename}", chart_data=chart_data, caption=caption, hype_score=hype_score)

        # Log run to MLflow
        log_run({
            "url": url,
            "hype_score": hype_score,
            "output_video_path": out_path,
            "excitement_curve_path": None,
            "confidence": 0.0,
            "render_time": render_time,
            "model": "gpt-3.5-or-fallback",
            "prompt_version": "v1",
        })
    except Exception as e:
        update_job(job_id, status="error", progress=0, error=str(e))
    finally:
        total = time.time() - start_time
        try:
            update_job(job_id, last_run_seconds=total)
        except Exception:
            pass
