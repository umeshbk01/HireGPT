import re
import os
import fitz  # PyMuPDF
from typing import List
from app.models.resume_profile import ResumeProfile, ExperienceItem, EducationItem

# Regex patterns
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_RE = re.compile(r"(\+?\d[\d\s-]{7,}\d)")
LINKEDIN_RE = re.compile(r"(https?://www\.linkedin\.com/in/\S+)")
GITHUB_RE   = re.compile(r"(https?://github\.com/\S+)")

def extract_text_from_pdf(path: str) -> str:
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text()
    return text

def split_sections(text: str) -> dict:
    """
    Split resume into sections based on common headings.
    Returns dict: {"education": "...", "experience": "...", ...}
    """
    sections = {}
    # Use headings as anchors (case-insensitive)
    headings = ["Education", "Experience", "Technical Skills", "Projects", "Certifications", "Achievements"]
    pattern = r"(" + "|".join(headings) + r")"
    parts = re.split(pattern, text, flags=re.IGNORECASE)
    # parts example: ["", "Education", "....", "Experience", "....", ...]
    for i in range(1, len(parts), 2):
        key = parts[i].strip().lower().replace(" ", "_")
        val = parts[i+1].strip()
        sections[key] = val
    return sections

def parse_education(sec: str) -> List[EducationItem]:
    items = []
    # split lines and look for institute-year-degree patterns
    for line in sec.split("\n"):
        if line.strip():
            # naive split on dash
            parts = [p.strip() for p in line.split("–") if p.strip()]
            inst = parts[0]
            rest = parts[1] if len(parts) > 1 else ""
            # try extract CGPA
            cgpa = None
            m = re.search(r"(\d\.\d+)\s*CGPA", rest)
            if m:
                cgpa = m.group(1)
            items.append(EducationItem(
                institution=inst,
                degree=rest,
                duration=None,
                cgpa=cgpa
            ))
    return items

def parse_experience(sec: str) -> List[ExperienceItem]:
    items = []
    # Split on roles by looking for date patterns or bullet markers
    blocks = re.split(r"\n•", sec)
    current = None
    for block in blocks:
        lines = [l.strip() for l in block.split("\n") if l.strip()]
        if not lines:
            continue
        # First line likely contains role + company + dates
        header = lines[0]
        # try split company & role & duration
        # e.g. "Senior Member of Technical Staff (Java...) May 2025 – Present"
        header_parts = re.split(r"\s{2,}|\s–\s|\s-\s", header)
        company = header_parts[0]
        role = header_parts[1] if len(header_parts) > 1 else ""
        duration = header_parts[-1] if len(header_parts) > 1 else ""
        details = lines[1:]
        items.append(ExperienceItem(
            company=company,
            role=role,
            duration=duration,
            details=details
        ))
    return items

def parse_skills(sec: str) -> List[str]:
    # skills often comma-separated
    skills = []
    for line in sec.split("\n"):
        parts = [s.strip() for s in line.split(",") if s.strip()]
        skills.extend(parts)
    return skills

def parse_simple_list(sec: str) -> List[str]:
    return [l.strip("• ").strip() for l in sec.split("\n") if l.strip()]

def parse_resume(path: str) -> ResumeProfile:
    text = extract_text_from_pdf(path)
    # basic fields
    email = EMAIL_RE.search(text).group(0) if EMAIL_RE.search(text) else ""
    phone = PHONE_RE.search(text).group(0) if PHONE_RE.search(text) else ""
    name = text.split("\n")[0].strip()  # first line
    linkedin = LINKEDIN_RE.search(text).group(0) if LINKEDIN_RE.search(text) else None
    github   = GITHUB_RE.search(text).group(0)   if GITHUB_RE.search(text) else None

    sections = split_sections(text)
    education = parse_education(sections.get("education", ""))
    experience = parse_experience(sections.get("experience", ""))
    skills = parse_skills(sections.get("technical_skills", ""))
    projects = parse_simple_list(sections.get("projects", ""))
    certifications = parse_simple_list(sections.get("certifications", "")) + \
                     parse_simple_list(sections.get("achievements", ""))

    return ResumeProfile(
        name=name,
        email=email,
        phone=phone,
        linkedin=linkedin,
        github=github,
        education=education,
        experience=experience,
        skills=skills,
        projects=projects,
        certifications=certifications
    )
