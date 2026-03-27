# AI-First CRM HCP Interaction Module

Production-ready AI-powered CRM workflow for pharmaceutical field reps.

## What You Get

- FastAPI backend with SQLite persistence
- LangGraph agent orchestration
- 5 integrated tools:
  - Log interaction
  - Edit interaction
  - Interaction summary
  - Follow-up recommendations
  - Sales insight extraction
- React + Redux frontend
- End-to-end interaction flow:
  - raw field notes -> AI extraction -> editable form -> save -> timeline

## Project Structure

```text
Ai-crm-hcp/
  backend/
    app/
      agents/
      database/
      models/
      routes/
      schemas/
      services/
      tools/
    requirements.txt
  frontend/
    src/
      components/
      pages/
      redux/
      services/
    package.json
```

## Prerequisites

- Python 3.9+
- Node.js 18+
- npm 9+
- Groq API key (optional for non-LLM API checks, required for AI responses)

## Backend Setup

```powershell
cd C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

Update `.env` with your key:

```env
GROQ_API_KEY=your_real_key_here
```

Run backend:

```powershell
uvicorn app.main:app --reload
```

Backend URLs:

- API root: `http://127.0.0.1:8000/`
- Swagger: `http://127.0.0.1:8000/docs`

## Frontend Setup

```powershell
cd C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\frontend
npm install
copy .env.example .env
npm run dev
```

Frontend URL:

- App: `http://localhost:5173/`

## Environment Files

### backend/.env

```env
ENV=development
HOST=0.0.0.0
PORT=8000
RELOAD=true
DATABASE_URL=sqlite:///./crm.db
GROQ_API_KEY=your_real_key_here
LOG_LEVEL=INFO
```

### frontend/.env

```env
VITE_API_BASE_URL=http://127.0.0.1:8000
```

## API Endpoints

### HCP

- `POST /hcp`
- `GET /hcp`
- `GET /hcp/{hcp_id}`
- `PUT /hcp/{hcp_id}`
- `DELETE /hcp/{hcp_id}`

### Interactions

- `POST /interaction/log`
- `POST /interaction/edit/{interaction_id}`
- `GET /interaction/timeline`
- `GET /interaction/{hcp_id}`

### Agent

- `POST /agent/chat`
- `GET /agent/health`

## Quick Demo Flow

1. Create at least one HCP (via Swagger at `/docs`)
2. Open frontend
3. Paste raw interaction notes in AI panel
4. Click `Analyze with AI`
5. Review auto-filled fields in editor
6. Select HCP
7. Click `Save Interaction`
8. Verify timeline updates

## Troubleshooting (Windows)

### `npm ENOENT ... package.json`

You ran npm from the wrong directory.

Use:

```powershell
npm --prefix C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\frontend run dev
```

### `venv\Scripts\python.exe is not recognized`

You are not inside `backend`.

Use full path or change directory first:

```powershell
cd C:\Users\venuk\OneDrive\Desktop\AIVOA\Ai-crm-hcp\backend
.\venv\Scripts\python.exe test_step14_agent.py
```

### Agent returns key/config errors

Set `GROQ_API_KEY` in `backend/.env` and restart backend.

## Development Notes

- DB file: `backend/crm.db`
- Frontend API base URL uses `VITE_API_BASE_URL`
- CORS is enabled for local development

## Current Status

Completed:

- Backend steps 1 to 15
- Frontend steps 16 to 20
- Full integration committed to `main`

Latest integration commit includes complete frontend implementation.
