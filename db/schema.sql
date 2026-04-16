-- Phase 1 Foundation Schema

CREATE TABLE IF NOT EXISTS initiatives (
    id VARCHAR PRIMARY KEY,
    slug VARCHAR,
    title VARCHAR,
    description TEXT,
    target_type VARCHAR,
    target_name VARCHAR,
    phase VARCHAR,
    status VARCHAR,
    created_at TIMESTAMP,
    deadline_at TIMESTAMP,
    signatures_count INTEGER DEFAULT 0,
    url VARCHAR,
    source VARCHAR DEFAULT 'rahvaalgatus',
    updated_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS initiative_snapshots (
    initiative_id VARCHAR,
    snapshot_date DATE,
    signatures_count INTEGER DEFAULT 0,
    phase VARCHAR,
    status VARCHAR,
    source VARCHAR DEFAULT 'rahvaalgatus',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (initiative_id, snapshot_date)
);

CREATE TABLE IF NOT EXISTS initiative_events (
    event_id VARCHAR PRIMARY KEY,
    initiative_id VARCHAR,
    event_type VARCHAR,
    event_title VARCHAR,
    event_description TEXT,
    event_date TIMESTAMP,
    actor VARCHAR,
    source VARCHAR DEFAULT 'rahvaalgatus',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Core tables for Phase 3 (Institutional), added now for completeness
CREATE TABLE IF NOT EXISTS riigikogu_votings (
    voting_id VARCHAR PRIMARY KEY,
    title VARCHAR,
    session_date TIMESTAMP,
    result VARCHAR,
    related_topic VARCHAR,
    source VARCHAR DEFAULT 'riigikogu',
    updated_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS initiative_tags (
    initiative_id VARCHAR,
    tag VARCHAR,
    confidence DOUBLE,
    method VARCHAR,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (initiative_id, tag)
);
