from pydantic import BaseModel, EmailStr
from typing import List, Optional

class ExperienceItem(BaseModel):
    company: str
    role: str
    duration: str
    details: List[str]

class EducationItem(BaseModel):
    institution: str
    degree: str
    duration: Optional[str]
    cgpa: Optional[str]

class ResumeProfile(BaseModel):
    name: str
    email: EmailStr
    phone: str
    linkedin: Optional[str]
    github: Optional[str]
    education: List[EducationItem]
    experience: List[ExperienceItem]
    skills: List[str]
    projects: Optional[List[str]] = []
    certifications: Optional[List[str]] = []
