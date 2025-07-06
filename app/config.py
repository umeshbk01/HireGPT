import os
from dotenv import load_dotenv

load_dotenv()

# RapidAPI credentials & hosts
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
LINKEDIN_API_HOST = "linkedin-job-search-api.p.rapidapi.com"
JSEARCH_API_HOST = "jsearch.p.rapidapi.com"

print(RAPIDAPI_KEY)