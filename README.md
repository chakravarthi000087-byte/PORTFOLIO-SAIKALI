# A. Sai Kali Chakravarthi — Portfolio (Python Backend + React Frontend)

Interactive Computer Science & Engineering portfolio featuring a Python 3.10+ data-processing backend (`backend/` + `api/index.py`) paired with the React frontend, configured for one-click deployment on **Vercel**.

## Architecture

- **`api/index.py`** — Vercel Python Serverless Function entrypoint (`BaseHTTPRequestHandler`) handling all `/api/*` endpoints.
- **`backend/`** — Modular Python backend logic and data processing:
  - `models.py` — Typed dataclasses for education, skills, CS knowledge, project architecture, and contact submissions.
  - `portfolio_data.py` — Structured domain repository.
  - `analytics_engine.py` — Weighted CGPA calculations, skill filtering/sorting/aggregation, architecture inspection, and repository language breakdown.
  - `contact_processor.py` — Input sanitization, email validation, deduplication fingerprinting, and `mailto:` builder.
  - `router.py` — Framework-agnostic HTTP dispatcher shared between Vercel and local execution.
  - `local_server.py` — Threaded Python HTTP server for local development.
- **`vercel.json`** — Configures `npm run build` (`dist/`) and rewrites `/api/(.*)` to `/api/index.py`.

## API Endpoints

- `GET /api/health` — Python runtime health and language share metadata.
- `GET /api/portfolio` — Complete hydrated portfolio payload.
- `GET /api/analytics` — Academic CGPA, skill summary, and codebase language statistics.
- `GET /api/skills?category=all|languages|web|tools` — Server-side skill filtering and ranking.
- `GET /api/knowledge?topic=oop|dsa|os|stats|prob` — Core CS knowledge lookup.
- `GET /api/projects?layer=overview|frontend|backend|data` — Trip Guide architecture breakdown.
- `POST /api/contact` — Validates, sanitizes, and records contact inquiries.

## Local Development

```bash
npm install
npm run dev
```

Run Python unit tests:

```bash
python3 -m unittest backend/test_backend.py
```

## Deploying to Vercel

1. Push this repository to GitHub (remove the old standalone `.html` files if migrating an existing repo so GitHub Linguist recalculates Python as the primary backend language).
2. Import the repository in [Vercel](https://vercel.com).
3. Vercel automatically uses `vercel.json` to build the Vite frontend (`dist`) and deploy `api/index.py` as a Python Serverless Function.
