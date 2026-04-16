# Project State: Estonian Civic Initiatives Analytics

## 1. Project Overview
**Goal:** Build a portfolio-grade, API-first analytics platform tracking civic initiatives in Estonia, their support dynamics, lifecycle events, and institutional follow-ups.
**Core Principle:** No web scraping. The project strictly relies on official APIs and serves as an MCP-ready (Model Context Protocol) backend that can be easily plugged into AI copilots.
**Tech Stack:**
- **Data Engineering / ETL:** Python (`requests`, `pydantic`), intended for scheduled scripts or GitHub Actions.
- **Database:** DuckDB / MotherDuck (used for local development and cloud data warehousing).
- **Backend / API:** Vercel Serverless Functions powered by FastAPI (`api/index.py`).
- **Frontend Dashboard:** React (Vite-based setup in `src/`), styled using modern vanilla CSS (Glassmorphism, dark theme).
- **Deployment:** Vercel (Frontend & API), GitHub (Source control).
- **Languages Supported in UI:** English, Estonian.

## 2. Current Status
**Current Phase:** Phase 2 (Core Analytics & Dashboard) is COMPLETED.
**Last Update:** April 16, 2026.
**Overall Progress:** Foundational data infrastructure and API layers are established. The DuckDB database successfully ingests real initiative data and their historical events. The initial React dashboard UI has been developed and linked to the FastAPI backend.

## 3. Completed Phases & Milestones

### Phase 1: Foundation
- Established directory structures (`etl/`, `db/`, `services/`, `src/`, `api/`).
- Designed DuckDB star-schema (`initiatives`, `initiative_snapshots`, `initiative_events`, `riigikogu_votings`).
- Wrote API client wrapper for **Rahvaalgatus API**.
- Created `etl/daily_sync.py` to upsert datasets securely.
- **Result:** Successfully fetched and populated over 1,000 active/archived initiatives into the local `petitions.duckdb`.

### Phase 2: Core Analytics & Dashboard
- Extracted and safely stored 1,000+ historical lifecycle events (e.g., sent-to-parliament, milestone-100) referencing the primary initiatives.
- Developed `services/analytics.py` and `services/initiatives.py` pulling logic (completely decoupled from UI to remain MCP-ready).
- Implemented `api/index.py` (FastAPI) mapping decoupled functions to Vercel serverless HTTP routes (`/api/kpis`, `/api/trending`, etc.).
- Developed the sleek React frontend mapping KPI blocks and dynamic UI translations.

## 4. Known Issues, Errors & Troubleshooting Log
This section covers errors encountered during development and how they were resolved to act as a memory bank and context restorer.

- **`xcrun: error: invalid active developer path`**
  - **Context:** Occurred during the first automated execution of Python API scripts on MacOS.
  - **Cause:** MacOS Xcode Command Line Tools were missing or unlinked after an OS update.
  - **Resolution:** Required running `xcode-select --install` in the host terminal to restore python compilation dependencies.

- **`ImportError: attempted relative import with no known parent package`**
  - **Context:** Triggered when running `python3 etl/daily_sync.py` due to the script containing `from .clients.rahvaalgatus import RahvaalgatusClient`.
  - **Cause:** Executing a submodule directly without Python's `-m` flag treats the script as the top-level package, breaking relative imports.
  - **Resolution:** Modified `daily_sync.py` to dynamically inject the project root into `sys.path`: `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`. This allowed absolute imports like `from etl.clients...` to work natively anywhere.

- **`pip install -r` syntax crash**
  - **Context:** User execution of `python3 -m pip install -r ` threw an argument error.
  - **Cause:** Missing the actual file name parameter.
  - **Resolution:** Re-executed with `python3 -m pip install -r requirements.txt`.

- **Rahvaalgatus Events API Accept Header (406 Not Acceptable)**
  - **Context:** When querying `https://rahvaalgatus.ee/initiative-events` to build the event history pipeline.
  - **Cause:** Standard `application/json` Accept headers trigger a server-side 406 Error.
  - **Resolution:** Analysed the actual `openapi.yaml` from their GitHub. The routing strictly requires `Accept: application/vnd.rahvaalgatus.initiative-event+json; v=1`. Hardcoded this exact header logic inside `etl/clients/rahvaalgatus.py`.

## 5. Next Steps
- **Phase 3 (Institutional Layer):** Integrate the Riigikogu Open Data API. We need to fetch parliamentary voting data and securely link it to initiatives that reached the parliament floor.
- **Phase 4 (AI Copilot & MCP):** Expose existing python `services/` logic as official Model Context Protocol tools so LLMs can interact with the DB directly.
- **Phase 5 (Infrastructure):** Setup automated GitHub Actions (`.github/workflows/daily_sync.yml`) to trigger the MotherDuck daily sync independently.
