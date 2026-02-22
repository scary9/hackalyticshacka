"""Composite hype scoring logic (stubbed).

Combines heatmap and audio signals into a 0-100 score.
"""
from typing import List, Dict


def score_moment(heatmap: List[Dict], audio: List[float], heatmap_weight: float = 0.6, audio_weight: float = 0.4):
    """Return a dict with top timestamp and score."""
    # Simplified: pick the time with highest heatmap intensity
    if not heatmap:
        return {"time": 0.0, "score": 0.0}
    best = max(heatmap, key=lambda h: h["intensity"])
    score = best["intensity"] * 100
    return {"time": best["time_seconds"], "score": score}
