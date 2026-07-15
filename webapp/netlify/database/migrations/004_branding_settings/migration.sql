-- Extra customization settings: plant/company branding shown in the sidebar,
-- plus JSA Approved % and Walkthrough Completion % targets (previously
-- hardcoded on the Executive spider chart / gauges).

INSERT INTO settings (key, value, note) VALUES
  ('site_name', 'RCPL SAFETY', 'Shown as the sidebar title'),
  ('company_name', 'Campa Cola CSD Plant · EHS System', 'Shown under the sidebar title'),
  ('jsa_approval_target_pct', '90', 'Target for JSA Approved % (radar/gauge)'),
  ('walkthrough_target_pct', '85', 'Target for Walkthroughs Done % (radar chart)')
ON CONFLICT (key) DO NOTHING;
