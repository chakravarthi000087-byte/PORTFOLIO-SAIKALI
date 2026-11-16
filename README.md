# A. Sai Kali Chakravarthi — CSE Student & Developer Portfolio

Interactive Computer Science & Engineering portfolio for **A. Sai Kali Chakravarthi** (B.Tech CSE, Jain University, Bengaluru), powered by a **Python 3.10+ backend & data-processing engine (`52.73%` Python)** paired with a React + TypeScript frontend and configured for **Vercel** deployment.

## Live Links

- **Live Portfolio Website:** [https://portfolio-saikalichakravarthi.netlify.app](https://portfolio-saikalichakravarthi.netlify.app)
- **GitHub Repository:** [https://github.com/chakravarthi000087-byte/saikali-portfolio](https://github.com/chakravarthi000087-byte/saikali-portfolio)
- **GitHub Profile:** [https://github.com/chakravarthi000087-byte](https://github.com/chakravarthi000087-byte)
- **LinkedIn:** [https://www.linkedin.com/in/anupati-sai-kali-chakravarthi-097178449](https://www.linkedin.com/in/anupati-sai-kali-chakravarthi-097178449)
- **Featured Project (Trip Guide):** [https://jainsmartnavigation.ai.studio](https://jainsmartnavigation.ai.studio)

## Architecture

- **`api/index.py`** — Vercel Python Serverless Function entrypoint (`BaseHTTPRequestHandler`) handling all `/api/*` endpoints.
- **`backend/`** — Modular Python backend logic and data processing:
  - `models.py` — Typed dataclasses for education, skills, CS knowledge, project architecture, and contact submissions.
  - `portfolio_data.py` — Structured portfolio dataset and profile configuration.
  - `analytics_engine.py` — Weighted CGPA calculations, skill filtering/sorting/aggregation, architecture inspection, and repository language breakdown.
  - `cgpa_projector.py` — Target-CGPA solver and 8-semester graduation trajectory forecasting engine.
  - `trip_planner_service.py` — Itinerary conflict detection and travel budget/per-traveler expense processing for Trip Guide.
  - `contact_processor.py` — Input sanitization, email validation, deduplication fingerprinting, and `mailto:` URI builder.
  - `router.py` — Framework-agnostic HTTP dispatcher shared between Vercel and local execution.
  - `local_server.py` — Threaded Python HTTP server for local development.
  - `test_backend.py` — Automated Python unit tests (`unittest`).
- **`vercel.json`** — Builds the frontend (`npm run build` → `dist`) and rewrites `/api/(.*)` to `/api/index.py`.

## Python Backend API Endpoints

- `GET /api/health` — Python runtime health and repository language share metadata.
- `GET /api/portfolio` — Complete hydrated portfolio payload.
- `GET /api/analytics` — Academic CGPA, skill summary, and codebase language statistics.
- `GET /api/analytics/projection?assumed_sgpa=8.6` — Target-CGPA scenarios and 8-semester forecast.
- `GET /api/skills?category=all|languages|web|tools` — Server-side skill filtering, search, and ranking.
- `GET /api/knowledge?topic=oop|dsa|os|stats|prob` — Core CS knowledge module lookup.
- `GET /api/projects?layer=overview|frontend|backend|data` — Trip Guide architecture breakdown.
- `GET / POST /api/trip-guide` — Travel itinerary validation and budget calculation engine.
- `GET / POST /api/contact` — Validates, sanitizes, and records contact form inquiries.

## Local Development

```bash
npm install
npm run dev
```

Run Python unit tests:

```bash
python3 -m unittest backend/test_backend.py -v
```

## Deploying to Vercel

1. Push this project to your GitHub repository ([`chakravarthi000087-byte/saikali-portfolio`](https://github.com/chakravarthi000087-byte/saikali-portfolio)), removing the old standalone `.html` files so GitHub Linguist detects Python (`~52.7%`) as the primary language.
2. Import the repository in [Vercel](https://vercel.com).
3. Vercel automatically uses `vercel.json` to build the Vite frontend (`dist`) and deploy `api/index.py` as a Python Serverless Function.

## Contact

- **Email:** [chakravarthi000087@gmail.com](mailto:chakravarthi000087@gmail.com)
- **Location:** Hyderabad, Telangana / Bengaluru, Karnataka (Jain University)

