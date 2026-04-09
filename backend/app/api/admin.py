from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.auth import get_current_user
from app import models

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/reset-posts")
def reset_posts(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Reset all approved posts back to pending for re-approval."""
    updated = db.query(models.Post).filter_by(user_id=user.id, status="approved").all()
    for post in updated:
        post.status = "pending"
    db.commit()
    return {"reset": len(updated), "message": f"Reset {len(updated)} posts to pending"}
