import { ColumnSpec } from "./tableApi";

export const incidentColumns: ColumnSpec[] = [
  { name: "incident_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "area", type: "text" },
  { name: "classification", type: "text", required: true },
  { name: "body_part", type: "text" },
  { name: "risk_rating", type: "text" },
  { name: "lost_days", type: "number" },
  { name: "root_cause", type: "text" },
  { name: "description", type: "text" },
  { name: "status", type: "text" },
  { name: "closure_date", type: "date" },
  { name: "sif_potential", type: "boolean" },
];

export const trainingColumns: ColumnSpec[] = [
  { name: "training_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "course_name", type: "text" },
  { name: "training_type", type: "text" },
  { name: "status", type: "text" },
  { name: "attendance_pct", type: "number" },
  { name: "assessment_result", type: "text" },
];

export const observationColumns: ColumnSpec[] = [
  { name: "obs_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "observation_type", type: "text" },
  { name: "risk_level", type: "text" },
  { name: "status", type: "text" },
  { name: "due_date", type: "date" },
  { name: "description", type: "text" },
];

export const inspectionColumns: ColumnSpec[] = [
  { name: "inspection_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "inspection_type", type: "text", required: true },
  { name: "status", type: "text" },
  { name: "critical_findings", type: "number" },
  { name: "non_conformances", type: "number" },
  { name: "due_date", type: "date" },
];

export const walkthroughColumns: ColumnSpec[] = [
  { name: "walk_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "area", type: "text" },
  { name: "owner", type: "text" },
  { name: "status", type: "text" },
  { name: "completion_pct", type: "number" },
  { name: "critical_findings", type: "number" },
  { name: "due_date", type: "date" },
];

export const correctiveActionColumns: ColumnSpec[] = [
  { name: "date_raised", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "source", type: "text" },
  { name: "priority", type: "text" },
  { name: "description", type: "text" },
  { name: "status", type: "text" },
  { name: "due_date", type: "date" },
  { name: "completion_date", type: "date" },
  { name: "assigned_to", type: "text" },
];

export const ptwAuditColumns: ColumnSpec[] = [
  { name: "audit_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "permit_type", type: "text" },
  { name: "auditor", type: "text" },
  { name: "permits_reviewed", type: "number" },
  { name: "deviations_found", type: "number" },
  { name: "compliance_pct", type: "number" },
  { name: "verdict", type: "text" },
];

export const riskAssessmentColumns: ColumnSpec[] = [
  { name: "assessment_date", type: "date", required: true },
  { name: "department", type: "text", required: true },
  { name: "task", type: "text" },
  { name: "risk_level", type: "text" },
  { name: "hazards_identified", type: "number" },
  { name: "approval_status", type: "text" },
  { name: "controls_implemented", type: "text" },
];
