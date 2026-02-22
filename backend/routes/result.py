from fastapi import APIRouter, HTTPException
from state import get_job

router = APIRouter()


@router.get("/result/{job_id}")
def result(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"status": "error", "error": "job not found"})
    if job.get("status") != "complete":
        return {"status": "ok", "data": {"status": "processing"}, "error": None}

    data = {
        "hype_score": job.get("hype_score", 0),
        "caption": job.get("caption", ""),
        "video_url": job.get("video_url", ""),
        "chart_data": job.get("chart_data", []),
    }
    return {"status": "ok", "data": data, "error": None}
