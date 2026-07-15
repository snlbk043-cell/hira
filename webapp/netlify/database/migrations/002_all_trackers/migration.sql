-- RCPL Safety Dashboard - the remaining 17 trackers, completing the full 25-tracker
-- set that mirrors the Excel Integrated EHS Management System's registers.
-- Same conventions as 001_init: free-text status/category columns (no enums), so the
-- app can extend value lists without a migration.

CREATE TABLE toolbox_talks (
  id SERIAL PRIMARY KEY,
  talk_date DATE NOT NULL,
  department TEXT NOT NULL,
  location TEXT,
  topic TEXT,
  target_attendees INTEGER DEFAULT 0,
  actual_attendees INTEGER DEFAULT 0,
  attendance_pct NUMERIC,
  duration_min INTEGER,
  safety_category TEXT,
  action_required TEXT,   -- Yes, No
  effectiveness TEXT,     -- Excellent, Good, Satisfactory, Needs Improvement, Unsatisfactory
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE equipment_inspections (
  id SERIAL PRIMARY KEY,
  inspection_date DATE NOT NULL,
  department TEXT NOT NULL,
  location TEXT,
  checkpoints_inspected INTEGER DEFAULT 0,
  non_conformances INTEGER DEFAULT 0,
  critical_findings INTEGER DEFAULT 0,
  overall_rating TEXT,
  status TEXT NOT NULL DEFAULT 'Pending',
  due_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE safety_meetings (
  id SERIAL PRIMARY KEY,
  meeting_date DATE NOT NULL,
  department TEXT NOT NULL,
  attendance_pct NUMERIC,
  action_items_raised INTEGER DEFAULT 0,
  actions_closed INTEGER DEFAULT 0,
  closeout_pct NUMERIC,
  duration_min INTEGER,
  mom_circulated TEXT,  -- Yes, No
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE safety_bulletins (
  id SERIAL PRIMARY KEY,
  issue_date DATE NOT NULL,
  department TEXT,
  bulletin_type TEXT,
  distribution_method TEXT,
  target_reach INTEGER DEFAULT 0,
  actual_reach INTEGER DEFAULT 0,
  reach_pct NUMERIC,
  status TEXT NOT NULL DEFAULT 'Issued', -- Issued, Acknowledged, Closed
  priority TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE emergency_drills (
  id SERIAL PRIMARY KEY,
  drill_date DATE NOT NULL,
  department TEXT,
  location TEXT,
  drill_type TEXT,
  target_participants INTEGER DEFAULT 0,
  actual_participants INTEGER DEFAULT 0,
  participation_pct NUMERIC,
  target_response_min NUMERIC,
  actual_response_min NUMERIC,
  status TEXT NOT NULL DEFAULT 'Action Pending', -- Completed, Action Pending, Rescheduled
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE internal_audits (
  id SERIAL PRIMARY KEY,
  audit_date DATE NOT NULL,
  department TEXT NOT NULL,
  audit_type TEXT,
  status TEXT NOT NULL DEFAULT 'Scheduled', -- Completed, In Progress, Scheduled
  checklist_items INTEGER DEFAULT 0,
  minor_nc INTEGER DEFAULT 0,
  major_nc INTEGER DEFAULT 0,
  observations INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE external_audits (
  id SERIAL PRIMARY KEY,
  audit_date DATE NOT NULL,
  department TEXT NOT NULL,
  audit_type TEXT,
  status TEXT NOT NULL DEFAULT 'Scheduled',
  checklist_items INTEGER DEFAULT 0,
  minor_nc INTEGER DEFAULT 0,
  major_nc INTEGER DEFAULT 0,
  observations INTEGER DEFAULT 0,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE management_visits (
  id SERIAL PRIMARY KEY,
  visit_date DATE NOT NULL,
  department TEXT NOT NULL,
  visit_type TEXT,
  observations_made INTEGER DEFAULT 0,
  actions_raised INTEGER DEFAULT 0,
  actions_closed INTEGER DEFAULT 0,
  closeout_pct NUMERIC,
  status TEXT NOT NULL DEFAULT 'Action Pending', -- Completed, Action Pending
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE management_reviews (
  id SERIAL PRIMARY KEY,
  review_date DATE NOT NULL,
  department TEXT,
  members_invited INTEGER DEFAULT 0,
  members_attended INTEGER DEFAULT 0,
  attendance_pct NUMERIC,
  decisions_made INTEGER DEFAULT 0,
  actions_assigned INTEGER DEFAULT 0,
  closeout_pct NUMERIC,
  status TEXT NOT NULL DEFAULT 'Scheduled', -- Completed, In Progress, Scheduled
  mom_distributed TEXT, -- Yes, No
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE disciplinary_actions (
  id SERIAL PRIMARY KEY,
  case_date DATE NOT NULL,
  department TEXT NOT NULL,
  violation_type TEXT,
  offense_level TEXT,   -- 1st Offense, 2nd Offense, 3rd Offense, Repeat
  action_taken TEXT,    -- Verbal Warning, Written Warning, Suspension, Retraining, Termination
  status TEXT NOT NULL DEFAULT 'Under Review', -- Completed, Under Review, Appealed
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE safety_awards (
  id SERIAL PRIMARY KEY,
  award_date DATE NOT NULL,
  department TEXT NOT NULL,
  award_category TEXT,
  reward_type TEXT,
  recipient TEXT,
  status TEXT NOT NULL DEFAULT 'Nominated', -- Presented, Scheduled, Nominated
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE stop_work_authority (
  id SERIAL PRIMARY KEY,
  event_date DATE NOT NULL,
  department TEXT NOT NULL,
  location TEXT,
  severity TEXT,          -- Critical, High, Medium
  downtime_min INTEGER DEFAULT 0,
  resolution TEXT NOT NULL DEFAULT 'Under Investigation', -- Resolved, Permanent Fix Applied, Under Investigation
  investigation_done TEXT, -- Yes, No
  description TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE alcohol_tests (
  id SERIAL PRIMARY KEY,
  test_date DATE NOT NULL,
  department TEXT NOT NULL,
  test_type TEXT,      -- Pre-Shift, Random, Post-Incident, Reasonable Suspicion
  result TEXT NOT NULL, -- Negative, Positive
  person_type TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE nc_management (
  id SERIAL PRIMARY KEY,
  date_raised DATE NOT NULL,
  department TEXT NOT NULL,
  severity TEXT,  -- Major, Minor, Observation
  root_cause_capa TEXT,
  status TEXT NOT NULL DEFAULT 'Open', -- Closed, Open, Under Review, Overdue
  due_date DATE,
  actual_close_date DATE,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE unsafe_acts (
  id SERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  department TEXT NOT NULL,
  location TEXT,
  description TEXT,
  risk_level TEXT,
  immediate_action TEXT,
  corrective_action TEXT,
  due_date DATE,
  status TEXT NOT NULL DEFAULT 'Pending', -- Completed, Pending, In Progress, Overdue
  reported_by TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE unsafe_conditions (
  id SERIAL PRIMARY KEY,
  report_date DATE NOT NULL,
  department TEXT NOT NULL,
  location TEXT,
  description TEXT,
  risk_level TEXT,
  immediate_action TEXT,
  corrective_action TEXT,
  due_date DATE,
  status TEXT NOT NULL DEFAULT 'Pending',
  reported_by TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE environmental_performance (
  id SERIAL PRIMARY KEY,
  record_date DATE NOT NULL,
  department TEXT NOT NULL,
  location TEXT,
  waste_type TEXT,
  waste_generated_kg NUMERIC DEFAULT 0,
  waste_recycled_kg NUMERIC DEFAULT 0,
  recycle_rate_pct NUMERIC,
  energy_kwh NUMERIC DEFAULT 0,
  water_m3 NUMERIC DEFAULT 0,
  fuel_l NUMERIC DEFAULT 0,
  remarks TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_toolbox_date ON toolbox_talks (talk_date);
CREATE INDEX idx_eqinsp_date ON equipment_inspections (inspection_date);
CREATE INDEX idx_meetings_date ON safety_meetings (meeting_date);
CREATE INDEX idx_bulletins_date ON safety_bulletins (issue_date);
CREATE INDEX idx_drills_date ON emergency_drills (drill_date);
CREATE INDEX idx_iaudit_date ON internal_audits (audit_date);
CREATE INDEX idx_eaudit_date ON external_audits (audit_date);
CREATE INDEX idx_mgmtvisit_date ON management_visits (visit_date);
CREATE INDEX idx_mgmtreview_date ON management_reviews (review_date);
CREATE INDEX idx_disc_date ON disciplinary_actions (case_date);
CREATE INDEX idx_awards_date ON safety_awards (award_date);
CREATE INDEX idx_swa_date ON stop_work_authority (event_date);
CREATE INDEX idx_alcohol_date ON alcohol_tests (test_date);
CREATE INDEX idx_nc_date ON nc_management (date_raised);
CREATE INDEX idx_unsafeact_date ON unsafe_acts (report_date);
CREATE INDEX idx_unsafecond_date ON unsafe_conditions (report_date);
CREATE INDEX idx_env_date ON environmental_performance (record_date);
