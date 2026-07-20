-- Employee Engagement tracker: fun activities, wellness, CSR and team
-- events - reuses the generic KPI/chart/evidence/gallery engine like every
-- other tracker, plus an events calendar view.

CREATE TABLE IF NOT EXISTS employee_engagement (
  id SERIAL PRIMARY KEY,
  event_date DATE NOT NULL,
  department TEXT NOT NULL,
  event_name TEXT NOT NULL,
  category TEXT,
  participation_count INTEGER,
  feedback_score_pct NUMERIC,
  status TEXT NOT NULL DEFAULT 'Planned',
  remarks TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_engagement_date ON employee_engagement (event_date);
CREATE INDEX IF NOT EXISTS idx_engagement_dept ON employee_engagement (department);
