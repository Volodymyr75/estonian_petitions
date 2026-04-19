# Project State: Estonian Civic Initiatives Analytics

## 1. Project Overview
**Goal:** Build a portfolio-grade, API-first analytics platform tracking civic initiatives in Estonia, their support dynamics, lifecycle events, and institutional follow-ups.
**Core Principle:** No web scraping. The project strictly relies on official APIs and serves as an MCP-ready (Model Context Protocol) backend that can be easily plugged into AI copilots.
**Tech Stack:**
- **Data Engineering / ETL:** Python (`requests`, `pydantic`), intended for scheduled scripts or GitHub Actions.
- **Database:** DuckDB / MotherDuck (isolated `estonia_petitions` cloud database).
- **Backend / API:** Vercel Serverless Functions powered by FastAPI (`api/index.py`).
- **Frontend Dashboard:** React (Vite-based setup in `src/`), styled using modern vanilla CSS (Glassmorphism, dark theme).
- **Deployment:** Vercel (Frontend & API), GitHub (Source control).
- **Languages Supported in UI:** English, Estonian.

## 2. Current Status
**Current Phase:** Phase 2 (Core Analytics & Dashboard) is IN PROGRESS.
**Last Update:** April 19, 2026.
**Overall Progress:** 
Foundational data infrastructure and API layers are established. The local DuckDB database was successfully migrated to **MotherDuck** (`estonia_petitions`). The project is successfully linked to GitHub and deployed live on **Vercel**. End-to-end communication from the MotherDuck cloud database to the Vercel Python API, and finally to the React frontend, is fully functional (MVP Skeleton is complete). We are currently building out the complex analytical blocks (Momentum, Process, etc.) for the dashboard.

## 3. Completed Phases & Milestones

### Phase 1: Foundation
- Established directory structures (`etl/`, `db/`, `services/`, `src/`, `api/`).
- Designed DuckDB star-schema (`initiatives`, `initiative_snapshots`, `initiative_events`, `riigikogu_votings`).
- Wrote API client wrapper for **Rahvaalgatus API**.
- Created `etl/daily_sync.py` to upsert datasets securely.
- **Result:** Successfully fetched and populated over 1,000 active/archived initiatives into the local `petitions.duckdb`.
- **Migration:** Created a python script to automatically migrate the local `.duckdb` tables to a cloud `MotherDuck` database securely.

### Phase 2: Core Analytics & Dashboard (In Progress)
- Extracted and safely stored 1,000+ historical lifecycle events (e.g., sent-to-parliament, milestone-100) referencing the primary initiatives.
- Developed `services/analytics.py` and `services/initiatives.py` pulling logic (completely decoupled from UI to remain MCP-ready).
- Implemented `api/index.py` (FastAPI) mapping decoupled functions to Vercel serverless HTTP routes.
- **Infrastructure:** Set up a global exception handler in FastAPI to return Python stack traces as JSON, fixing silent UI loading hangs.
- **Deployment:** Automated CI/CD pipeline set up via GitHub to Vercel.

## 4. Known Issues, Errors & Troubleshooting Log
This section covers errors encountered during development and how they were resolved to act as a memory bank and context restorer.

- **`xcrun: error: invalid active developer path`**
  - **Context:** Occurred during the first automated execution of Python API scripts on MacOS.
  - **Resolution:** Required running `xcode-select --install` in the host terminal to restore python compilation dependencies.

- **`ImportError: attempted relative import with no known parent package`**
  - **Context:** Triggered when running `python3 etl/daily_sync.py`.
  - **Resolution:** Modified `daily_sync.py` to dynamically inject the project root into `sys.path`.

- **Rahvaalgatus Events API Accept Header (406 Not Acceptable)**
  - **Context:** Querying `https://rahvaalgatus.ee/initiative-events`.
  - **Resolution:** The routing strictly requires `Accept: application/vnd.rahvaalgatus.initiative-event+json; v=1`. Hardcoded this exact header logic.

- **Vercel DuckDB MotherDuck Connection Crash (`NotImplementedException: read_only`)**
  - **Context:** Pushing the MotherDuck connection string `md:` to Vercel but failing to load data.
  - **Cause:** Using `duckdb.connect(DB_PATH, read_only=True)` with MotherDuck is not supported by the DuckDB driver and throws an unhandled 500 exception.
  - **Resolution:** Added conditional logic in database services to remove the `read_only=True` parameter when the path starts with `md:`.

- **Vercel / AWS Lambda Environment Crash (`IO Error: Can't find the home directory at ''`)**
  - **Context:** DuckDB attempts to initialize extension space in the user's `$HOME` directory, but AWS Lambda (Vercel Serverless) has a Read-Only filesystem and an empty `HOME` variable.
  - **Cause:** Since `HOME` is empty `""`, DuckDB immediately throws an IOError before even attempting to connect to MotherDuck. 
  - **Resolution:** Forced `os.environ["HOME"] = "/tmp"` universally at the top of the python API modules before importing DuckDB. `/tmp` is the only writable directory allocated to Vercel serverless functions.

## 5. Next Steps
- **Dashboard Expansion (Phase 2):** Fully build out the Momentum analytics block (growth dynamics) and Process metrics (lifecycle funnel).
- **Phase 3 (Institutional Layer):** Integrate the Riigikogu Open Data API. We need to fetch parliamentary voting data and securely link it to initiatives that reached the parliament floor.
- **Phase 4 (AI Copilot & MCP):** Expose existing python `services/` logic as official Model Context Protocol tools.
- **Phase 5 (Infrastructure):** Setup automated GitHub Actions (`.github/workflows/daily_sync.yml`) to trigger the MotherDuck daily sync independently.
