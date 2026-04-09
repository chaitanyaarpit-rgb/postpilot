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


@router.post("/publish-now")
def publish_now(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Force publish all approved posts immediately."""
    from app.agents.publisher import publish_post_record
    posts = db.query(models.Post).filter_by(user_id=user.id, status="approved").all()
    results = []
    for post in posts:
        try:
            publish_post_record(post.id, user.id, db)
            results.append({"id": post.id, "status": "published"})
        except Exception as e:
            results.append({"id": post.id, "status": "failed", "error": str(e)})
    return {"results": results}
def check_keys(db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Check if API keys can be decrypted."""
    from app.crypto import decrypt
    keys = db.query(models.UserAPIKeys).filter_by(user_id=user.id).first()
    if not keys:
        return {"status": "no keys found"}
    results = {}
    for field in ["openai_key_enc", "tavily_key_enc", "linkedin_access_token_enc"]:
        val = getattr(keys, field, None)
        if not val:
            results[field] = "empty"
            continue
        try:
            decrypted = decrypt(val)
            results[field] = f"ok (starts with: {decrypted[:8]}...)"
        except Exception as e:
            results[field] = f"FAILED: {str(e)}"
    return results
