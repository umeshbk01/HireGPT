from pydantic import BaseModel, conlist, Field
from typing import List, Optional

class UserPreferences(BaseModel):
    user_id: str = Field(..., description="UUID of the user")
    desired_roles: List[str] = Field(
        ..., min_items=1,
        description="List of job titles/roles the user is interested in"
    )
    locations: List[str] = Field(
        default_factory=list,
        description="Preferred job locations (cities, regions, etc.)"
    )
    salary_min: Optional[int] = Field(
        None, ge=0, description="Minimum target salary in annual USD/INR"
    )
    salary_max: Optional[int] = Field(
        None, ge=0, description="Maximum target salary in annual USD/INR"
    )
    industries: List[str] = Field(
        default_factory=list,
        description="Preferred industries (e.g. Technology, Finance)"
    )
    experience_years: Optional[float] = Field(
        None, ge=0,
        description="Total years of experience (used to filter seniority)"
    )
    remote_only: bool = Field(
        default=False, description="Whether to include only remote jobs"
    )
    seniority_levels: List[str] = Field(
        default_factory=list,
        description="Allowed seniority levels (e.g. Entry level, Mid-Senior level)"
    )
