from fastapi import FastAPI
from app.routers.jobs import router as jobs_router

app = FastAPI(title="AI Job Agent")

app.include_router(jobs_router)

# Optional health check
@app.get("/health")
async def health():
    return {"status": "ok"}
