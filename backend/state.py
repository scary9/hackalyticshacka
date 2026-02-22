"""Shared in-memory state for job tracking."""

job_store = {}


def create_job(job_id: str, data: dict):
    job_store[job_id] = data


def get_job(job_id: str):
    return job_store.get(job_id)


def update_job(job_id: str, **kwargs):
    job = job_store.setdefault(job_id, {})
    job.update(kwargs)
    return job
