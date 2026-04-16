# Estonian Civic Initiatives Analytics

## Project overview

Estonian Civic Initiatives Analytics is a portfolio-grade civic data product focused on public initiatives in Estonia.

The project is designed as an API-first analytics platform that combines:
- data engineering,
- automation,
- dashboard analytics,
- and an AI copilot layer.

The product tracks civic initiatives, their support dynamics, process events, and their institutional follow-up.

This project must be built without HTML scraping.
Only official or stable APIs should be used.

## Core idea

The platform should answer four main questions:

1. What civic initiatives are active right now?
2. Which initiatives are gaining support the fastest?
3. How do initiatives move through their process lifecycle?
4. Which initiatives reach institutional or parliamentary context?

The project should feel like a real data product, not a demo dashboard.

## Product layers

### 1. Core civic layer

Primary source: **Rahvaalgatus API**

This is the main dataset and the heart of the project.

Use it for:
- initiative metadata,
- phases and statuses,
- signatures and support counts,
- initiative statistics,
- process events,
- recent momentum and trending logic.

This layer powers the majority of the ETL, analytics, and dashboard.

### 2. Institutional layer

Secondary source: **Riigikogu Open Data API**

This layer adds institutional context.

Use it for:
- parliamentary voting data,
- related institutional actions,
- follow-up context for initiatives that reach parliament,
- broader civic-to-institution analytics.

This layer should enrich the core civic dataset rather than replace it.

### 3. Context layer

Optional source: **Tallinn Open Data API**

This layer is not part of the MVP core.
Use it only for a focused enrichment module related to infrastructure initiatives.

Examples:
- transport,
- roads,
- construction,
- municipal services,
- urban planning context.

Do not let this layer overload the main civic narrative.

## What is excluded

The project should **not** include:
- HTML scraping,
- anti-bot workarounds,
- election datasets,
- historical TEHIK or health datasets as a main product direction,
- random unrelated open data just to make the project look bigger.

The product must stay conceptually focused.

## Main product concept

This is a **civic intelligence platform**.

The user should be able to:
- monitor active initiatives,
- see support momentum,
- explore process timelines,
- understand which initiatives move into institutional space,
- inspect related parliamentary context,
- ask natural-language questions through an AI analytics copilot.

## Target positioning

This project should be portfolio-ready for roles related to:
- data analytics,
- data engineering,
- civic tech,
- automation,
- AI-assisted analytics.

The final presentation should communicate:
- reliable API-based ingestion,
- historical data modeling,
- automation pipelines,
- analytics and visualization,
- AI-based exploration.

## Suggested stack

- Python for ETL and data processing
- DuckDB or MotherDuck for analytics storage
- React for frontend dashboard
- GitHub Actions for scheduled sync
- optional lightweight API or static JSON delivery for frontend data
- LLM-based analytics copilot for natural-language queries and insights

Keep the stack practical and portfolio-oriented.

## MCP readiness

This project should be designed so that a Model Context Protocol (MCP) server can be added later without major refactoring.

MCP is **not required for MVP**, but the architecture should be prepared for it from the beginning.

### Goal of future MCP integration

A future MCP server should act as a thin adapter layer between:
- the analytics database,
- the internal service functions,
- and external AI clients or assistants.

The MCP layer should not replace ETL, storage, or dashboard logic.
It should expose selected project capabilities in a structured and safe way.

### MCP design principles

The system should be implemented so that business logic is separated from:
- UI components,
- ETL scripts,
- and one-off SQL written directly inside the frontend.

Analytics and data access logic should live in dedicated internal modules such as:
- `services/analytics.py`
- `services/initiatives.py`
- `services/institutions.py`
- `services/insights.py`
- `services/context.py`

These internal functions should later be easy to wrap as MCP tools.

### Future MCP capabilities

The future MCP server may expose three categories of capabilities:

#### 1. Tools

Model-callable actions with typed inputs and outputs.

Examples:
- `get_overview_kpis`
- `get_trending_initiatives`
- `get_initiative_timeline`
- `get_phase_funnel`
- `get_recent_institutional_updates`
- `get_infrastructure_context`

These tools should be designed as narrow, explicit, schema-friendly operations.

#### 2. Resources

Read-only contextual data that can be loaded by AI applications.

Examples:
- database schema summary,
- initiative glossary,
- category definitions,
- dashboard metric definitions,
- latest weekly report,
- selected initiative detail records.

These resources should be treated as passive context, not executable actions.

#### 3. Prompts

Reusable domain workflows for AI clients.

Examples:
- explain current dashboard KPIs,
- summarize weekly civic activity,
- compare initiative momentum across categories,
- inspect institutional follow-up of one initiative.

These prompts should be optional and should build on top of existing tools and resources.

### Read-only first strategy

The first MCP version should be read-only.

It should focus on:
- querying analytics,
- retrieving initiative details,
- reading context resources,
- and generating structured analytical summaries.

Administrative or write actions should be added only later and should be clearly separated from read-only analytics capabilities.

### MCP-friendly engineering rules

To keep the project MCP-ready:
- keep query logic out of React components,
- avoid coupling analytics logic to the dashboard layer,
- create stable service functions with clear arguments,
- return structured data objects instead of only formatted strings,
- keep validation and normalization inside the backend or service layer,
- document key analytics functions and expected outputs.

### Example future MCP tools

Possible first MCP tools for this project:
- `get_overview_kpis(date_range, category)`
- `get_trending_initiatives(days, limit, tag)`
- `get_initiative_details(initiative_id)`
- `get_initiative_timeline(initiative_id)`
- `get_phase_distribution(date_range)`
- `get_parliament_followup(initiative_id)`

### Practical rule

Build the MVP normally first.

Then, once the ETL, schema, and analytics services are stable, expose selected internal functions through an MCP server.

## Data model

### Main tables

#### `initiatives`

Stores the latest known state of each initiative.

Suggested fields:
- id
- slug
- title
- description
- target_type
- target_name
- phase
- status
- created_at
- deadline_at
- signatures_count
- url
- source
- updated_at
- ingested_at

#### `initiative_snapshots`

Stores daily historical snapshots for trend analysis.

Suggested fields:
- initiative_id
- snapshot_date
- signatures_count
- phase
- status
- source
- ingested_at

#### `initiative_events`

Stores process and lifecycle events.

Suggested fields:
- event_id
- initiative_id
- event_type
- event_title
- event_description
- event_date
- actor
- source
- ingested_at

#### `riigikogu_votings`

Stores voting-level parliamentary context.

Suggested fields:
- voting_id
- title
- session_date
- result
- related_topic
- source
- updated_at
- ingested_at

#### `riigikogu_voting_details`

Stores detailed voting information.

Suggested fields:
- voting_id
- member_name
- faction
- vote_value
- source
- ingested_at

#### `initiative_tags`

Stores analytical or AI-generated categories.

Suggested fields:
- initiative_id
- tag
- confidence
- method
- updated_at

#### `initiative_infrastructure_context`

Optional enrichment table for infrastructure-themed initiatives.

Suggested fields:
- initiative_id
- context_source
- context_type
- context_title
- context_date
- context_location
- context_value
- metadata_json

## ETL architecture

The ETL should be split into two modes.

### Daily sync

Purpose:
- refresh active initiatives,
- capture latest counts,
- collect new events,
- update dashboard-ready aggregates.

Responsibilities:
- fetch initiative list,
- fetch initiative detail if needed,
- fetch statistics,
- store new snapshot rows,
- insert new events,
- update latest state table,
- log run status.

### Weekly enrichment

Purpose:
- enrich analytical quality,
- improve categorization,
- attach institutional context,
- compute heavier derived tables.

Responsibilities:
- tag initiatives by topic,
- identify infrastructure-related initiatives,
- map possible initiative to institutional context,
- update long-term aggregate tables,
- refresh narrative insight tables.

## Validation and reliability

The pipeline must include:
- duplicate checks,
- null checks for critical fields,
- signature count sanity checks,
- phase and status normalization,
- API failure handling,
- structured logging,
- safe reruns,
- idempotent updates where possible.

The project must be resilient and easy to restart.

## Analytics plan

### Overview analytics

- total initiatives
- active initiatives
- signatures total
- phase distribution
- target distribution
- recent additions

### Momentum analytics

- top growing initiatives in last 7 days
- support velocity
- fastest-growing initiatives
- newly active initiatives
- rare viral cases

### Process analytics

- funnel by lifecycle stage
- average time between stages
- stalled initiatives
- recent process events
- timeline of civic activity

### Institutional analytics

- initiatives with institutional follow-up
- linked parliamentary context
- recent Riigikogu actions
- possible impact-oriented metrics

### Infrastructure analytics

Optional module only.

Use when initiatives are tagged as infrastructure-related.

Examples:
- initiatives about transport,
- local services,
- road issues,
- construction,
- urban environment.

## Dashboard structure

### 1. Overview

Show:
- KPI cards,
- active initiative counts,
- phase split,
- recent platform summary.

### 2. Momentum

Show:
- trending initiatives,
- 7-day growth,
- support velocity,
- sparkline-style change patterns,
- top movers.

### 3. Process

Show:
- event timeline,
- phase funnel,
- median durations,
- stalled initiatives,
- recent process updates.

### 4. Institutions

Show:
- initiatives with parliamentary context,
- related voting data,
- institutional follow-up cards,
- recent relevant actions.

### 5. Infrastructure context (optional)

Show:
- infrastructure-tagged initiatives,
- contextual Tallinn open data enrichments,
- thematic filters.

## AI copilot

The AI layer must be useful, not decorative.

In the MVP stage, the copilot may work through internal analytics functions and prebuilt services.

Later, the same analytical capabilities should be exposable through an MCP server, so external AI clients can interact with the project through structured tools, resources, and prompts.

The copilot should:
- answer natural-language questions,
- translate questions into analytical operations,
- explain chart findings,
- summarize recent changes,
- generate narrative insights,
- compare themes, phases, and growth patterns.

Examples:
- Which initiatives gained the most support in the last 7 days?
- Which initiatives are currently active in infrastructure topics?
- Which initiatives reached institutional processing?
- What phases appear to be the slowest?

## UX principles

The interface should be:
- clean,
- modern,
- portfolio-quality,
- data-dense but readable,
- strong in hierarchy,
- filterable,
- responsive,
- useful in dark and light mode.

Avoid generic AI-dashboard aesthetics.
Avoid fake demo data.
Avoid making every section look visually identical.

## Development roadmap

### Phase 1 — Foundation

- define folder structure
- design DB schema
- set up ETL skeleton
- connect Rahvaalgatus API
- store first raw and normalized data

### Phase 2 — Core analytics

- create initiative snapshots
- create event ingestion
- compute overview and momentum metrics
- build first dashboard sections

### Phase 3 — Institutional layer

- connect Riigikogu API
- ingest voting data
- enrich civic records with parliamentary context
- build institutional dashboard section

### Phase 4 — AI copilot

- add queryable analytics layer
- generate insights
- support natural-language exploration

### Phase 5 — Optional enrichment

- connect Tallinn open data for infrastructure module
- add infrastructure thematic views
- refine narrative and presentation quality

### Phase 6 — MCP layer (post-MVP)

- expose selected analytics functions as MCP tools
- expose schema and metric docs as MCP resources
- add reusable civic-analysis prompts
- keep first MCP version read-only
- add admin or write tools only after analytics layer is stable

## Suggested repo structure

```text
project-root/
├── README.md
├── PROJECT_BRIEF.md
├── etl/
│   ├── daily_sync.py
│   ├── weekly_enrichment.py
│   ├── clients/
│   ├── transforms/
│   └── validators/
├── db/
│   ├── schema.sql
│   ├── views.sql
│   └── seeds/
├── services/
│   ├── analytics.py
│   ├── initiatives.py
│   ├── institutions.py
│   ├── insights.py
│   └── context.py
├── src/
│   ├── components/
│   ├── pages/
│   ├── hooks/
│   ├── lib/
│   └── data/
├── scripts/
├── docs/
└── .github/
    └── workflows/
```

## Final principle

This project should demonstrate:
- API-first data ingestion,
- historical analytics design,
- production-style automation,
- portfolio-grade dashboarding,
- AI-assisted analytical exploration,
- future-ready MCP integration without architectural rewrites.

Every decision should support clarity, reliability, and strong presentation value.