"""Heatmap fetching and parsing stubs.

Real implementation should use `yt-dlp` to extract heatmap markers
and return a list of {"time_seconds": float, "intensity": float}.
"""
from typing import List, Dict
from yt_dlp import YoutubeDL


def fetch_heatmap(url: str) -> List[Dict]:
    """Fetch basic metadata and produce a best-effort heatmap.

    Attempts to read chapters/markers from yt-dlp metadata. If none are
    available, returns an evenly-sampled synthetic heatmap with a soft
    peak near the midpoint.
    """
    ydl_opts = {"quiet": True, "skip_download": True}
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)

    duration = info.get("duration") or 0
    chapters = info.get("chapters") or []

    if chapters:
        heatmap = []
        for ch in chapters:
            t = ch.get("start_time") or ch.get("start") or 0
            length = (ch.get("end_time") or ch.get("duration") or 1)
            intensity = min(1.0, (length / max(1.0, duration)) * 1.5)
            heatmap.append({"time_seconds": float(t), "intensity": float(intensity)})
        return heatmap

    samples = max(10, int(min(120, duration // 2 or 10)))
    heatmap = []
    for i in range(samples):
        t = (i / max(1, samples - 1)) * duration
        mid = duration / 2.0 if duration > 0 else samples / 2.0
        dist = abs(t - mid) / (duration / 2.0 if duration > 0 else 1.0)
        intensity = max(0.05, 1.0 - dist) * 0.6
        heatmap.append({"time_seconds": float(t), "intensity": float(intensity)})
    return heatmap
