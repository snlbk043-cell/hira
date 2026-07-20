import { RISK_LEVELS } from "./constants";
import { ColumnSpec } from "./tableApi";

export type FieldType = "date" | "text" | "number" | "boolean" | "select" | "department";
export type FieldRole = "date" | "department" | "status" | "category" | "risk" | "metric_pct" | "metric_num" | "target_num" | "actual_num";

export type TrackerField = {
  name: string;
  label: string;
  type: FieldType;
  options?: string[];
  required?: boolean;
  role?: FieldRole;
  /** Overrides the DB column type when it differs from the UI widget type
   * (e.g. a numeric field rendered as a 1-5 dropdown). */
  dataType?: "text" | "number" | "date" | "boolean";
};

export type TrackerDef = {
  key: string;          // URL slug + API slug
  table: string;         // Postgres table name
  label: string;
  icon: string;
  description: string;
  fields: TrackerField[];
};

const STATUS4 = ["Completed", "In Progress", "Pending", "Overdue"];
const YESNO = ["Yes", "No"];

export const TRACKERS: TrackerDef[] = [
  {
    key: "toolbox-talks", table: "toolbox_talks", label: "Toolbox Talks", icon: "🗣️",
    description: "Daily/weekly safety talks — topic, attendance and effectiveness.",
    fields: [
      { name: "talk_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "topic", label: "Topic", type: "select", options: ["PPE Usage","Fire Safety","Working at Heights","Manual Handling","Electrical Safety","Chemical Safety","Housekeeping","Heat Stress","Slip Trip Fall","Confined Space","LOTO","Emergency Procedures","Hot Work","Machine Guarding"], role: "category" },
      { name: "target_attendees", label: "Target Attendees", type: "number", role: "target_num" },
      { name: "actual_attendees", label: "Actual Attendees", type: "number", role: "actual_num" },
      { name: "attendance_pct", label: "Attendance %", type: "number", role: "metric_pct" },
      { name: "duration_min", label: "Duration (min)", type: "number" },
      { name: "safety_category", label: "Safety Category", type: "text" },
      { name: "action_required", label: "Action Required", type: "select", options: YESNO },
      { name: "effectiveness", label: "Effectiveness", type: "select", options: ["Excellent","Good","Satisfactory","Needs Improvement","Unsatisfactory"] },
    ],
  },
  {
    key: "jsa", table: "risk_assessments", label: "JSA Risk Assessment", icon: "⚠️",
    description: "Job Safety Analysis — hazards identified, risk level, approval status.",
    fields: [
      { name: "assessment_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "task", label: "Task/Activity", type: "text" },
      { name: "risk_level", label: "Risk Level", type: "select", options: RISK_LEVELS, role: "risk" },
      { name: "hazards_identified", label: "Hazards Identified", type: "number" },
      { name: "approval_status", label: "Approval Status", type: "select", options: ["Approved","Pending Review","Revision Required","Rejected"], role: "status" },
      { name: "controls_implemented", label: "Controls Implemented (Description)", type: "text" },
      { name: "likelihood", label: "Likelihood (1-5)", type: "select", options: ["1","2","3","4","5"], dataType: "number" },
      { name: "consequence", label: "Consequence (1-5)", type: "select", options: ["1","2","3","4","5"], dataType: "number" },
      { name: "controls_planned", label: "Controls Planned (Count)", type: "number", role: "target_num" },
      { name: "controls_completed", label: "Controls Completed (Count)", type: "number", role: "actual_num" },
      { name: "controls_compliance_pct", label: "Controls Compliance %", type: "number", role: "metric_pct" },
    ],
  },
  {
    key: "training", table: "training", label: "Training", icon: "🎓",
    description: "Induction, refresher and competency training records.",
    fields: [
      { name: "training_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "course_name", label: "Course Name", type: "text" },
      { name: "training_type", label: "Training Type", type: "select", options: ["Induction","Refresher","Advanced","On-the-Job","Awareness","Competency"], role: "category" },
      { name: "status", label: "Status", type: "select", options: ["Completed","In Progress","Scheduled"], role: "status" },
      { name: "attendance_pct", label: "Attendance %", type: "number", role: "metric_pct" },
      { name: "assessment_result", label: "Assessment Result", type: "select", options: ["Pass","Fail","N/A"] },
    ],
  },
  {
    key: "hse-observations", table: "hse_observations", label: "HSE Observations", icon: "👁️",
    description: "Behaviour-based safety observations — safe/unsafe acts & conditions.",
    fields: [
      { name: "obs_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "observation_type", label: "Observation Type", type: "select", options: ["Safe Act","Unsafe Act","Safe Condition","Unsafe Condition","Near Miss"], role: "category" },
      { name: "risk_level", label: "Risk Level", type: "select", options: RISK_LEVELS, role: "risk" },
      { name: "status", label: "Status", type: "select", options: STATUS4, role: "status" },
      { name: "due_date", label: "Due Date", type: "date" },
      { name: "description", label: "Description", type: "text" },
    ],
  },
  {
    key: "workplace-inspections", table: "inspections", label: "Workplace Inspections", icon: "🔍",
    description: "Area/checkpoint inspections — non-conformances and critical findings.",
    fields: [
      { name: "inspection_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "inspection_type", label: "Inspection Type", type: "text", required: true, role: "category" },
      { name: "status", label: "Status", type: "select", options: STATUS4, role: "status" },
      { name: "critical_findings", label: "Critical Findings", type: "number" },
      { name: "non_conformances", label: "Non-Conformances", type: "number" },
      { name: "due_date", label: "Due Date", type: "date" },
    ],
  },
  {
    key: "equipment-inspections", table: "equipment_inspections", label: "Equipment Inspections", icon: "🛠️",
    description: "Equipment checkpoint inspections — findings and overall rating.",
    fields: [
      { name: "inspection_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "checkpoints_inspected", label: "Checkpoints Inspected", type: "number" },
      { name: "non_conformances", label: "Non-Conformances", type: "number" },
      { name: "critical_findings", label: "Critical Findings", type: "number" },
      { name: "overall_rating", label: "Overall Rating", type: "select", options: ["Excellent","Good","Satisfactory","Needs Improvement","Unsatisfactory"], role: "category" },
      { name: "status", label: "Status", type: "select", options: STATUS4, role: "status" },
      { name: "due_date", label: "Due Date", type: "date" },
    ],
  },
  {
    key: "safety-walkthroughs", table: "safety_walkthroughs", label: "Safety Walkthroughs", icon: "🚶",
    description: "Leadership/safety-team floor walks — completion and findings.",
    fields: [
      { name: "walk_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "area", label: "Area", type: "text" },
      { name: "owner", label: "Owner", type: "text" },
      { name: "status", label: "Status", type: "select", options: STATUS4, role: "status" },
      { name: "completion_pct", label: "Completion %", type: "number", role: "metric_pct" },
      { name: "critical_findings", label: "Critical Findings", type: "number" },
      { name: "due_date", label: "Due Date", type: "date" },
    ],
  },
  {
    key: "safety-meetings", table: "safety_meetings", label: "Safety Meetings", icon: "🗓️",
    description: "Safety committee meetings — action items raised vs closed.",
    fields: [
      { name: "meeting_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "attendance_pct", label: "Attendance %", type: "number", role: "metric_pct" },
      { name: "action_items_raised", label: "Action Items Raised", type: "number" },
      { name: "actions_closed", label: "Actions Closed", type: "number" },
      { name: "closeout_pct", label: "Close-out %", type: "number" },
      { name: "duration_min", label: "Duration (min)", type: "number" },
      { name: "mom_circulated", label: "MoM Circulated", type: "select", options: YESNO },
    ],
  },
  {
    key: "safety-bulletins", table: "safety_bulletins", label: "Safety Bulletins", icon: "📰",
    description: "Safety alerts/lessons-learned — reach by distribution method.",
    fields: [
      { name: "issue_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", role: "department" },
      { name: "bulletin_type", label: "Type", type: "select", options: ["Safety Alert","Bulletin","Toolbox Topic","Lesson Learned","Best Practice","Advisory"], role: "category" },
      { name: "distribution_method", label: "Distribution Method", type: "select", options: ["Email","Notice Board","App Notification","All Channels"] },
      { name: "target_reach", label: "Target Reach", type: "number", role: "target_num" },
      { name: "actual_reach", label: "Actual Reach", type: "number", role: "actual_num" },
      { name: "reach_pct", label: "Reach %", type: "number", role: "metric_pct" },
      { name: "status", label: "Status", type: "select", options: ["Issued","Acknowledged","Closed"], role: "status" },
      { name: "priority", label: "Priority", type: "select", options: ["Critical","High","Medium","Low"] },
    ],
  },
  {
    key: "emergency-drills", table: "emergency_drills", label: "Emergency Drills", icon: "🚨",
    description: "Fire/spill/medical drills — participation and response time.",
    fields: [
      { name: "drill_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "drill_type", label: "Drill Type", type: "select", options: ["Fire Evacuation","Chemical Spill","Medical Emergency","Gas Leak","Confined Space Rescue","Earthquake"], role: "category" },
      { name: "target_participants", label: "Target Participants", type: "number", role: "target_num" },
      { name: "actual_participants", label: "Actual Participants", type: "number", role: "actual_num" },
      { name: "participation_pct", label: "Participation %", type: "number", role: "metric_pct" },
      { name: "target_response_min", label: "Target Response (min)", type: "number" },
      { name: "actual_response_min", label: "Actual Response (min)", type: "number" },
      { name: "status", label: "Status", type: "select", options: ["Completed","Action Pending","Rescheduled"], role: "status" },
    ],
  },
  {
    key: "internal-audits", table: "internal_audits", label: "Internal Audits", icon: "📋",
    description: "Internal system/compliance audits — NC counts by severity.",
    fields: [
      { name: "audit_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "audit_type", label: "Audit Type", type: "select", options: ["System Audit","Compliance Audit","Process Audit","Surveillance","Customer Audit","Regulatory Inspection"], role: "category" },
      { name: "status", label: "Status", type: "select", options: ["Completed","In Progress","Scheduled"], role: "status" },
      { name: "checklist_items", label: "Checklist Items", type: "number" },
      { name: "minor_nc", label: "Minor NC", type: "number" },
      { name: "major_nc", label: "Major NC", type: "number" },
      { name: "observations", label: "Observations", type: "number" },
    ],
  },
  {
    key: "external-audits", table: "external_audits", label: "External Audits", icon: "🏛️",
    description: "Third-party/regulatory audits — NC counts by severity.",
    fields: [
      { name: "audit_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "audit_type", label: "Audit Type", type: "select", options: ["System Audit","Compliance Audit","Process Audit","Surveillance","Customer Audit","Regulatory Inspection"], role: "category" },
      { name: "status", label: "Status", type: "select", options: ["Completed","In Progress","Scheduled"], role: "status" },
      { name: "checklist_items", label: "Checklist Items", type: "number" },
      { name: "minor_nc", label: "Minor NC", type: "number" },
      { name: "major_nc", label: "Major NC", type: "number" },
      { name: "observations", label: "Observations", type: "number" },
    ],
  },
  {
    key: "management-visits", table: "management_visits", label: "Management Visits", icon: "🧑‍💼",
    description: "Leadership site visits — observations and action close-out.",
    fields: [
      { name: "visit_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "visit_type", label: "Visit Type", type: "select", options: ["Site Walk","Plant Visit","Safety Observation","Project Visit"], role: "category" },
      { name: "observations_made", label: "Observations Made", type: "number" },
      { name: "actions_raised", label: "Actions Raised", type: "number" },
      { name: "actions_closed", label: "Actions Closed", type: "number" },
      { name: "closeout_pct", label: "Close-out %", type: "number" },
      { name: "status", label: "Status", type: "select", options: ["Completed","Action Pending"], role: "status" },
    ],
  },
  {
    key: "management-reviews", table: "management_reviews", label: "Management Reviews", icon: "🧭",
    description: "Formal EHS management reviews — decisions and actions assigned.",
    fields: [
      { name: "review_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", role: "department" },
      { name: "members_invited", label: "Members Invited", type: "number", role: "target_num" },
      { name: "members_attended", label: "Members Attended", type: "number", role: "actual_num" },
      { name: "attendance_pct", label: "Attendance %", type: "number", role: "metric_pct" },
      { name: "decisions_made", label: "Decisions Made", type: "number" },
      { name: "actions_assigned", label: "Actions Assigned", type: "number" },
      { name: "closeout_pct", label: "Close-out %", type: "number" },
      { name: "status", label: "Status", type: "select", options: ["Completed","In Progress","Scheduled"], role: "status" },
      { name: "mom_distributed", label: "MoM Distributed", type: "select", options: YESNO },
    ],
  },
  {
    key: "disciplinary-actions", table: "disciplinary_actions", label: "Disciplinary Actions", icon: "🛑",
    description: "Safety-rule violation cases and outcomes.",
    fields: [
      { name: "case_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "violation_type", label: "Violation Type", type: "select", options: ["PPE Violation","Safety Rule Breach","Permit Violation","Unauthorized Work","Reckless Behavior","Substance Abuse"], role: "category" },
      { name: "offense_level", label: "Offense Level", type: "select", options: ["1st Offense","2nd Offense","3rd Offense","Repeat"] },
      { name: "action_taken", label: "Action Taken", type: "select", options: ["Verbal Warning","Written Warning","Suspension","Retraining","Termination"] },
      { name: "status", label: "Status", type: "select", options: ["Completed","Under Review","Appealed"], role: "status" },
    ],
  },
  {
    key: "safety-awards", table: "safety_awards", label: "Safety Awards", icon: "🏅",
    description: "Recognition & reward programme records.",
    fields: [
      { name: "award_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "award_category", label: "Award Category", type: "select", options: ["Safe Worker of Month","Best Safety Suggestion","Zero Incident Award","HSE Champion","Safety Innovation","Best Department"], role: "category" },
      { name: "reward_type", label: "Reward Type", type: "select", options: ["Certificate","Trophy","Cash Bonus","Gift Voucher","Recognition Letter"] },
      { name: "recipient", label: "Recipient", type: "text" },
      { name: "status", label: "Status", type: "select", options: ["Presented","Scheduled","Nominated"], role: "status" },
    ],
  },
  {
    key: "stop-work-authority", table: "stop_work_authority", label: "Stop Work Authority", icon: "✋",
    description: "Stop-work events — downtime and resolution.",
    fields: [
      { name: "event_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "severity", label: "Severity", type: "select", options: ["Critical","High","Medium"], role: "risk" },
      { name: "downtime_min", label: "Downtime (min)", type: "number" },
      { name: "resolution", label: "Resolution", type: "select", options: ["Resolved","Permanent Fix Applied","Under Investigation"], role: "status" },
      { name: "investigation_done", label: "Investigation Done", type: "select", options: YESNO },
      { name: "description", label: "Description", type: "text" },
    ],
  },
  {
    key: "alcohol-tests", table: "alcohol_tests", label: "Alcohol Tests", icon: "🧪",
    description: "Random/pre-shift alcohol testing records.",
    fields: [
      { name: "test_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "test_type", label: "Test Type", type: "select", options: ["Pre-Shift","Random","Post-Incident","Reasonable Suspicion"], role: "category" },
      { name: "result", label: "Result", type: "select", options: ["Negative","Positive"], required: true, role: "status" },
      { name: "person_type", label: "Person Type", type: "select", options: ["Employee","Contractor","Visitor","Third Party"] },
    ],
  },
  {
    key: "ptw-audits", table: "ptw_audits", label: "PTW Audits", icon: "📝",
    description: "Permit-to-Work compliance audits.",
    fields: [
      { name: "audit_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "permit_type", label: "Permit Type", type: "select", options: ["Hot Work","Confined Space","Working at Height","Electrical","Cold Work","Lifting","Excavation"], role: "category" },
      { name: "auditor", label: "Auditor", type: "text" },
      { name: "permits_reviewed", label: "Permits Reviewed", type: "number" },
      { name: "deviations_found", label: "Deviations Found", type: "number" },
      { name: "compliance_pct", label: "Compliance %", type: "number", role: "metric_pct" },
      { name: "verdict", label: "Verdict", type: "select", options: ["Compliant","Non-Compliant","Partially Compliant"], role: "status" },
    ],
  },
  {
    key: "corrective-actions", table: "corrective_actions", label: "Corrective Actions", icon: "🔧",
    description: "CAPA tracker — priority, source and closure.",
    fields: [
      { name: "date_raised", label: "Date Raised", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "source", label: "Source", type: "select", options: ["Audit Finding","Inspection Finding","Incident Follow-up","Observation","Drill Finding","Management Review"], role: "category" },
      { name: "priority", label: "Priority", type: "select", options: ["Critical","High","Medium","Low"] },
      { name: "description", label: "Description", type: "text" },
      { name: "status", label: "Status", type: "select", options: ["Completed","In Progress","Overdue","Pending","Cancelled"], role: "status" },
      { name: "due_date", label: "Due Date", type: "date" },
      { name: "completion_date", label: "Completion Date", type: "date" },
      { name: "assigned_to", label: "Assigned To", type: "text" },
    ],
  },
  {
    key: "nc-management", table: "nc_management", label: "NC Management", icon: "🚫",
    description: "Non-conformance tracker — severity and closure.",
    fields: [
      { name: "date_raised", label: "Date Raised", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "severity", label: "Severity", type: "select", options: ["Major","Minor","Observation"], role: "risk" },
      { name: "root_cause_capa", label: "Root Cause / CAPA", type: "text" },
      { name: "status", label: "Status", type: "select", options: ["Closed","Open","Under Review","Overdue"], role: "status" },
      { name: "due_date", label: "Due Date", type: "date" },
      { name: "actual_close_date", label: "Actual Close Date", type: "date" },
    ],
  },
  {
    key: "unsafe-acts", table: "unsafe_acts", label: "Unsafe Acts", icon: "🙅",
    description: "Unsafe-act reports — risk level and corrective action.",
    fields: [
      { name: "report_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "description", label: "Description", type: "text" },
      { name: "risk_level", label: "Risk Level", type: "select", options: RISK_LEVELS, role: "risk" },
      { name: "immediate_action", label: "Immediate Action", type: "text" },
      { name: "corrective_action", label: "Corrective Action", type: "text" },
      { name: "due_date", label: "Due Date", type: "date" },
      { name: "status", label: "Status", type: "select", options: STATUS4, role: "status" },
      { name: "reported_by", label: "Reported By", type: "text" },
    ],
  },
  {
    key: "unsafe-conditions", table: "unsafe_conditions", label: "Unsafe Conditions", icon: "⛔",
    description: "Unsafe-condition reports — risk level and corrective action.",
    fields: [
      { name: "report_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "description", label: "Description", type: "text" },
      { name: "risk_level", label: "Risk Level", type: "select", options: RISK_LEVELS, role: "risk" },
      { name: "immediate_action", label: "Immediate Action", type: "text" },
      { name: "corrective_action", label: "Corrective Action", type: "text" },
      { name: "due_date", label: "Due Date", type: "date" },
      { name: "status", label: "Status", type: "select", options: STATUS4, role: "status" },
      { name: "reported_by", label: "Reported By", type: "text" },
    ],
  },
  {
    key: "incidents", table: "incidents", label: "Incident", icon: "🔥",
    description: "Injuries, near-misses and other incidents.",
    fields: [
      { name: "incident_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "area", label: "Area", type: "text" },
      { name: "classification", label: "Classification", type: "select", options: ["Near Miss","First Aid","Medical Treatment","Restricted Work","Lost Time Injury","Fatality"], required: true, role: "category" },
      { name: "body_part", label: "Body Part", type: "select", options: ["Head","Eye","Hand/Finger","Arm","Foot/Leg","Back","Torso","Multiple"] },
      { name: "risk_rating", label: "Risk Rating", type: "select", options: RISK_LEVELS, role: "risk" },
      { name: "lost_days", label: "Lost Days", type: "number" },
      { name: "root_cause", label: "Root Cause", type: "text" },
      { name: "description", label: "Description", type: "text" },
      { name: "status", label: "Status", type: "select", options: ["Open","In Progress","Closed"], role: "status" },
      { name: "closure_date", label: "Closure Date", type: "date" },
    ],
  },
  {
    key: "environmental-performance", table: "environmental_performance", label: "Environmental Performance", icon: "🌱",
    description: "Waste, energy, water & fuel consumption.",
    fields: [
      { name: "record_date", label: "Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "location", label: "Location", type: "text" },
      { name: "waste_type", label: "Waste Type", type: "select", options: ["General Waste","Hazardous Waste","E-Waste","Plastic","Metal Scrap","Organic/Food Waste"], role: "category" },
      { name: "waste_generated_kg", label: "Waste Generated (kg)", type: "number" },
      { name: "waste_recycled_kg", label: "Waste Recycled (kg)", type: "number" },
      { name: "recycle_rate_pct", label: "Recycle Rate %", type: "number", role: "metric_pct" },
      { name: "energy_kwh", label: "Energy (kWh)", type: "number" },
      { name: "water_m3", label: "Water (m3)", type: "number" },
      { name: "fuel_l", label: "Fuel (L)", type: "number" },
      { name: "remarks", label: "Remarks", type: "text" },
    ],
  },
  {
    key: "statutory-compliance", table: "statutory_compliance", label: "Statutory Compliance Register", icon: "🏛️",
    description: "Legal & regulatory requirements — licenses, renewals, statutory inspections and next-due tracking.",
    fields: [
      { name: "review_date", label: "Review Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "requirement", label: "Requirement", type: "text", required: true },
      { name: "applicable_law", label: "Applicable Law / Act", type: "text" },
      { name: "frequency", label: "Frequency", type: "select", options: ["One-time","Monthly","Quarterly","Half-Yearly","Annually"], role: "category" },
      { name: "last_complied_date", label: "Last Complied Date", type: "date" },
      { name: "next_due_date", label: "Next Due Date", type: "date" },
      { name: "status", label: "Status", type: "select", options: ["Complied","Pending","Overdue"], role: "status" },
      { name: "responsible_person", label: "Responsible Person", type: "text" },
      { name: "remarks", label: "Remarks", type: "text" },
    ],
  },
  {
    key: "employee-engagement", table: "employee_engagement", label: "Employee Engagement", icon: "🎉",
    description: "Fun activities, wellness, CSR and team events — calendar, photos and participation.",
    fields: [
      { name: "event_date", label: "Event Date", type: "date", required: true, role: "date" },
      { name: "department", label: "Department", type: "department", required: true, role: "department" },
      { name: "event_name", label: "Event Name", type: "text", required: true },
      { name: "category", label: "Category", type: "select", options: ["Fun Activity","Award Ceremony","Team Building","Wellness","CSR","Sports","Cultural"], role: "category" },
      { name: "participation_count", label: "Participation Count", type: "number" },
      { name: "feedback_score_pct", label: "Feedback Score %", type: "number", role: "metric_pct" },
      { name: "status", label: "Status", type: "select", options: ["Completed","Planned"], role: "status" },
      { name: "remarks", label: "Remarks", type: "text" },
    ],
  },
];

export function trackerByKey(key: string): TrackerDef | undefined {
  return TRACKERS.find((t) => t.key === key);
}

/** Leading vs lagging classification, standard EHS theory: lagging = an
 * outcome measured after harm/a violation has already occurred (incidents,
 * disciplinary cases); everything else here is a proactive/preventive
 * activity carried out to stop that outcome happening - leading. */
const LAGGING_TRACKER_KEYS = new Set(["incidents", "disciplinary-actions"]);
export function natureOf(t: TrackerDef): "leading" | "lagging" {
  return LAGGING_TRACKER_KEYS.has(t.key) ? "lagging" : "leading";
}

export function dateFieldOf(t: TrackerDef): string {
  return t.fields.find((f) => f.role === "date")!.name;
}

export function toColumnSpecs(t: TrackerDef): ColumnSpec[] {
  return t.fields.map((f) => ({
    name: f.name,
    type: f.dataType ?? (f.type === "select" || f.type === "department" ? "text" : f.type),
    required: f.required,
  }));
}
