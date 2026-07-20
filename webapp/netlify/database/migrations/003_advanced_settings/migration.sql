-- Settings needed for the advanced-analysis round: cost-impact rates and
-- prior-year actuals for a genuine YoY comparison (left at 0 until the user
-- types real figures in, never fabricated), plus Likelihood/Consequence on
-- JSA Risk Assessment for a true 5x5 risk matrix.

INSERT INTO settings (key, value, note) VALUES
  ('cost_per_lost_day', '8000', 'Incident lost days -> estimated cost (Rs)'),
  ('cost_per_downtime_min', '150', 'Stop Work Authority downtime -> estimated cost (Rs per minute)'),
  ('py_trir', '0', 'Prior year TRIR - for YoY comparison'),
  ('py_ltifr', '0', 'Prior year LTIFR - for YoY comparison'),
  ('py_total_incidents', '0', 'Prior year total incidents - for YoY comparison'),
  ('py_training_pct', '0', 'Prior year training compliance % - for YoY comparison'),
  ('py_obs_pct', '0', 'Prior year observation closure % - for YoY comparison'),
  ('py_ca_pct', '0', 'Prior year CA closure % - for YoY comparison')
ON CONFLICT (key) DO NOTHING;

ALTER TABLE risk_assessments ADD COLUMN IF NOT EXISTS likelihood INTEGER;
ALTER TABLE risk_assessments ADD COLUMN IF NOT EXISTS consequence INTEGER;
