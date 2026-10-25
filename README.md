# KAIFARMS AI

**Smarter Farming. Better Harvests.**

KAIFARMS AI is an agricultural assistant designed to help farmers capture farm information and get practical, cautious AI-supported guidance.

## Working MVP foundation

- Responsive Next.js farmer web app
- FastAPI backend
- Agricultural AI chat endpoint
- Safe demo mode when no API key is configured
- Farmer and farm-record API endpoints
- Explicit crop, poultry, livestock and automatic assistant routing
- Farm context included in AI prompts when a farm is selected
- Private expert-support requests with urgency, category and contact preferences
- Validated request inputs and clearer AI-provider failure responses
- PostgreSQL-ready Docker Compose environment
- Automated API and web build checks with GitHub Actions

## Run locally

### Docker

```bash
cp .env.example .env
docker compose up --build
```

Web: http://localhost:3000  
API docs: http://localhost:8000/docs  
Health: http://localhost:8000/health

### Without Docker

Backend:

```bash
cd apps/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:

```bash
cd apps/web
npm install
npm run dev
```

Set `NEXT_PUBLIC_API_URL=http://localhost:8000` for the web app.

## AI configuration

Set `OPENAI_API_KEY` in your local environment or deployment secret. The default model is `gpt-6-luna`; override it with `OPENAI_MODEL` if your API account uses a different available model. **Never commit API keys.** If no key is present, the API uses a clearly marked safe demo response; it does not generate real AI advice until a valid key is configured.

## Production setup

1. Copy `.env.example` to `.env` and replace the sample `JWT_SECRET` and database password with unique strong values.
2. Set `ENVIRONMENT=production`, `CORS_ORIGINS` to the exact public web origin, and `NEXT_PUBLIC_API_URL` to the public API base URL (without a trailing slash).
3. Configure a valid `OPENAI_API_KEY` if live AI responses are required.
4. Run `docker compose up --build` and verify `/health`, registration/login, farm records, AI mode routing and referral creation before inviting farmers.
5. Use HTTPS and a managed secret store in production. Do not expose PostgreSQL publicly.

The current repository provides a deployable code foundation, but a public deployment, real expert dispatch, SMS/email notifications and an expert assignment console still require hosting credentials/services and additional implementation.

## Safety

KAIFARMS AI is an assistant, not a replacement for qualified veterinary or agricultural professionals. The product should escalate serious, uncertain, or high-risk cases to an appropriate expert.

## Roadmap

1. MVP vertical slice
2. Persistent authentication and PostgreSQL records
3. Farmer profiles and farm management
4. Local agricultural knowledge base / RAG
5. Image-assisted crop and livestock diagnosis
6. Expert referral dispatch, expert directory and case-status management
7. Weather and farm alerts
8. Android application
9. Marketplace and B2B tools
