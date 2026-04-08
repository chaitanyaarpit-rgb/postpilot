"""
Per-user scheduler: runs daily for each active user at their configured time.
"""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from app.database import SessionLocal
from app import models
from app.agents.pipeline import run_pipeline_for_user
import logging

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("scheduler")

scheduler = BackgroundScheduler()


def schedule_all_users():
    """Load all users and schedule their daily jobs."""
    db = SessionLocal()
    try:
        users = db.query(models.User).filter_by(is_active=True).all()
        for user in users:
            if not user.profile or not user.profile.onboarding_complete:
                continue
            _schedule_user(user)
        log.info(f"Scheduled {len(users)} users")
    finally:
        db.close()


def _schedule_user(user):
    profile = user.profile
    job_id = f"user_{user.id}_daily_post"
    scheduler.add_job(
        run_pipeline_for_user,
        CronTrigger(
            hour=profile.post_hour,
            minute=0,
            timezone=profile.post_timezone,
        ),
        args=[user.id],
        id=job_id,
        replace_existing=True,
    )
    log.info(f"Scheduled user {user.id} at {profile.post_hour}:00 {profile.post_timezone}")


def start_scheduler():
    schedule_all_users()
    scheduler.start()
    log.info("Scheduler started")


def stop_scheduler():
    scheduler.shutdown()
    log.info("Scheduler stopped")
