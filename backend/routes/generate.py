from fastapi import APIRouter, BackgroundTasks, HTTPException
from pydantic import BaseModel
import uuid
from state import create_job, update_job
from pipeline.runner import run_pipeline

router = APIRouter()


class GenerateRequest(BaseModel):
    url: str


@router.post("/generate")
def generate(req: GenerateRequest, background_tasks: BackgroundTasks):
    if not req.url:
        raise HTTPException(status_code=400, detail={"status": "error", "error": "url required"})
    job_id = str(uuid.uuid4())
    create_job(job_id, {"status": "fetching", "progress": 0, "url": req.url})
    background_tasks.add_task(run_pipeline, job_id, req.url)
    return {"status": "ok", "data": {"job_id": job_id}, "error": None}
