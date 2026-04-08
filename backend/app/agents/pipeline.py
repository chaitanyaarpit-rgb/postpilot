"""
Core pipeline: runs per user, uses their own API keys and profile.
"""
import os
import json
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import models
from app.crypto import decrypt


def get_user_context(user_id: int, db: Session) -> dict:
    """Fetch decrypted keys + profile for a user."""
    profile = db.query(models.UserProfile).filter_by(user_id=user_id).first()
    keys = db.query(models.UserAPIKeys).filter_by(user_id=user_id).first()

    if not profile or not keys:
        raise ValueError(f"User {user_id} has incomplete setup")

    return {
        "openai_key": decrypt(keys.openai_key_enc),
        "tavily_key": decrypt(keys.tavily_key_enc),
        "linkedin_token": decrypt(keys.linkedin_access_token_enc),
        "linkedin_org_id": keys.linkedin_org_id,
        "company_name": profile.company_name,
        "industry": profile.industry,
        "target_audience": profile.target_audience,
        "competitors": profile.competitors,
        "tone": profile.tone,
        "context_prompt": f"""
Company: {profile.company_name}
Industry: {profile.industry}
Target Audience: {profile.target_audience}
Competitors: {profile.competitors}
Tone: {profile.tone}
""",
    }


def run_pipeline_for_user(user_id: int):
    """Full pipeline: research → topics → content → images → save as pending posts."""
    db = SessionLocal()
    try:
        ctx = get_user_context(user_id, db)
        _run(user_id, ctx, db)
    except Exception as e:
        print(f"[Pipeline] Error for user {user_id}: {e}")
    finally:
        db.close()


def _run(user_id: int, ctx: dict, db: Session):
    import openai
    from tavily import TavilyClient

    openai.api_key = ctx["openai_key"]
    tavily = TavilyClient(api_key=ctx["tavily_key"])

    # 1. Check if we already have a plan this week
    week_start = datetime.utcnow().strftime("%Y-W%W")
    existing_plan = (
        db.query(models.WeeklyPlan)
        .filter_by(user_id=user_id, week_start=week_start)
        .first()
    )

    if not existing_plan:
        print(f"[Pipeline] Generating weekly plan for user {user_id}")
        topics = _generate_weekly_plan(ctx, tavily, openai)
        plan = models.WeeklyPlan(user_id=user_id, week_start=week_start, topics=topics)
        db.add(plan)
        db.commit()
    else:
        topics = existing_plan.topics

    # 2. Find today's topic
    today = datetime.utcnow().strftime("%A")
    topic = next((t for t in topics if t.get("day", "").lower() == today.lower()), None)
    if not topic:
        print(f"[Pipeline] No topic for {today}, user {user_id}")
        return

    # 3. Check if post already generated today
    today_date = datetime.utcnow().date()
    existing_post = (
        db.query(models.Post)
        .filter(
            models.Post.user_id == user_id,
            models.Post.topic == topic["topic"],
            models.Post.created_at >= datetime(today_date.year, today_date.month, today_date.day),
        )
        .first()
    )
    if existing_post:
        print(f"[Pipeline] Post already generated today for user {user_id}")
        return

    # 4. Generate content
    print(f"[Pipeline] Generating content for: {topic['topic']}")
    post_data, image_paths = _generate_content(topic, ctx, openai, user_id)

    # 5. Save as pending post
    post = models.Post(
        user_id=user_id,
        topic=topic["topic"],
        content_type=topic.get("content_type", "post"),
        caption=post_data.get("caption", ""),
        hashtags=" ".join(post_data.get("hashtags", [])),
        image_paths=image_paths,
        status="pending",
        scheduled_for=datetime.utcnow(),
    )
    db.add(post)
    db.commit()
    print(f"[Pipeline] Post saved as pending for user {user_id}, post id: {post.id}")


def _generate_weekly_plan(ctx: dict, tavily, openai) -> list:
    queries = [
        f"latest trends in {ctx['industry']} 2025",
        f"AI tools for {ctx['target_audience']}",
        f"marketing technology trends {ctx['industry']}",
    ]
    results = []
    for q in queries:
        resp = tavily.search(query=q, max_results=5, search_depth="advanced")
        results.extend(resp.get("results", []))

    raw = "\n\n".join(f"{r['title']}: {r['content']}" for r in results[:12])

    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": f"You are a LinkedIn content strategist. {ctx['context_prompt']}"},
            {"role": "user", "content": f"""Based on this research, create a 7-day LinkedIn content plan.
Research: {raw}

Return JSON with key 'topics' — array of 7 objects:
- day (Monday-Sunday)
- topic (short title)
- angle (unique insight/hook)
- content_type (post | carousel | infographic)
"""},
        ],
        response_format={"type": "json_object"},
    )
    data = json.loads(response.choices[0].message.content)
    return data.get("topics", [])


def _generate_content(topic: dict, ctx: dict, openai, user_id: int) -> tuple:
    from app.agents.content import generate_post_content
    from app.agents.images import generate_post_image

    post_data = generate_post_content(topic, ctx, openai)
    image_paths = generate_post_image(topic, post_data, ctx, user_id, openai)
    return post_data, image_paths
