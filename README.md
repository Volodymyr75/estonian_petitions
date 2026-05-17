# Estonian Civic Initiatives Analytics 🇪🇪

A portfolio-grade, API-first civic data product designed to track, analyze, and visualize public initiatives in Estonia. It monitors support dynamics, lifecycle events, and institutional follow-ups with a focus on transparency and actionable insights.

![Civic Analytics Dashboard](https://img.shields.io/badge/Status-Live-success?style=for-the-badge) ![Vercel](https://img.shields.io/badge/Deployed_on-Vercel-black?style=for-the-badge&logo=vercel) ![React](https://img.shields.io/badge/Frontend-React-blue?style=for-the-badge&logo=react) ![Python](https://img.shields.io/badge/Backend-Python-yellow?style=for-the-badge&logo=python) ![DuckDB](https://img.shields.io/badge/Database-MotherDuck-orange?style=for-the-badge)

## 📌 Project Overview

This platform answers the most critical questions about civic engagement in Estonia:
1. What civic initiatives are active right now?
2. Which initiatives are gaining support the fastest?
3. How do initiatives move through their process lifecycle?
4. Which initiatives are getting stuck in the bureaucratic pipeline, and which are successfully implemented?

The project is built without HTML scraping, strictly relying on official, stable APIs (Rahvaalgatus API), and serves as an **MCP-ready (Model Context Protocol)** backend designed to be plugged into AI copilots.

## 🏛 Architecture & Tech Stack

This project uses a highly optimized **Static Site Generation (SSG)** architecture to bypass cloud database rate limits and serverless cold-start timeouts.

- **Data Engineering / ETL:** Python (`requests`, `pandas`, `duckdb`).
- **Database:** **MotherDuck** (Cloud DuckDB) for fast, analytical querying.
- **Automation:** **GitHub Actions** runs a daily ETL sync that fetches fresh data, runs SQL analytics in MotherDuck, and automatically generates lightweight static JSON API files.
- **Frontend:** **React** (Vite), leveraging modern vanilla CSS (Glassmorphism, dark theme) and `recharts` for interactive sparklines and donut charts.
- **Deployment:** Vercel (Frontend), GitHub (Source control).
- **Languages Supported:** English and Estonian.

## 🚀 Key Features

- **Live Overview KPIs:** Instantly see total initiatives, active petitions, and the overall success funnel.
- **Momentum Tracking:** "Hot Petitions" block identifying initiatives with the highest signature velocity (growth per day).
- **Call to Action (Approaching Deadlines):** A dedicated block surfacing petitions that are close to their deadline but falling short of the 1,000 signature threshold.
- **Fate of Initiatives:** A comprehensive success funnel and donut chart showing the exact cross-sectional success rate of civic actions.
- **Bureaucratic Blackhole vs. Recent Wins:** A stark, side-by-side comparison of the longest-stalled petitions in parliament versus the most recently implemented successes, tracking exact months pending/implemented and total signatures.

## 🛠 Project Status & Roadmap

The project is currently completing **Phase 2**, having successfully established the data pipelines, cloud database migration, and a fully automated, high-performance static JSON dashboard.

- [x] **Phase 1 — Foundation:** DB schema, ETL skeleton, Rahvaalgatus API connection, MotherDuck migration.
- [x] **Phase 2 — Core Analytics:** Initiative snapshots, trending metrics, process funnels, SSG architecture overhaul, outcomes/deadline tracking, and full UI/UX buildout.
- [ ] **Phase 3 — Institutional Layer:** Integrate Riigikogu Open Data API to fetch parliamentary voting data for initiatives that reach the parliament floor.
- [ ] **Phase 4 — AI Copilot & MCP:** Expose the internal Python analytical services as official Model Context Protocol tools for natural-language AI exploration.
- [ ] **Phase 5 — Context Enrichment (Optional):** Infrastructure-related integrations via Tallinn Open Data API.

## ⚠️ Development Workflow

This repository relies on a daily automated GitHub Action (`daily_sync.yml`) that syncs data, generates new `/public/api_data/*.json` files, and commits them directly to the `main` branch. 

> **CRITICAL:** Always run `git pull --rebase` before starting any new development or making commits to avoid merge conflicts with the automated bot commits.

## 📩 Contact

Built to provide transparency and actionable insights into Estonian civic engagement.  
For inquiries, please contact: `strembov@gmail.com`
