from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    profile = relationship("UserProfile", back_populates="user", uselist=False)
    api_keys = relationship("UserAPIKeys", back_populates="user", uselist=False)
    posts = relationship("Post", back_populates="user")
    weekly_plans = relationship("WeeklyPlan", back_populates="user")


class UserProfile(Base):
    __tablename__ = "user_profiles"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    company_name = Column(String)
    industry = Column(String)
    target_audience = Column(Text)
    competitors = Column(Text)          # comma-separated
    tone = Column(String, default="professional")
    post_hour = Column(Integer, default=9)
    post_timezone = Column(String, default="UTC")
    post_frequency = Column(String, default="daily")
    onboarding_complete = Column(Boolean, default=False)

    user = relationship("User", back_populates="profile")


class UserAPIKeys(Base):
    __tablename__ = "user_api_keys"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    openai_key_enc = Column(Text)
    tavily_key_enc = Column(Text)
    linkedin_access_token_enc = Column(Text)
    linkedin_org_id = Column(String)
    linkedin_client_id = Column(String)
    linkedin_client_secret_enc = Column(Text)

    user = relationship("User", back_populates="api_keys")


class WeeklyPlan(Base):
    __tablename__ = "weekly_plans"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    week_start = Column(String)         # ISO date string
    topics = Column(JSON)               # list of topic dicts
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="weekly_plans")


class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    topic = Column(String)
    content_type = Column(String)       # post | carousel | infographic
    caption = Column(Text)
    hashtags = Column(Text)
    image_paths = Column(JSON)
    status = Column(String, default="pending")  # pending | approved | rejected | published
    scheduled_for = Column(DateTime)
    published_at = Column(DateTime, nullable=True)
    linkedin_post_id = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="posts")
