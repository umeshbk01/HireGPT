from fastapi import FastAPI
from app.routers.jobs import router as jobs_router
from app.routers.resume import router as resume_router
from app.routers.preferences import router as prefs_router
from app.routers.find_jobs import router as find_router
from app.routers.test_llm import router as test_llm_router
app = FastAPI(title="AI Job Agent")

app.include_router(jobs_router)
app.include_router(resume_router)
app.include_router(prefs_router)
app.include_router(find_router)
app.include_router(test_llm_router)
# Optional health check
@app.get("/health")
async def health():
    return {"status": "ok"}
