-- HIRA/JSA Controls Compliance: planned vs actually implemented control
-- measures per risk assessment, following the same target/actual/%-auto-calc
-- pattern already used by Toolbox Talks, Safety Bulletins, Emergency Drills
-- and Management Reviews.

ALTER TABLE risk_assessments ADD COLUMN IF NOT EXISTS controls_planned INTEGER;
ALTER TABLE risk_assessments ADD COLUMN IF NOT EXISTS controls_completed INTEGER;
ALTER TABLE risk_assessments ADD COLUMN IF NOT EXISTS controls_compliance_pct NUMERIC;
