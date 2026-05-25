# RecruitAI — Recruitment Intelligence Suite

Full-stack recruitment intelligence app powered by Kimi (Moonshot AI).

## Architecture

```
recruit-ai/
├── frontend/          → Cloudflare Pages (static)
│   └── index.html     → SPA with 5 modules
├── backend/           → Render.com (FastAPI)
│   ├── main.py        → API endpoints
│   ├── requirements.txt
│   ├── Procfile
│   └── .env.example
└── README.md
```

## Modules

1. **CV Optimizer** — ATS analysis, keyword gaps, rewrite suggestions
2. **LinkedIn Analyzer** — Profile scoring, headline/bio optimization
3. **Job Analyzer** — Match scoring vs job descriptions
4. **Freelance Search** — Project recommendations by specialty
5. **Interview Trainer** — STAR scripts, roleplay scenarios, negotiation

## Deploy

### Backend (Render.com)

1. Push this repo to GitHub
2. Create new Web Service on Render
3. Point to `backend/` folder (or use monorepo with root `render.yaml`)
4. Set environment variables:
   - `KIMI_API_KEY` — from platform.moonshot.cn
   - `API_SECRET` — your own secret for frontend auth
   - `KIMI_MODEL` — `kimi-latest` (default)

### Frontend (Cloudflare Pages)

1. Upload `frontend/` folder to Cloudflare Pages
2. Or connect GitHub repo with `frontend/` as build directory
3. No build step needed — pure static HTML

### Connect them

In the app, go to Settings (gear icon), enter:
- **Backend URL**: your Render URL (e.g., `https://recruit-ai-api.onrender.com`)
- **API Secret**: the `API_SECRET` you set in Render

## Local Dev

```bash
cd backend
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your keys
uvicorn main:app --reload --port 8000
```

Frontend: just open `frontend/index.html` in a browser.

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/cv/optimize` | ATS analysis + rewrite |
| POST | `/api/linkedin/analyze` | LinkedIn profile scoring |
| POST | `/api/job/match` | Job vs profile match score |
| POST | `/api/freelance/search` | Freelance project recs |
| POST | `/api/interview/prep` | Interview scripts & prep |
| GET | `/health` | Health check |

All endpoints require `x-api-key` header.

## Commercial Notes

- Your Kimi API key stays in the backend. Users never see it.
- You control access via `API_SECRET`.
- You can add rate limiting, user accounts, billing later.
- The frontend is a PWA — users can install on phone/desktop.
