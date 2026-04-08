from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from app.database import get_db
from app.auth import get_current_user
from app import models
from app.crypto import encrypt

router = APIRouter(prefix="/api/onboarding", tags=["onboarding"])


class ProfileRequest(BaseModel):
    company_name: str
    industry: str
    target_audience: str
    competitors: str = ""
    tone: str = "professional"
    post_hour: int = 9
    post_timezone: str = "UTC"
    post_frequency: str = "daily"


class APIKeysRequest(BaseModel):
    openai_key: str
    tavily_key: str
    linkedin_access_token: str
    linkedin_org_id: str
    linkedin_client_id: str = ""
    linkedin_client_secret: str = ""


@router.post("/profile")
def save_profile(req: ProfileRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(models.UserProfile).filter_by(user_id=user.id).first()
    if not profile:
        profile = models.UserProfile(user_id=user.id)
        db.add(profile)

    profile.company_name = req.company_name
    profile.industry = req.industry
    profile.target_audience = req.target_audience
    profile.competitors = req.competitors
    profile.tone = req.tone
    profile.post_hour = req.post_hour
    profile.post_timezone = req.post_timezone
    profile.post_frequency = req.post_frequency
    db.commit()
    return {"status": "ok"}


@router.post("/api-keys")
def save_api_keys(req: APIKeysRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    keys = db.query(models.UserAPIKeys).filter_by(user_id=user.id).first()
    if not keys:
        keys = models.UserAPIKeys(user_id=user.id)
        db.add(keys)

    keys.openai_key_enc = encrypt(req.openai_key)
    keys.tavily_key_enc = encrypt(req.tavily_key)
    keys.linkedin_access_token_enc = encrypt(req.linkedin_access_token)
    keys.linkedin_org_id = req.linkedin_org_id
    keys.linkedin_client_id = req.linkedin_client_id
    keys.linkedin_client_secret_enc = encrypt(req.linkedin_client_secret) if req.linkedin_client_secret else ""

    # Mark onboarding complete
    profile = db.query(models.UserProfile).filter_by(user_id=user.id).first()
    if profile:
        profile.onboarding_complete = True

    db.commit()
    return {"status": "ok", "message": "Setup complete. Your automation is now active."}


@router.get("/status")
def onboarding_status(db: Session = Depends(get_db), user=Depends(get_current_user)):
    profile = db.query(models.UserProfile).filter_by(user_id=user.id).first()
    keys = db.query(models.UserAPIKeys).filter_by(user_id=user.id).first()
    return {
        "has_profile": profile is not None,
        "has_keys": keys is not None,
        "onboarding_complete": profile.onboarding_complete if profile else False,
    }
