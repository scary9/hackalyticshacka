from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from routes import generate, status, result, download

app = FastAPI(title="Stream Highlight Generator")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount outputs as static files
outputs_path = os.path.join(os.path.dirname(__file__), "outputs")
app.mount("/outputs", StaticFiles(directory=outputs_path), name="outputs")

# include routers
app.include_router(generate.router, prefix="/api")
app.include_router(status.router, prefix="/api")
app.include_router(result.router, prefix="/api")
app.include_router(download.router, prefix="/api")


@app.get("/health")
def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
