import asyncio
from typing import List
import httpx

from app.models.job_posting import JobPosting
from app.config import RAPIDAPI_KEY, LINKEDIN_API_HOST, JSEARCH_API_HOST

# Common RapidAPI header
HEADERS = {"x-rapidapi-key": RAPIDAPI_KEY, "x-rapidapi-host": LINKEDIN_API_HOST}

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
        "x-rapidapi-key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": LINKEDIN_API_HOST,
    }
    print("Using API key:", RAPIDAPI_KEY)
    print("Using LinkedIn API host:", LINKEDIN_API_HOST)
    async with httpx.AsyncClient() as client:
        resp = await client.get(url, headers=headers, params=params)
        resp.raise_for_status()
        data = resp.json()  # Directly use the list
        if isinstance(data, list):
            items = data
        elif isinstance(data, dict) and "data" in data:
            items = data["data"]
        else:
            print("Unexpected response format:", data)
            items = []
    jobs = []
    for item in items:
        jobs.append(JobPosting(
            title=item.get("title", ""),
            company=item.get("organization", ""),
            location=", ".join(item.get("locations_derived", [])),
            url=item.get("url", ""),
            description=item.get("linkedin_org_description", ""),
            source="LinkedIn",
        ))
    return jobs

# async def search_indeed_jobs(
#     query: str,
#     location: str,
#     limit: int = 10,
#     offset: int = 0,
# ) -> List[JobPosting]:
#     url = f"https://{JSEARCH_API_HOST}/search"
#     params = {
#         "query": query,
#         "location": location,
#         "limit": limit,
#         "offset": offset,
#     }
#     headers = {
#         **HEADERS,
#         "X-RapidAPI-Host": JSEARCH_API_HOST,
#     }
#     async with httpx.AsyncClient() as client:
#         resp = await client.get(url, headers=headers, params=params)
#         resp.raise_for_status()
#         items = resp.json().get("data", [])
#     jobs = []
#     for item in items:
#         jobs.append(JobPosting(
#             title=item.get("job_title", ""),
#             company=item.get("employer_name", ""),
#             location=", ".join(filter(None, [item.get("job_city"), item.get("job_country")])),
#             url=item.get("job_apply_link", item.get("job_link", "")),
#             description=item.get("job_description", ""),
#             source="Indeed",
#         ))
#     return jobs

async def search_jobs(
    title: str,
    location: str,
    limit: int = 10,
    offset: int = 0,
) -> List[JobPosting]:
    # Run both searches concurrently
    li_task = asyncio.create_task(search_linkedin_jobs(title, location, limit, offset))
    # in_task = asyncio.create_task(search_indeed_jobs(title, location, limit, offset))
    linkedin = await li_task
    # indeed = await in_task
    return linkedin
