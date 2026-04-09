import requests
import tempfile
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.crypto import decrypt


def publish_post_record(post_id: int, user_id: int, db: Session):
    """Publish a post to LinkedIn personal profile using w_member_social scope."""
    post = db.query(models.Post).filter_by(id=post_id, user_id=user_id).first()
    if not post or post.status != "approved":
        return

    keys = db.query(models.UserAPIKeys).filter_by(user_id=user_id).first()
    if not keys:
        return

    token = decrypt(keys.linkedin_access_token_enc)
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }

    # Get member ID using userinfo endpoint (works with w_member_social)
    userinfo_resp = requests.get(
        "https://api.linkedin.com/v2/userinfo",
        headers=headers,
    )
    userinfo_resp.raise_for_status()
    member_id = userinfo_resp.json().get("sub")
    author_urn = f"urn:li:person:{member_id}"

    # Build post text
    text = post.caption or ""
    if post.hashtags:
        text += "\n\n" + post.hashtags

    # Publish
    payload = {
        "author": author_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {
            "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
        },
    }

    resp = requests.post(
        "https://api.linkedin.com/v2/ugcPosts",
        headers=headers,
        json=payload,
    )
    resp.raise_for_status()

    result = resp.json()
    post.status = "published"
    post.published_at = datetime.utcnow()
    post.linkedin_post_id = result.get("id", "")
    db.commit()
    print(f"[Publisher] Published to LinkedIn: {result.get('id')}")
