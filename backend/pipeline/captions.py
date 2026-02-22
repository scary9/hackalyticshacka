"""Subtitle generation using OpenAI Whisper (local) and burning via ffmpeg.

This file exposes two helpers:
- `generate_subtitles(audio_path)` -> list of segments (start,end,text)
- `burn_subtitles(video_path, subtitles, out_path)` -> writes output file
"""
import os
import subprocess
import tempfile
from typing import List, Dict


def _segments_to_srt(segments: List[Dict]) -> str:
    srt_lines = []
    for i, seg in enumerate(segments, start=1):
        start = _format_srt_time(seg.get("start", 0.0))
        end = _format_srt_time(seg.get("end", seg.get("start", 0.0) + 3.0))
        text = seg.get("text", "")
        srt_lines.append(f"{i}\n{start} --> {end}\n{text}\n")
    return "\n".join(srt_lines)


def _format_srt_time(t: float) -> str:
    hrs = int(t // 3600)
    mins = int((t % 3600) // 60)
    secs = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{hrs:02d}:{mins:02d}:{secs:02d},{ms:03d}"


def generate_subtitles(audio_path: str) -> List[Dict]:
    """Run Whisper locally (if installed) and return segments.

    Falls back to a single empty segment on failure.
    """
    try:
        import whisper

        model = whisper.load_model("base")
        res = model.transcribe(audio_path)
        segments = []
        for seg in res.get("segments", []):
            segments.append({"start": seg["start"], "end": seg["end"], "text": seg["text"]})
        return segments
    except Exception:
        return [{"start": 0.0, "end": 3.0, "text": "(no transcription available)"}]


def burn_subtitles(video_path: str, subtitles: List[Dict], out_path: str) -> bool:
    """Burn SRT subtitles into `video_path` producing `out_path`.

    Returns True on success, raises on failure.
    """
    srt_text = _segments_to_srt(subtitles)
    fd, srt_file = tempfile.mkstemp(suffix=".srt")
    os.close(fd)
    with open(srt_file, "w", encoding="utf-8") as f:
        f.write(srt_text)

    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        video_path,
        "-vf",
        f"subtitles={srt_file}",
        "-c:a",
        "copy",
        out_path,
    ]
    try:
        subprocess.run(cmd, check=True)
        return True
    finally:
        try:
            os.remove(srt_file)
        except Exception:
            pass
