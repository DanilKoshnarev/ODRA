-- ODRA ClickHouse Schema

CREATE DATABASE IF NOT EXISTS odra;

-- Documents with embeddings table
CREATE TABLE IF NOT EXISTS odra.documents (
    id String,
    title String,
    content String,
    embedding Array(Float32),
    source String,
    department String DEFAULT '',
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    shard_id String,
    metadata JSON
) ENGINE = MergeTree()
ORDER BY (created_at, id)
PARTITION BY toYYYYMM(created_at);

-- Index for vector search (HNSW if available, otherwise just B-tree)
ALTER TABLE odra.documents ADD INDEX embedding_idx embedding TYPE ngram(3);

-- Audit jobs table
CREATE TABLE IF NOT EXISTS odra.audit_jobs (
    id String,
    goal String,
    scope String DEFAULT '',
    status String,
    progress Float32 DEFAULT 0.0,
    precision Float32 DEFAULT 0.0,
    recall Float32 DEFAULT 0.0,
    created_at DateTime DEFAULT now(),
    updated_at DateTime DEFAULT now(),
    results JSON
) ENGINE = MergeTree()
ORDER BY (created_at, id)
PARTITION BY toYYYYMM(created_at);

-- Audit evidence links
CREATE TABLE IF NOT EXISTS odra.audit_evidence (
    id String,
    job_id String,
    doc_id String,
    score Float32,
    evidence_text String,
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (job_id, score DESC, created_at)
PARTITION BY toYYYYMM(created_at);

-- Human feedback table
CREATE TABLE IF NOT EXISTS odra.feedback (
    id String,
    job_id String,
    doc_id String,
    feedback_type String,
    comment String DEFAULT '',
    created_at DateTime DEFAULT now()
) ENGINE = MergeTree()
ORDER BY (job_id, created_at)
PARTITION BY toYYYYMM(created_at);

-- Metrics/observability table
CREATE TABLE IF NOT EXISTS odra.metrics (
    timestamp DateTime,
    metric_name String,
    metric_value Float32,
    tags JSON
) ENGINE = MergeTree()
ORDER BY (timestamp, metric_name)
PARTITION BY toYYYYMM(timestamp);
