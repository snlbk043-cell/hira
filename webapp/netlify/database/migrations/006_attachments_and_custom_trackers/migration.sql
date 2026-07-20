-- File/photo evidence attachments (works for both built-in and custom trackers -
-- tracker_key + record_id is a generic composite lookup regardless of which
-- table the record actually lives in) and user-defined custom trackers.
-- Custom tracker data is stored as JSONB rather than creating real Postgres
-- tables at runtime, so no dynamic DDL is ever needed.

CREATE TABLE IF NOT EXISTS attachments (
  id SERIAL PRIMARY KEY,
  tracker_key TEXT NOT NULL,
  record_id INTEGER NOT NULL,
  filename TEXT NOT NULL,
  content_type TEXT NOT NULL,
  size_bytes INTEGER NOT NULL,
  blob_key TEXT NOT NULL UNIQUE,
  kind TEXT NOT NULL DEFAULT 'document',
  uploaded_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_attachments_tracker_record ON attachments (tracker_key, record_id);

CREATE TABLE IF NOT EXISTS custom_trackers (
  id SERIAL PRIMARY KEY,
  key TEXT NOT NULL UNIQUE,
  label TEXT NOT NULL,
  icon TEXT NOT NULL DEFAULT '📁',
  description TEXT NOT NULL DEFAULT '',
  fields JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS custom_tracker_records (
  id SERIAL PRIMARY KEY,
  tracker_key TEXT NOT NULL REFERENCES custom_trackers(key) ON DELETE CASCADE,
  data JSONB NOT NULL,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_custom_records_tracker ON custom_tracker_records (tracker_key);
