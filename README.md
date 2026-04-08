# PostPilot — AI LinkedIn Automation Platform

Any user signs up, describes their business, pastes API keys, and PostPilot runs daily — researching trends, generating content, and publishing to LinkedIn automatically.

## Stack
- Frontend: Next.js 14 + Tailwind CSS
- Backend: FastAPI + SQLAlchemy (SQLite)
- AI: OpenAI GPT-4o + DALL-E 3
- Search: Tavily API
- Scheduling: APScheduler (per-user)
- Auth: JWT + bcrypt

## Quick Start (Local)

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env — set SECRET_KEY and ENCRYPTION_KEY
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
# Paste output as ENCRYPTION_KEY in .env
uvicorn main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

Open http://localhost:3000

## Docker (Recommended)
```bash
cp backend/.env.example backend/.env
# Fill in backend/.env
docker-compose up --build
```

## User Flow
1. Sign up at /login
2. Onboarding: fill business profile → paste API keys
3. Dashboard: see stats, trigger manual generation
4. Review Queue: approve / edit / reject posts before publish
5. Settings: update profile or rotate API keys anytime

## API Keys Each User Needs
| Key | Where to get |
|-----|-------------|
| OpenAI | platform.openai.com/api-keys |
| Tavily | app.tavily.com (free tier) |
| LinkedIn Access Token | linkedin.com/developers/apps |
| LinkedIn Org ID | Your company page URL |
