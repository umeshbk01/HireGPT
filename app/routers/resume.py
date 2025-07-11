import os
import shutil
from fastapi import APIRouter, UploadFile, File, HTTPException
from app.services.resume_parser import parse_resume
from app.models.resume_profile import ResumeProfile

router = APIRouter(prefix="/resume", tags=["resume"])

@router.post("/upload", response_model=ResumeProfile)
async def upload_resume(file: UploadFile = File(...)):
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

    return profile
