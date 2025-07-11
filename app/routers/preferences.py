from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from app.models.user_preferences import UserPreferences

router = APIRouter(prefix="/preferences", tags=["preferences"])

# For now, a simple in-memory store. Swap out for a DB later.
_PREF_STORE: Dict[str, UserPreferences] = {}

def get_current_user_id():
    # Stub: replace with real auth dependency returning user's ID
    return "user-1234"

@router.post("/", response_model=UserPreferences, status_code=201)
async def create_or_update_preferences(
    prefs: UserPreferences,
    user_id: str = Depends(get_current_user_id)
):
    if prefs.user_id != user_id:
        raise HTTPException(403, "Cannot set preferences for another user")
    _PREF_STORE[user_id] = prefs
    return prefs

@router.get("/", response_model=UserPreferences)
async def get_preferences(user_id: str = Depends(get_current_user_id)):
    prefs = _PREF_STORE.get(user_id)
    if not prefs:
        raise HTTPException(404, "Preferences not found")
    return prefs
