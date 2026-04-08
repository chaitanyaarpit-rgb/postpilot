from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats")
def get_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    total = db.query(models.Post).filter_by(user_id=user.id).count()
    published = db.query(models.Post).filter_by(user_id=user.id, status="published").count()
    pending = db.query(models.Post).filter_by(user_id=user.id, status="pending").count()
    rejected = db.query(models.Post).filter_by(user_id=user.id, status="rejected").count()

    recent = (
        db.query(models.Post)
        .filter_by(user_id=user.id)
        .order_by(models.Post.created_at.desc())
        .limit(5)
        .all()
    )

    profile = db.query(models.UserProfile).filter_by(user_id=user.id).first()

    return {
        "stats": {
            "total_posts": total,
            "published": published,
            "pending_review": pending,
            "rejected": rejected,
        },
        "recent_posts": [
            {"id": p.id, "topic": p.topic, "status": p.status, "created_at": p.created_at}
            for p in recent
        ],
        "profile": {
            "company_name": profile.company_name if profile else "",
            "industry": profile.industry if profile else "",
            "post_hour": profile.post_hour if profile else 9,
            "post_timezone": profile.post_timezone if profile else "UTC",
        } if profile else None,
    }
