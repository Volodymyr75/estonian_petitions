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
CREATE TABLE IF NOT EXISTS riigikogu_petitions (
    riigikogu_uuid VARCHAR PRIMARY KEY,
    initiative_id VARCHAR,
    reference VARCHAR,
    title VARCHAR,
    sender VARCHAR,
    submitting_date DATE,
    compliance_deadline DATE,
    responsible_committee VARCHAR,
    current_status VARCHAR,
    current_status_date DATE,
    last_committee_decision VARCHAR,
    has_draft BOOLEAN DEFAULT FALSE,
    draft_uuid VARCHAR,
    draft_title VARCHAR,
    draft_status VARCHAR,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS riigikogu_petition_statuses (
    status_id VARCHAR PRIMARY KEY,
    riigikogu_uuid VARCHAR,
    status_date DATE,
    status_code VARCHAR,
    status_value VARCHAR,
    committee_decision_code VARCHAR,
    committee_decision_value VARCHAR,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS riigikogu_votings (
    voting_id VARCHAR PRIMARY KEY,
    initiative_id VARCHAR,
    draft_uuid VARCHAR,
    title VARCHAR,
    description VARCHAR,
    session_date TIMESTAMP,
    result VARCHAR,
    in_favor INTEGER,
    against INTEGER,
    neutral INTEGER,
    abstained INTEGER,
    present INTEGER,
    absent INTEGER,
    source VARCHAR DEFAULT 'riigikogu',
    updated_at TIMESTAMP,
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS riigikogu_voting_details (
    voting_id VARCHAR,
    member_name VARCHAR,
    faction VARCHAR,
    vote_value VARCHAR,
    source VARCHAR DEFAULT 'riigikogu',
    ingested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (voting_id, member_name)
);

CREATE TABLE IF NOT EXISTS initiative_tags (
    initiative_id VARCHAR,
    tag VARCHAR,
    confidence DOUBLE,
    method VARCHAR,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (initiative_id, tag)
);
