-- RCPL Safety Dashboard - core schema
-- Departments/status are free-text (not enums) so the app can add new values
-- without a migration, matching how the Excel system's dropdowns work.

CREATE TABLE incidents (
  id SERIAL PRIMARY KEY,
  incident_date DATE NOT NULL,
  department TEXT NOT NULL,
  area TEXT,
  classification TEXT NOT NULL,        -- Near Miss, First Aid, Medical Treatment, Restricted Work, Lost Time Injury, Fatality
  body_part TEXT,                      -- Head, Eye, Hand/Finger, Arm, Foot/Leg, Back, Torso, Multiple
  risk_rating TEXT,                    -- Critical, High, Medium, Low
  lost_days INTEGER DEFAULT 0,
  root_cause TEXT,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'Open', -- Open, In Progress, Closed
  closure_date DATE,
  sif_potential BOOLEAN DEFAULT FALSE, -- Serious Injury/Fatality potential flag
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE training (
  id SERIAL PRIMARY KEY,
  training_date DATE NOT NULL,
  department TEXT NOT NULL,
  course_name TEXT,
  training_type TEXT,
  status TEXT NOT NULL DEFAULT 'Scheduled', -- Completed, In Progress, Scheduled
  attendance_pct NUMERIC,
  assessment_result TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE hse_observations (
  id SERIAL PRIMARY KEY,
  obs_date DATE NOT NULL,
  department TEXT NOT NULL,
  observation_type TEXT,       -- Safe Act, Unsafe Act, Safe Condition, Unsafe Condition, Near Miss
  risk_level TEXT,
  status TEXT NOT NULL DEFAULT 'Pending', -- Completed, In Progress, Pending, Overdue
  due_date DATE,
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE inspections (
  id SERIAL PRIMARY KEY,
  inspection_date DATE NOT NULL,
  department TEXT NOT NULL,
  inspection_type TEXT NOT NULL, -- Workplace, Equipment
  status TEXT NOT NULL DEFAULT 'Pending',
  critical_findings INTEGER DEFAULT 0,
  non_conformances INTEGER DEFAULT 0,
  due_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE safety_walkthroughs (
  id SERIAL PRIMARY KEY,
  walk_date DATE NOT NULL,
  department TEXT NOT NULL,
  area TEXT,
  owner TEXT,
  status TEXT NOT NULL DEFAULT 'Pending', -- Completed, In Progress, Overdue, Pending
  completion_pct NUMERIC DEFAULT 0,
  critical_findings INTEGER DEFAULT 0,
  due_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE corrective_actions (
  id SERIAL PRIMARY KEY,
  date_raised DATE NOT NULL,
  department TEXT NOT NULL,
  source TEXT,
  priority TEXT,
  description TEXT,
  status TEXT NOT NULL DEFAULT 'Pending', -- Completed, In Progress, Overdue, Pending, Cancelled
  due_date DATE,
  completion_date DATE,
  assigned_to TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE ptw_audits (
  id SERIAL PRIMARY KEY,
  audit_date DATE NOT NULL,
  department TEXT NOT NULL,
  permit_type TEXT,
  auditor TEXT,
  permits_reviewed INTEGER DEFAULT 0,
  deviations_found INTEGER DEFAULT 0,
  compliance_pct NUMERIC,
  verdict TEXT, -- Compliant, Non-Compliant, Partially Compliant
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE risk_assessments (
  id SERIAL PRIMARY KEY,
  assessment_date DATE NOT NULL,
  department TEXT NOT NULL,
  task TEXT,
  risk_level TEXT, -- Critical, High, Medium, Low
  hazards_identified INTEGER DEFAULT 0,
  approval_status TEXT NOT NULL DEFAULT 'Pending Review', -- Approved, Pending Review, Revision Required, Rejected
  controls_implemented TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE manhours (
  id SERIAL PRIMARY KEY,
  year INTEGER NOT NULL,
  month INTEGER NOT NULL,          -- 1-12
  department TEXT NOT NULL DEFAULT 'All', -- 'All' = plant-wide total
  hours NUMERIC NOT NULL,
  UNIQUE (year, month, department)
);

CREATE TABLE settings (
  key TEXT PRIMARY KEY,
  value TEXT NOT NULL,
  note TEXT
);

INSERT INTO settings (key, value, note) VALUES
  ('trir_target', '1.0', 'Green if actual <= target'),
  ('ltifr_target', '2.0', 'Green if actual <= target'),
  ('training_target_pct', '95', ''),
  ('obs_closure_target_pct', '90', ''),
  ('ca_closure_target_pct', '90', ''),
  ('ptw_compliance_target_pct', '95', ''),
  ('amber_band', '0.8', 'Below this fraction of target = Red'),
  ('trir_multiplier', '200000', 'OSHA standard'),
  ('ltifr_multiplier', '1000000', 'Per million man-hours'),
  ('industry_benchmark_trir', '1.5', ''),
  ('industry_benchmark_ltifr', '2.5', '');

CREATE INDEX idx_incidents_date ON incidents (incident_date);
CREATE INDEX idx_incidents_dept ON incidents (department);
CREATE INDEX idx_training_date ON training (training_date);
CREATE INDEX idx_obs_date ON hse_observations (obs_date);
CREATE INDEX idx_insp_date ON inspections (inspection_date);
CREATE INDEX idx_walk_date ON safety_walkthroughs (walk_date);
CREATE INDEX idx_ca_date ON corrective_actions (date_raised);
CREATE INDEX idx_ptw_date ON ptw_audits (audit_date);
CREATE INDEX idx_risk_date ON risk_assessments (assessment_date);
