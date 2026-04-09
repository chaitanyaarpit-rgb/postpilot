import requests
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
        "LinkedIn-Version": "202401",
    }

    # Get member ID
    me_resp = requests.get("https://api.linkedin.com/v2/me", headers=headers)
    print(f"[Publisher] me response: {me_resp.status_code} {me_resp.text}")
    me_resp.raise_for_status()
    member_id = me_resp.json().get("id")
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
    print(f"[Publisher] ugcPosts response: {resp.status_code} {resp.text}")
    resp.raise_for_status()

    result = resp.json()
    post.status = "published"
    post.published_at = datetime.utcnow()
    post.linkedin_post_id = result.get("id", "")
    db.commit()
    print(f"[Publisher] Published to LinkedIn: {result.get('id')}")
