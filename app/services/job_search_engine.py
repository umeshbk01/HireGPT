import asyncio
from typing import List
import httpx

from app.models.job_posting import JobPosting
from app.config import RAPIDAPI_KEY, LINKEDIN_API_HOST, JSEARCH_API_HOST

# Common RapidAPI header
HEADERS = {"X-RapidAPI-Key": RAPIDAPI_KEY}

async def search_linkedin_jobs(
    title_filter: str,
    location_filter: str,
    limit: int = 10,
    offset: int = 0,
) -> List[JobPosting]:
    url = f"https://{LINKEDIN_API_HOST}/active-jb-24h"
    params = {
        "limit": limit,
        "offset": offset,
        "title_filter": f"\"{title_filter}\"",
        "location_filter": f"\"{location_filter}\"",
    }
    headers = {
        **HEADERS,
        "X-RapidAPI-Host": LINKEDIN_API_HOST,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        items = resp.json().get("data", [])
    jobs = []
    for item in items:
        jobs.append(JobPosting(
            title=item.get("job_title", ""),
            company=item.get("company_name", ""),
            location=item.get("location", ""),
            url=item.get("external_job_url", item.get("job_link", "")),
            description=item.get("description_text", ""),
            source="LinkedIn",
        ))
    return jobs

async def search_indeed_jobs(
    query: str,
    location: str,
    limit: int = 10,
    offset: int = 0,
) -> List[JobPosting]:
    url = f"https://{JSEARCH_API_HOST}/search"
    params = {
        "query": query,
        "location": location,
        "limit": limit,
        "offset": offset,
    }
    headers = {
        **HEADERS,
        "X-RapidAPI-Host": JSEARCH_API_HOST,
    }
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        items = resp.json().get("data", [])
    jobs = []
    for item in items:
        jobs.append(JobPosting(
            title=item.get("job_title", ""),
            company=item.get("employer_name", ""),
            location=", ".join(filter(None, [item.get("job_city"), item.get("job_country")])),
            url=item.get("job_apply_link", item.get("job_link", "")),
            description=item.get("job_description", ""),
            source="Indeed",
        ))
    return jobs

async def search_jobs(
    title: str,
    location: str,
    limit: int = 10,
    offset: int = 0,
) -> List[JobPosting]:
    # Run both searches concurrently
    li_task = asyncio.create_task(search_linkedin_jobs(title, location, limit, offset))
    in_task = asyncio.create_task(search_indeed_jobs(title, location, limit, offset))
    linkedin = await li_task
    indeed = await in_task
    return linkedin + indeed
