"""Audio analysis using `yt-dlp` to fetch audio and `librosa` to compute RMS.

This module downloads a video's audio (if needed), computes framewise
RMS energy, and returns a normalized time-series (0-100) along with
corresponding timestamps.
"""
from typing import List, Dict
import tempfile
import os
import numpy as np
from yt_dlp import YoutubeDL
import librosa


def _download_audio(url: str) -> str:
    ydl_opts = {"format": "bestaudio/best", "outtmpl": os.path.join(tempfile.gettempdir(), "shg-audio-%(id)s.%(ext)s"), "quiet": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        fname = ydl.prepare_filename(info)
        # change extension to actual audio ext if needed
        if not os.path.exists(fname):
            # try common extensions
            for ext in ("mp3", "m4a", "webm", "wav", "aac"):
                alt = fname + "." + ext
                if os.path.exists(alt):
                    fname = alt
                    break
        return fname


def analyze_audio_from_url(url: str, sr: int = 22050, hop_length: int = 512) -> List[Dict]:
    """Download audio from `url` and return list of {time, energy}.

    Energy is normalized to 0-100.
    """
    audio_path = _download_audio(url)
    try:
        y, _sr = librosa.load(audio_path, sr=sr, mono=True)
        rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_length)[0]
        times = librosa.frames_to_time(np.arange(len(rms)), sr=_sr, hop_length=hop_length)
        # normalize to 0-100
        if rms.max() > 0:
            norm = (rms / rms.max()) * 100.0
        else:
            norm = rms * 0.0
        return [{"time": float(t), "energy": float(e)} for t, e in zip(times, norm)]
    finally:
        # don't delete downloaded file immediately; keep for downstream
        pass


def analyze_audio(file_path: str, sr: int = 22050, hop_length: int = 512) -> List[Dict]:
    """Analyze a local audio file and return energy time-series.

    Returns list of {time, energy} normalized to 0-100.
    """
    y, _sr = librosa.load(file_path, sr=sr, mono=True)
    rms = librosa.feature.rms(y=y, frame_length=2048, hop_length=hop_length)[0]
    times = librosa.frames_to_time(np.arange(len(rms)), sr=_sr, hop_length=hop_length)
    if rms.max() > 0:
        norm = (rms / rms.max()) * 100.0
    else:
        norm = rms * 0.0
    return [{"time": float(t), "energy": float(e)} for t, e in zip(times, norm)]
