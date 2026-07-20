-- Generic compliance-calendar scheduling, shared across any tracker that
-- needs "what/where is due when, is it done" planning (Workplace/Equipment
-- Inspections, Safety Walkthroughs, Internal/External Audits, and the new
-- Statutory Compliance Register). Deliberately separate from each tracker's
-- own record table - this is a forward-looking plan, not a completed record.

CREATE TABLE IF NOT EXISTS compliance_schedule (
  id SERIAL PRIMARY KEY,
  tracker_key TEXT NOT NULL,
  title TEXT NOT NULL,
  location TEXT,
  frequency TEXT NOT NULL DEFAULT 'One-time',
  due_date DATE NOT NULL,
  status TEXT NOT NULL DEFAULT 'Pending',
  completed_date DATE,
  notes TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_compliance_schedule_tracker ON compliance_schedule (tracker_key, due_date);
