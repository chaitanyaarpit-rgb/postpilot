import requests
from datetime import datetime
from sqlalchemy.orm import Session
from app import models
from app.crypto import decrypt


def publish_post_record(post_id: int, user_id: int, db: Session):
    """Publish a post to LinkedIn using user's credentials."""
    post = db.query(models.Post).filter_by(id=post_id, user_id=user_id).first()
    if not post or post.status != "approved":
        return

    keys = db.query(models.UserAPIKeys).filter_by(user_id=user_id).first()
    if not keys:
        return

    token = decrypt(keys.linkedin_access_token_enc)
    org_urn = f"urn:li:organization:{keys.linkedin_org_id}"

    # Upload image if it's a local path; if it's already a URL (Cloudinary), download first
    image_path = post.image_paths[0] if post.image_paths else None
    asset_urn = None
    if image_path:
        if image_path.startswith("http"):
            # Cloudinary URL — download to temp file for LinkedIn upload
            import tempfile
            img_data = requests.get(image_path).content
            with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
                tmp.write(img_data)
                tmp_path = tmp.name
            asset_urn = _upload_image(tmp_path, token, org_urn)
            import os; os.unlink(tmp_path)
        else:
            asset_urn = _upload_image(image_path, token, org_urn)

    # Publish post
    text = post.caption
    if post.hashtags:
        text += "\n\n" + post.hashtags

    payload = {
        "author": org_urn,
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": text},
                "shareMediaCategory": "IMAGE" if asset_urn else "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }

    if asset_urn:
        payload["specificContent"]["com.linkedin.ugc.ShareContent"]["media"] = [
            {"status": "READY", "media": asset_urn, "description": {"text": ""}}
        ]

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    resp = requests.post("https://api.linkedin.com/v2/ugcPosts", headers=headers, json=payload)
    resp.raise_for_status()

    result = resp.json()
    post.status = "published"
    post.published_at = datetime.utcnow()
    post.linkedin_post_id = result.get("id")
    db.commit()


def _upload_image(image_path: str, token: str, org_urn: str) -> str:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
        "X-Restli-Protocol-Version": "2.0.0",
    }
    register_payload = {
        "registerUploadRequest": {
            "recipes": ["urn:li:digitalmediaRecipe:feedshare-image"],
            "owner": org_urn,
            "serviceRelationships": [{"relationshipType": "OWNER", "identifier": "urn:li:userGeneratedContent"}],
        }
    }
    reg_resp = requests.post(
        "https://api.linkedin.com/v2/assets?action=registerUpload",
        headers=headers,
        json=register_payload,
    )
    reg_resp.raise_for_status()
    reg_data = reg_resp.json()

    upload_url = reg_data["value"]["uploadMechanism"][
        "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest"
    ]["uploadUrl"]
    asset = reg_data["value"]["asset"]

    with open(image_path, "rb") as f:
        upload_resp = requests.put(upload_url, data=f, headers={"Authorization": f"Bearer {token}"})
    upload_resp.raise_for_status()
    return asset
