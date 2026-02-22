from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
import os
from state import get_job

router = APIRouter()


@router.get("/download/{job_id}")
def download(job_id: str):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail={"status": "error", "error": "job not found"})
    path = job.get("video_path")
    if not path or not os.path.exists(path):
        raise HTTPException(status_code=404, detail={"status": "error", "error": "file not found"})
    return FileResponse(path, media_type="video/mp4", filename=os.path.basename(path))
