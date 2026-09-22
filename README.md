# KAIFARMS AI

**Smarter Farming. Better Harvests.**

KAIFARMS AI is an agricultural assistant designed to help farmers capture farm information and get practical, cautious AI-supported guidance.

## Working MVP foundation

- Responsive Next.js farmer web app
- FastAPI backend
- Agricultural AI chat endpoint
- Safe demo mode when no API key is configured
- Farmer and farm-record API endpoints
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

Set `OPENAI_API_KEY` in your local environment or deployment secret. **Never commit API keys.** If no key is present, the API uses a safe demo response so the interface remains testable.

## Safety

KAIFARMS AI is an assistant, not a replacement for qualified veterinary or agricultural professionals. The product should escalate serious, uncertain, or high-risk cases to an appropriate expert.

## Roadmap

1. MVP vertical slice
2. Persistent authentication and PostgreSQL records
3. Farmer profiles and farm management
4. Local agricultural knowledge base / RAG
5. Image-assisted crop and livestock diagnosis
6. Expert referral workflow
7. Weather and farm alerts
8. Android application
9. Marketplace and B2B tools
