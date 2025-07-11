import re
import fitz  # PyMuPDF
from typing import List, Optional
from app.models.resume_profile import ResumeProfile, ExperienceItem, EducationItem

# Regex patterns for text-based fallback
EMAIL_RE      = re.compile(r"[\w.+-]+@[\w-]+\.[\w.-]+")
PHONE_RE      = re.compile(r"(\+?\d[\d\s-]{7,}\d)")
LINKEDIN_RE   = re.compile(r"(https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9\-_]+")
GITHUB_RE     = re.compile(r"(https?://)?(?:www\.)?github\.com/[A-Za-z0-9\-_]+")
DATE_RANGE_RE = re.compile(r"(\w+\s\d{4})\s*[–-]\s*(Present|\w+\s\d{4})")

# Headings in the resume, in order
HEADINGS = [
    "Education",
    "Experience",
    "Technical Skills",
    "Projects",
    "Certifications & Achievements",
    "Certifications"
]

def extract_text_from_pdf(path: str) -> str:
    """Extract all text from the PDF to a single string."""
    doc = fitz.open(path)
    return "\n".join(page.get_text() for page in doc)

def extract_links_from_pdf(path: str) -> List[str]:
    """
    Scan each page's link annotations and collect all URIs.
    """
    doc = fitz.open(path)
    uris: List[str] = []
    for page in doc:
        for annot in page.annots(types=[fitz.PDF_ANNOT_LINK]) or []:
            uri = annot.info.get("uri")
            if uri:
                uris.append(uri)
    print(uris)
    return uris

def split_sections(text: str) -> dict:
    """
    Identify section headings and split the resume text into sections.
    Returns a dict mapping heading keys to content strings.
    """
    positions = []
    for heading in HEADINGS:
        pattern = rf"(?im)^{re.escape(heading)}:?$"
        for m in re.finditer(pattern, text, flags=re.MULTILINE):
            positions.append((m.start(), heading))
    positions.sort()
    sections = {}
    for idx, (pos, heading) in enumerate(positions):
        start = pos + len(heading)
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(text)
        key = heading.lower().replace(" & ", "_and_").replace(" ", "_")
        sections[key] = text[start:end].strip()
    return sections

def parse_education(sec: str) -> List[EducationItem]:
    items: List[EducationItem] = []
    for block in [b for b in sec.split("\n\n") if b.strip()]:
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines:
            continue
        # Detect CGPA
        cgpa = None
        for line in lines:
            m = re.search(r"(\d\.\d+)(?:/\d+)?\s*CGPA", line)
            if m:
                cgpa = m.group(1)
                break
        # Detect degree
        degree = next((l for l in lines if re.search(r"Bachelor|Master|B\.Tech|M\.Tech|MBA", l, re.I)), "")
        items.append(EducationItem(
            institution=lines[0],
            degree=degree,
            duration=None,
            cgpa=cgpa
        ))
    return items

def parse_experience(sec: str) -> List[ExperienceItem]:
    items: List[ExperienceItem] = []
    lines = [l.strip() for l in sec.splitlines() if l.strip()]
    i = 0
    while i < len(lines):
        line = lines[i]
        date_match = DATE_RANGE_RE.search(line)
        if date_match:
            duration = date_match.group(0)
            # Determine role: text before date on same line, else previous line
            header = line
            role = DATE_RANGE_RE.sub("", header).strip()
            if not role and i > 0:
                role = lines[i - 1]
            # Company: next non-date line
            j = i + 1
            while j < len(lines) and DATE_RANGE_RE.search(lines[j]):
                j += 1
            company = lines[j] if j < len(lines) else ""
            # Details: everything after company until next date entry
            details: List[str] = []
            k = j + 1
            while k < len(lines) and not DATE_RANGE_RE.search(lines[k]):
                details.append(re.sub(r"^[•\-\*]\s*", "", lines[k]))
                k += 1
            items.append(ExperienceItem(
                company=company,
                role=role,
                duration=duration,
                details=details
            ))
            i = k
        else:
            i += 1
    return items

def parse_skills(sec: str) -> List[str]:
    skills: List[str] = []
    for line in sec.splitlines():
        for part in re.split(r"[,;]", line):
            part = part.strip()
            if part:
                skills.append(part)
    return skills

def parse_simple_list(sec: str) -> List[str]:
    return [l.strip("•- ").strip() for l in sec.splitlines() if l.strip()]

def parse_resume(path: str) -> ResumeProfile:
    # 1) Extract full text
    text = extract_text_from_pdf(path)

    # 2) Extract hyperlink URIs for LinkedIn/GitHub
    uris = extract_links_from_pdf(path)
    linkedin: Optional[str] = next((u for u in uris if "linkedin.com/in/" in u.lower()), None)
    github:   Optional[str] = next((u for u in uris if "github.com/" in u.lower()), None)

    # 3) Fallback to text-based regex if no annotated link found
    if not linkedin:
        m = LINKEDIN_RE.search(text)
        linkedin = m.group(0) if m else None
    if not github:
        m = GITHUB_RE.search(text)
        github = m.group(0) if m else None

    # 4) Extract basic fields from text
    name    = text.splitlines()[0].strip()
    email_m = EMAIL_RE.search(text)
    phone_m = PHONE_RE.search(text)

    # 5) Split into sections and parse each
    sections       = split_sections(text)
    education      = parse_education(sections.get("education", ""))
    experience     = parse_experience(sections.get("experience", ""))
    skills         = parse_skills(sections.get("technical_skills", ""))
    projects       = parse_simple_list(sections.get("projects", ""))
    certifications = (
        parse_simple_list(sections.get("certifications_and_achievements", "")) +
        parse_simple_list(sections.get("certifications", ""))
    )

    return ResumeProfile(
        name=name,
        email=email_m.group(0) if email_m else "",
        phone=phone_m.group(0) if phone_m else "",
        linkedin=linkedin,
        github=github,
        education=education,
        experience=experience,
        skills=skills,
        projects=projects,
        certifications=certifications
    )
