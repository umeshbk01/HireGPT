from pydantic import BaseModel

class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    url: str
    description: str
    source: str
