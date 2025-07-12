import os
import shutil
from typing import Dict

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from app.services.resume_parser import parse_resume
from app.models.resume_profile import ResumeProfile

router = APIRouter(prefix="/resume", tags=["resume"])

# In‑memory store of parsed resumes by user_id
_RESUME_STORE: Dict[str, ResumeProfile] = {}

def get_current_user_id() -> str:
    """
    Stub for user auth. Replace with real auth logic (e.g. JWT / OAuth2).
    """
    # For now we'll assume a single test user
    return "user-1234"

@router.post("/upload", response_model=ResumeProfile)
async def upload_resume(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user_id)
):
    # Accept only PDF or DOCX
    if file.content_type not in (
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload PDF or DOCX."
        )

    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, file.filename)

    # Save to temp
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        profile = parse_resume(file_path)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to parse resume: {e}"
        )
    finally:
        # Cleanup
        os.remove(file_path)

    # Store the parsed profile under this user_id
    _RESUME_STORE[user_id] = profile
    return profile

# Helper to allow retrieval from in-memory store in other routers
def get_resume_for_user(user_id: str) -> ResumeProfile:
    resume = _RESUME_STORE.get(user_id)
    if not resume:
        raise HTTPException(404, "Resume not found for user")
    return resume
