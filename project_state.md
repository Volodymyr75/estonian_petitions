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
**Last Update:** April 30, 2026.
**Overall Progress:** 
Foundational data infrastructure and API layers are established. The local DuckDB database was successfully migrated to **MotherDuck** (`estonia_petitions`). The project is successfully linked to GitHub and deployed live on **Vercel**. End-to-end communication from the MotherDuck cloud database to the Vercel Python API, and finally to the React frontend, is fully functional. 

We have successfully completed two major analytical dashboard blocks:
1. **Overview Block:** Live KPI metrics, a stacked-bar Phase Distribution visualizer, and an automated Recent Platform Activity summary based on active metadata logs.
2. **Momentum Block:** Shows trending active petitions, their raw signature velocity (+X sig./day), and renders custom SVG Sparklines from parsed 7-day snapshot arrays directly parsed natively via MotherDuck SQL.

The immediate next step is building out the Process metrics.

## 3. Completed Phases & Milestones

### Phase 1: Foundation
- Established directory structures (`etl/`, `db/`, `services/`, `src/`, `api/`).
- Designed DuckDB star-schema (`initiatives`, `initiative_snapshots`, `initiative_events`, `riigikogu_votings`).
- Wrote API client wrapper for **Rahvaalgatus API**.
- Created `etl/daily_sync.py` to upsert datasets securely.
- **Result:** Successfully fetched and populated over 1,000 active/archived initiatives into the local `petitions.duckdb`.
- **Migration:** Created a python script to automatically migrate the local `.duckdb` tables to a cloud `MotherDuck` database securely.

### Phase 2: Core Analytics & Dashboard (In Progress)
- Extracted and safely stored 1,000+ historical lifecycle events referencing the primary initiatives.
- Developed `services/analytics.py` and `services/initiatives.py` pulling logic (decoupled to remain MCP-ready).
- Implemented `api/index.py` (FastAPI) mapping decoupled functions to Vercel serverless HTTP routes.
- **Infrastructure:** Set up a global exception handler in FastAPI to return Python stack traces as JSON.
- **Deployment:** Automated CI/CD pipeline set up via GitHub to Vercel.
- **Block 1 (Overview) & Block 2 (Momentum)** are fully coded, linked to analytical SQL APIs, and visually styled.

## 4. Known Issues, Errors & Troubleshooting Log

- **`xcrun: error: invalid active developer path`**
  - **Resolution:** Required running `xcode-select --install` in the host terminal to restore python compilation dependencies.

- **Vercel DuckDB MotherDuck Connection Crash (`NotImplementedException: read_only`)**
  - **Context:** Pushing the MotherDuck connection string `md:` to Vercel but failing to load data.
  - **Resolution:** Added conditional logic in database services to remove the `read_only=True` parameter when the path starts with `md:`.

- **Vercel / AWS Lambda Environment Crash (`IO Error: Can't find the home directory at ''`)**
  - **Context:** DuckDB attempts to initialize extension space in the user's `$HOME` directory, but AWS Lambda has an empty `HOME` variable.
  - **Resolution:** Forced `os.environ["HOME"] = "/tmp"` universally at the top of the python API modules before importing DuckDB.

- **Missing specific 'Phase' tags defaulting to "Other" in React**
  - **Context:** Rahvaalgatus API uses many internal phase sub-tags (`edit`, `done`, `government`). The React dictionary fallback mapped them all identical generic "Other" strings.
  - **Resolution:** Explicitly added language dictionary lookups and hex color assignments for all derived phase strings (`#8b5cf6` for done, etc.).

- **Sparkline missing data visual context**
  - **Context:** Initial deployment of Momentum block shows flatlines/dots for 7-day sparklines.
  - **Resolution:** Mathematical behavior is correct; the `initiative_snapshots` table currently only possesses 1 day of cron-driven data gathering. Native visual fallback prevents UX crash.

- **Analytics Queries Returning Incorrect or Missing Data ("8 new petitions", "empty trends")**
  - **Context:** The "Recent Platform Activity" query relied solely on `created_at` which is frequently null for older petitions, leading to an inaccurate representation of new data. Additionally, the trends query looked backwards from `current_date()`, but when scraping is paused/delayed, the 7-day window returned no data, causing empty sparklines. The "Latest event" relied on an inactive `initiative_events` table (last updated March 2024).
  - **Resolution:** 
    - Updated the "new petitions" query to fallback to `ingested_at` via `coalesce(created_at, ingested_at)`.
    - Rewrote the trends query to dynamically calculate the 7-day window backwards from the maximum available `snapshot_date` in the `initiative_snapshots` table.
    - Swapped the "Latest Activity" query to retrieve the most recently modified snapshot event directly from the initiatives state.
    - Added a global "Last Updated" timestamp block beneath the dashboard title to clearly indicate the freshness of the UI data.
    - Generated and integrated a custom Estonian-themed favicon to improve aesthetics.
    - **Follow-up Fix:** Re-styled the "Last Updated" text using CSS margins to resolve UI overlapping with the sub-title.
    - **Follow-up Fix:** Realized Rahvaalgatus API natively omits `created_at` for initiatives. Appended an ETL post-processing SQL routine to auto-deduce `created_at` from the oldest timestamp in `initiative_events` to fix the "new initiatives" counter.
    - **Follow-up Fix:** Changed "Trending Initiatives" SQL + Python logic to sort strictly by `velocity` (growth per day) rather than lifetime total signatures, accurately surfacing the *currently* most active petitions.

## 5. Next Steps
- **Dashboard Expansion (Phase 2):** Fully build out the Process metrics block (lifecycle timelines, event funnels).
- **Phase 3 (Institutional Layer):** Integrate the Riigikogu Open Data API. We need to fetch parliamentary voting data and securely link it to initiatives that reached the parliament floor.
- **Phase 4 (AI Copilot & MCP):** Expose existing python `services/` logic as official Model Context Protocol tools.
