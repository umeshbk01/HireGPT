from fastapi import APIRouter, Query
from typing import List
from app.services.job_search_engine import search_jobs
from app.models.job_posting import JobPosting

router = APIRouter(prefix="/jobs", tags=["jobs"])

@router.get("/search", response_model=List[JobPosting])
async def search_jobs_route(
    title: str = Query(..., description="Job title to search for"),
    location: str = Query(..., description="Location to search in"),
    limit: int = Query(10, ge=1, le=100, description="Number of jobs per source"),
    offset: int = Query(0, ge=0, description="Pagination offset"),
):
    """
    Aggregate jobs from LinkedIn and Indeed via RapidAPI.
    """
    return await search_jobs(title, location, limit, offset)
