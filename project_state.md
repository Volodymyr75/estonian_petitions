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
**Current Phase:** Phase 4 (AI Copilot & MCP) is PLANNED.
**Last Update:** June 12, 2026.
**Overall Progress:** 
Foundational data infrastructure and API layers are established. The local DuckDB database was successfully migrated to **MotherDuck** (`estonia_petitions`). The project is successfully linked to GitHub and deployed live on **Vercel**. End-to-end communication from the MotherDuck cloud database to the Vercel Python API, and finally to the React frontend, is fully functional. 

We have successfully completed all core analytical blocks of Phase 2 (Overview, Momentum, Process Metrics) and Phase 3 (Institutional Layer):
1. **Overview Block:** Live KPI metrics, stacked-bar Phase Distribution visualizer, and Recent Platform Activity.
2. **Momentum Block:** Trending active petitions with signature velocity and interactive recharts Sparklines.
3. **Process Metrics Block:** Stage transition durations (bottleneck flow), stalled rates, and an autocomplete-powered vertical timeline log.
4. **Institutional Layer Block:** Riigikogu petition sync, parlamet timeline events, draft bill references, and faction voting support breakdowns.

The immediate next step is building the AI Copilot & MCP layer.

## 3. Completed Phases & Milestones

### Phase 1: Foundation
- Established directory structures (`etl/`, `db/`, `services/`, `src/`, `api/`).
- Designed DuckDB star-schema (`initiatives`, `initiative_snapshots`, `initiative_events`, `riigikogu_votings`).
- Wrote API client wrapper for **Rahvaalgatus API**.
- Created `etl/daily_sync.py` to upsert datasets securely.
- **Result:** Successfully fetched and populated over 1,000 active/archived initiatives into the local `petitions.duckdb`.
- **Migration:** Created a python script to automatically migrate the local `.duckdb` tables to a cloud `MotherDuck` database securely.

### Phase 2: Core Analytics, Process Metrics & Dashboard (Completed)
- Extracted and safely stored 1,000+ historical lifecycle events referencing the primary initiatives.
- Developed `services/analytics.py` and `services/initiatives.py` pulling logic (decoupled to remain MCP-ready).
- Implemented `api/index.py` (FastAPI) mapping decoupled functions to Vercel serverless HTTP routes.
- **Infrastructure:** Set up a global exception handler in FastAPI to return Python stack traces as JSON.
- **Deployment:** Automated CI/CD pipeline set up via GitHub to Vercel.
- **Overview, Momentum, and Process blocks** are fully coded, linked to analytical SQL APIs, and visually styled.
- **Bug Fix:** Resolved FastAPI crash due to missing `get_stalled_initiatives` import in `api/index.py`.

### Phase 3: Institutional Layer (Riigikogu Integration) (Completed)
- Built the API client wrapper `RiigikoguClient` (`etl/clients/riigikogu.py`) to interface with the Riigikogu Open Data API.
- Extended the MotherDuck / local DuckDB schema to include tables for `riigikogu_petitions`, `riigikogu_petition_statuses`, `riigikogu_votings`, and `riigikogu_voting_details`.
- Integrated Riigikogu data sync into the daily automated ETL script (`etl/daily_sync.py`).
- Created an analytical mapping service `services/institutions.py` to link parliamentary proceedings and votes back to civic initiatives using exact `senderReference` UUIDs.
- Updated `generate_api_json.py` to pre-calculate and export static `institutions.json` and `institutions_details.json`.
- Implemented `InstitutionalBlock.jsx` component displaying petition progress in parliament, draft bill timelines, and visual breakdowns of faction votes. Rendered the block in `App.jsx`.


## 4. Known Issues, Errors & Troubleshooting Log

- **`xcrun: error: invalid active developer path`**
  - **Resolution:** Required running `xcode-select --install` in the host terminal to restore python compilation dependencies.

- **Vercel DuckDB MotherDuck Connection Crash (`NotImplementedException: read_only`)**
  - **Context:** Pushing the MotherDuck connection string `md:` to Vercel but failing to load data.
  - **Resolution:** Added conditional logic in database services to remove the `read_only=True` parameter when the path starts with `md:`.

- **GitHub Actions / Vercel Sync Failure (`InvalidInputException: motherduck_duckdb_cpp_init`)**
  - **Context:** The automated daily sync failed with "Your DuckDB version (v1.5.3) is not yet supported by MotherDuck. The latest supported version is v1.5.2." because `requirements.txt` previously used `duckdb>=1.0.0`, allowing the unpinned installation of `1.5.3` which MotherDuck did not yet support. Furthermore, `.github/workflows/daily_sync.yml` was using a manual `pip install duckdb ...` bypassing `requirements.txt`.
  - **Resolution:** Pinned the dependency to exactly `duckdb==1.5.2` in `requirements.txt` and updated `daily_sync.yml` to use `pip install -r requirements.txt` ensuring the locked version is installed on the runner. Added missing `pandas` to `requirements.txt`.

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
    - **Follow-up Feature:** Replaced custom static SVG sparklines with `recharts` for interactive hover tooltips (showing precise daily vote counts and snapshot dates).
    - **Follow-up Feature:** Improved Trending Initiatives layout by allocating more text width and separating the clickable title zone from the interactive chart using a chevron indicator. Added a smooth UI hover effect for better discoverability.
    - **Follow-up Feature:** Fixed Recharts tooltip overlap by pinning it cleanly above the sparkline graphs.
    - **Follow-up Feature:** Completely replaced the sequential "Phase Funnel" with a "Fate of Initiatives" dashboard block. Uses a 4-card grid (Active, Under Review, Done, Total), a horizontal Donut Chart for overall success rate, and a "True Success Funnel" to accurately visualize the cross-sectional success rate without falsely implying sequential conversion.
    - **Architecture Overhaul (Static JSON API):** Hit MotherDuck daily compute limits due to intensive development queries, causing Vercel serverless timeouts ("Loading Civic Data..."). Implemented a Static Site Generation (SSG) approach:
      - Created `generate_api_json.py` to pre-calculate all analytics into static `.json` files.
      - Updated `daily_sync.yml` GitHub Action to automatically generate and commit these JSONs daily.
      - Modified React frontend to fetch `/api_data/*.json` directly via Vercel CDN, eliminating serverless runtime, reducing load times to milliseconds, and permanently bypassing MotherDuck rate limits.
      - **Post-Rollout Fixes:** Restored `phases.json` generation to correctly power the Donut Chart and Funnel. Fixed Python numpy array parsing for `history_array` to ensure historical sparklines render correctly from MotherDuck. Handled React edge-cases for Recharts sparklines when historical data length is exactly 1.
    - **Follow-up Feature (Call to Action):** Added a new "Needs Your Voice (Approaching Deadline)" block directly beneath Trending Initiatives. This queries active (`sign`) petitions with <1000 signatures, sorted by closest deadline. Visually styled identically to Trending but replaces velocity green badges with urgent orange/red badges ("⏳ X days left", "⚠️ X needed") to create a sharp contrast between rapidly growing petitions and those struggling to meet the threshold.
    - **Follow-up Feature (Translations & Footer):** Fully translated the "Fate of Initiatives" block, the donut chart, and funnel into Estonian. Added a new full-width "About this Project" footer block containing the project's tech stack, a link to the GitHub repository, and contact email (`strembov@gmail.com`).
    - **Follow-up Feature (Outcomes Block):** Replaced the list of 10 "Stalled Initiatives" with a split view: "Bureaucratic Blackhole" (Top 5 longest stalled initiatives) vs "Recent Wins" (Top 5 most recently successfully implemented). Modified `analytics.py` and `generate_api_json.py` to calculate these together and export to `outcomes.json`.
    - **Follow-up UI UX Tweak:** Upgraded the Outcomes block metrics to display actionable context. Replaced the generic "updated_at" tracking with real project lifecycle metrics: displaying total collected signatures and exact age in months since creation ("70 months pending" vs "12 months to implement").

> ⚠️ **CRITICAL DEVELOPMENT WORKFLOW NOTE:** Because the GitHub Action (`daily_sync.yml`) now automatically commits static JSON updates directly to the `main` branch every morning, **you must run `git pull --rebase` before beginning any new coding session.** Failure to do so will result in push rejections and merge conflicts on the `/public/api_data/` files. Never push without fetching the latest remote state first!

## 5. Next Steps

### Phase 3: Institutional Layer (Riigikogu Integration) (Completed):
- [x] **Block 3.1: Riigikogu Ingestion & DB Schema**
  - Connect to the Riigikogu Open Data API.
  - Create client in `etl/clients/riigikogu.py` to fetch vote counts, session dates, faction details, and results.
  - Expand tables `riigikogu_votings` and `riigikogu_voting_details` in `petitions.duckdb`.
- [x] **Block 3.2: Analytical Mapping Service**
  - Map parliamentary vote results back to civic initiatives using exact UUID matching.
  - Implement service in `services/institutions.py`.
  - Add to `generate_api_json.py` to export `institutions.json` and `institutions_details.json`.
- [x] **Block 3.3: Parliament Dashboard Block**
  - Create React component showing vote outcome breakdowns, faction behaviors, and timelines for initiatives that reached parliament.
- [x] **Block 3.4: Integration & Verification**

### Future Phases:
- **Phase 4 (AI Copilot & MCP):** Expose existing python `services/` logic as official Model Context Protocol tools for natural-language queries.

