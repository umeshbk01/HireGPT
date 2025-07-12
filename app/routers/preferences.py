from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.models.user_preferences import UserPreferences
from app.routers.resume import get_current_user_id

router = APIRouter(prefix="/preferences", tags=["preferences"])

_PREF_STORE: dict[str, UserPreferences] = {}

@router.post("/", response_model=UserPreferences, status_code=201)
async def create_or_update_preferences(
    prefs: UserPreferences,
    user_id: str = Depends(get_current_user_id)
):
    prefs.user_id = user_id
    _PREF_STORE[user_id] = prefs
    return prefs

@router.get("/", response_model=UserPreferences)
async def get_preferences(user_id: str = Depends(get_current_user_id)):
    prefs = _PREF_STORE.get(user_id)
    if not prefs:
        raise HTTPException(404, "Preferences not found")
    return prefs
