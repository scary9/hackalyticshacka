from fastapi import APIRouter, HTTPException
from state import get_job

router = APIRouter()


@router.get("/status/{job_id}")
def status(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"status": "error", "error": "job not found"})
    return {"status": "ok", "data": {"status": job.get("status"), "progress": job.get("progress", 0)}, "error": None}
