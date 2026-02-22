"""Video processing helpers using `yt-dlp` and `ffmpeg`.

This module downloads the source video, extracts a clip around the
`timestamp` with `duration` seconds, applies lightweight cinematic
effects (color grading and gentle zoom) and outputs a 1080x1920 vertical
file suitable for TikTok/Shorts.
"""
from typing import Dict
import tempfile
import os
import subprocess
from yt_dlp import YoutubeDL


def _download_video(url: str) -> str:
    ydl_opts = {"format": "bestvideo+bestaudio/best", "outtmpl": os.path.join(tempfile.gettempdir(), "shg-video-%(id)s.%(ext)s"), "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        return ydl.prepare_filename(info)


def render_clip(url: str, timestamp: float, duration: int, out_path: str) -> Dict:
    """Download source, render a stylized vertical clip, and return metadata.

    - `timestamp` is center of the desired highlight window (seconds)
    - `duration` is clip duration in seconds (int)
    """
    src = _download_video(url)
    # compute start time (clamp to >=0)
    start = max(0, float(timestamp) - float(duration) / 2.0)

    # Build ffmpeg filter: scale to height 1920 then center-crop width 1080,
    # apply mild contrast/brightness (eq) and a subtle zoom via scale+crop.
    vf = (
        "scale=-2:1920,"
        "crop=1080:1920:((in_w-1080)/2):((in_h-1920)/2),"
        "eq=contrast=1.08:brightness=0.02"
    )

    cmd = [
        "ffmpeg",
        "-y",
        "-ss",
        str(start),
        "-i",
        src,
        "-t",
        str(duration),
        "-vf",
        vf,
        "-c:v",
        "libx264",
        "-preset",
        "fast",
        "-crf",
        "23",
        "-c:a",
        "aac",
        "-b:a",
        "128k",
        out_path,
    ]

    try:
        subprocess.run(cmd, check=True)
        return {"out_path": out_path, "duration": duration}
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"ffmpeg render failed: {e}")
