from fastapi import FastAPI
from app.routers.jobs import router as jobs_router
from app.routers.resume import router as resume_router
from app.routers.preferences import router as prefs_router

app = FastAPI(title="AI Job Agent")

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(prefs_router)

# Optional health check
@app.get("/health")
async def health():
    return {"status": "ok"}
