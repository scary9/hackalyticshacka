# Stream Highlight Generator

Scaffolded full-stack starter for the Stream Highlight Generator (React + FastAPI).

Quick start

1. Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

2. Frontend

```bash
cd frontend
npm install
npm run dev
```

APIs

- POST `/api/generate` { url }
- GET `/api/status/{job_id}`
- GET `/api/result/{job_id}`
- GET `/api/download/{job_id}`

This scaffold includes stubbed pipeline implementations to iterate quickly during development.
