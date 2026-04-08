from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.api import auth, onboarding, posts, dashboard
from app.scheduler import start_scheduler, stop_scheduler
import os


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    os.makedirs("output", exist_ok=True)
    start_scheduler()
    yield
    stop_scheduler()


app = FastAPI(title="PostPilot API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        os.getenv("FRONTEND_URL", ""),  # set this in Railway env vars
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(onboarding.router)
app.include_router(posts.router)
app.include_router(dashboard.router)

if os.path.exists("output"):
    app.mount("/output", StaticFiles(directory="output"), name="output")


@app.get("/")
def root():
    return {"message": "PostPilot API", "status": "running"}
