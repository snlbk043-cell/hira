-- Statutory Compliance Register: legal/regulatory requirements tracker
-- (licenses, renewals, statutory inspections), with its own compliance
-- calendar (compliance_schedule, tracker_key = 'statutory-compliance').

CREATE TABLE IF NOT EXISTS statutory_compliance (
  id SERIAL PRIMARY KEY,
  review_date DATE NOT NULL,
  department TEXT NOT NULL,
  requirement TEXT NOT NULL,
  applicable_law TEXT,
  frequency TEXT NOT NULL DEFAULT 'Annually',
  last_complied_date DATE,
  next_due_date DATE,
  status TEXT NOT NULL DEFAULT 'Pending',
  responsible_person TEXT,
  remarks TEXT,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);
CREATE INDEX IF NOT EXISTS idx_statutory_date ON statutory_compliance (review_date);
CREATE INDEX IF NOT EXISTS idx_statutory_dept ON statutory_compliance (department);
