from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.auth import get_current_user
from app import models
from app.agents.pipeline import run_pipeline_for_user

router = APIRouter(prefix="/api/posts", tags=["posts"])


@router.get("/")
def list_posts(status: Optional[str] = None, db: Session = Depends(get_db), user=Depends(get_current_user)):
    q = db.query(models.Post).filter_by(user_id=user.id)
    if status:
        q = q.filter_by(status=status)
    posts = q.order_by(models.Post.created_at.desc()).all()
    return [
        {
            "id": p.id,
            "topic": p.topic,
            "content_type": p.content_type,
            "caption": p.caption,
            "hashtags": p.hashtags,
            "image_paths": p.image_paths,
            "status": p.status,
            "scheduled_for": p.scheduled_for,
            "published_at": p.published_at,
            "linkedin_post_id": p.linkedin_post_id,
            "created_at": p.created_at,
        }
        for p in posts
    ]


@router.post("/{post_id}/approve")
def approve_post(post_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.query(models.Post).filter_by(id=post_id, user_id=user.id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.status = "approved"
    db.commit()
    background_tasks.add_task(publish_approved_post, post_id, user.id)
    return {"status": "approved", "message": "Publishing in background..."}


@router.post("/{post_id}/reject")
def reject_post(post_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.query(models.Post).filter_by(id=post_id, user_id=user.id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    post.status = "rejected"
    db.commit()
    return {"status": "rejected"}


class EditPostRequest(BaseModel):
    caption: Optional[str] = None
    hashtags: Optional[str] = None


@router.patch("/{post_id}")
def edit_post(post_id: int, req: EditPostRequest, db: Session = Depends(get_db), user=Depends(get_current_user)):
    post = db.query(models.Post).filter_by(id=post_id, user_id=user.id).first()
    if not post:
        raise HTTPException(404, "Post not found")
    if req.caption:
        post.caption = req.caption
    if req.hashtags:
        post.hashtags = req.hashtags
    db.commit()
    return {"status": "updated"}


@router.post("/generate-now")
def generate_now(background_tasks: BackgroundTasks, db: Session = Depends(get_db), user=Depends(get_current_user)):
    """Manually trigger content generation for today."""
    background_tasks.add_task(run_pipeline_for_user, user.id)
    return {"status": "started", "message": "Content generation started in background."}


def publish_approved_post(post_id: int, user_id: int):
    from app.database import SessionLocal
    from app.agents.publisher import publish_post_record
    db = SessionLocal()
    try:
        publish_post_record(post_id, user_id, db)
    finally:
        db.close()
