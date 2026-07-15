/** Bespoke, tracker-specific KPI card definitions - one set of 8 cards per
 * tracker, mirroring the exact KPI cards the Excel system's _kpi_defs()
 * produces for each register, rather than the generic role-driven set.
 * computeSnapshot() in aggregate.ts falls back to the generic set only for
 * a tracker key that has no entry here. */

type Row = Record<string, string | number | boolean | null>;
type Kpi = { icon: string; label: string; value: string; accent: "teal" | "gold" | "purple" | "coral" };

const RECORDABLE = ["Medical Treatment", "Restricted Work", "Lost Time Injury", "Fatality"];
const CLOSED = new Set(["Completed", "Compliant", "Approved", "Closed"]);

function n(v: unknown): number {
  const x = Number(v);
  return isNaN(x) ? 0 : x;
}
function countIf(rows: Row[], pred: (r: Row) => boolean): number {
  return rows.filter(pred).length;
}
function is(field: string, val: string) {
  return (r: Row) => String(r[field]) === val;
}
function isIn(field: string, vals: string[]) {
  return (r: Row) => vals.includes(String(r[field]));
}
function sumField(rows: Row[], field: string): number {
  return rows.reduce((a, r) => a + n(r[field]), 0);
}
function avgField(rows: Row[], field: string, decimals = 0): number {
  const vals = rows.map((r) => Number(r[field])).filter((v) => !isNaN(v));
  if (!vals.length) return 0;
  const a = vals.reduce((x, y) => x + y, 0) / vals.length;
  const f = 10 ** decimals;
  return Math.round(a * f) / f;
}
function distinctField(rows: Row[], field: string): number {
  return new Set(rows.map((r) => String(r[field] ?? "")).filter((v) => v && v !== "null")).size;
}
function pct(part: number, total: number): number {
  return total ? Math.round((part / total) * 100) : 0;
}
function closedCount(rows: Row[], field: string): number {
  return countIf(rows, (r) => CLOSED.has(String(r[field])));
}
function k(icon: string, label: string, value: string | number, accent: Kpi["accent"]): Kpi {
  return { icon, label, value: String(value), accent };
}

type Builder = (rows: Row[]) => Kpi[];

const BUILDERS: Record<string, Builder> = {
  "toolbox-talks": (rows) => [
    k("🗣️", "Total Talks", rows.length, "teal"),
    k("⚠️", "Action Required: Yes", countIf(rows, is("action_required", "Yes")), "coral"),
    k("✅", "Action Required: No", countIf(rows, is("action_required", "No")), "teal"),
    k("📊", "Avg Attendance %", `${avgField(rows, "attendance_pct")}%`, "gold"),
    k("🎯", "Total Target Attendees", sumField(rows, "target_attendees"), "purple"),
    k("👥", "Total Actual Attendees", sumField(rows, "actual_attendees"), "purple"),
    k("⏱️", "Avg Duration (min)", avgField(rows, "duration_min"), "gold"),
    k("📚", "Topics Covered", distinctField(rows, "topic"), "teal"),
  ],
  jsa: (rows) => {
    const scores = rows.map((r) => n(r.likelihood) * n(r.consequence)).filter((v) => v > 0);
    const avgScore = scores.length ? Math.round((scores.reduce((a, b) => a + b, 0) / scores.length) * 10) / 10 : 0;
    return [
      k("📋", "Total JSAs", rows.length, "teal"),
      k("✅", "Approved", countIf(rows, is("approval_status", "Approved")), "teal"),
      k("⏳", "Pending Review", countIf(rows, is("approval_status", "Pending Review")), "gold"),
      k("🔴", "High / Critical Risk", countIf(rows, isIn("risk_level", ["Critical", "High"])), "coral"),
      k("🟡", "Medium Risk", countIf(rows, is("risk_level", "Medium")), "gold"),
      k("🟢", "Low Risk", countIf(rows, is("risk_level", "Low")), "teal"),
      k("⚠️", "Total Hazards Identified", sumField(rows, "hazards_identified"), "purple"),
      k("🎯", "Avg Risk Score", avgScore, "coral"),
      k("🛠️", "HIRA Controls Compliance %", `${avgField(rows, "controls_compliance_pct")}%`, "teal"),
    ];
  },
  training: (rows) => [
    k("🎓", "Total Trainings", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("🗓️", "Scheduled", countIf(rows, is("status", "Scheduled")), "purple"),
    k("📊", "Avg Attendance %", `${avgField(rows, "attendance_pct")}%`, "gold"),
    k("✅", "Pass Rate %", `${pct(countIf(rows, is("assessment_result", "Pass")), countIf(rows, isIn("assessment_result", ["Pass", "Fail"])))}%`, "teal"),
    k("❌", "Fail Count", countIf(rows, is("assessment_result", "Fail")), "coral"),
    k("📚", "Training Types Covered", distinctField(rows, "training_type"), "purple"),
  ],
  "hse-observations": (rows) => [
    k("👁️", "Total Observations", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("🟢", "Safe Acts / Conditions", countIf(rows, isIn("observation_type", ["Safe Act", "Safe Condition"])), "teal"),
    k("🔴", "Unsafe Acts / Conditions", countIf(rows, isIn("observation_type", ["Unsafe Act", "Unsafe Condition"])), "coral"),
    k("⚠️", "High / Critical Risk", countIf(rows, isIn("risk_level", ["Critical", "High"])), "coral"),
    k("📊", "Closure %", `${pct(closedCount(rows, "status"), rows.length)}%`, "gold"),
  ],
  "workplace-inspections": (rows) => [
    k("🔍", "Total Inspections", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("🔴", "Critical Findings", sumField(rows, "critical_findings"), "coral"),
    k("🚫", "Non-Conformances", sumField(rows, "non_conformances"), "gold"),
    k("📊", "Completion %", `${pct(closedCount(rows, "status"), rows.length)}%`, "gold"),
    k("⏳", "Pending", countIf(rows, is("status", "Pending")), "purple"),
    k("📉", "Avg NC per Inspection", avgField(rows, "non_conformances", 1), "purple"),
  ],
  "equipment-inspections": (rows) => [
    k("🛠️", "Total Inspections", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("🔴", "Critical Findings", sumField(rows, "critical_findings"), "coral"),
    k("📋", "Checkpoints Inspected", sumField(rows, "checkpoints_inspected"), "purple"),
    k("🚫", "Non-Conformances", sumField(rows, "non_conformances"), "gold"),
    k("📊", "Completion %", `${pct(closedCount(rows, "status"), rows.length)}%`, "gold"),
    k("🌟", "Excellent Rating", countIf(rows, is("overall_rating", "Excellent")), "teal"),
  ],
  "safety-walkthroughs": (rows) => [
    k("🚶", "Total Walkthroughs", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("📊", "Avg Completion %", `${avgField(rows, "completion_pct")}%`, "gold"),
    k("🔴", "Critical Findings", sumField(rows, "critical_findings"), "coral"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("✅", "Closure %", `${pct(closedCount(rows, "status"), rows.length)}%`, "teal"),
    k("🗺️", "Areas Covered", distinctField(rows, "area"), "purple"),
  ],
  "safety-meetings": (rows) => [
    k("🗓️", "Total Meetings", rows.length, "teal"),
    k("📊", "Avg Attendance %", `${avgField(rows, "attendance_pct")}%`, "gold"),
    k("📌", "Actions Raised", sumField(rows, "action_items_raised"), "purple"),
    k("✅", "Actions Closed", sumField(rows, "actions_closed"), "teal"),
    k("📈", "Avg Close-out %", `${avgField(rows, "closeout_pct")}%`, "gold"),
    k("⏱️", "Total Hours", Math.round((sumField(rows, "duration_min") / 60) * 10) / 10, "purple"),
    k("📄", "MoM Circulated", countIf(rows, is("mom_circulated", "Yes")), "teal"),
    k("📄", "MoM Pending", countIf(rows, is("mom_circulated", "No")), "coral"),
  ],
  "safety-bulletins": (rows) => [
    k("📰", "Total Bulletins", rows.length, "teal"),
    k("📤", "Issued", countIf(rows, is("status", "Issued")), "gold"),
    k("👍", "Acknowledged", countIf(rows, is("status", "Acknowledged")), "purple"),
    k("✅", "Closed", countIf(rows, is("status", "Closed")), "teal"),
    k("🎯", "Total Target Reach", sumField(rows, "target_reach"), "purple"),
    k("👥", "Total Actual Reach", sumField(rows, "actual_reach"), "purple"),
    k("📊", "Avg Reach %", `${avgField(rows, "reach_pct")}%`, "gold"),
    k("🔴", "High Priority", countIf(rows, isIn("priority", ["Critical", "High"])), "coral"),
  ],
  "emergency-drills": (rows) => [
    k("🚨", "Total Drills", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("⏳", "Action Pending", countIf(rows, is("status", "Action Pending")), "coral"),
    k("📊", "Avg Participation %", `${avgField(rows, "participation_pct")}%`, "gold"),
    k("🎯", "Avg Target Response (min)", avgField(rows, "target_response_min", 1), "purple"),
    k("⏱️", "Avg Actual Response (min)", avgField(rows, "actual_response_min", 1), "purple"),
    k("👥", "Total Participants", sumField(rows, "actual_participants"), "teal"),
    k("🔄", "Rescheduled", countIf(rows, is("status", "Rescheduled")), "gold"),
  ],
  "internal-audits": (rows) => [
    k("📋", "Total Audits", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("🗓️", "Scheduled", countIf(rows, is("status", "Scheduled")), "purple"),
    k("☑️", "Checklist Items", sumField(rows, "checklist_items"), "purple"),
    k("🟡", "Minor NC", sumField(rows, "minor_nc"), "gold"),
    k("🔴", "Major NC", sumField(rows, "major_nc"), "coral"),
    k("👁️", "Observations", sumField(rows, "observations"), "teal"),
  ],
  "external-audits": (rows) => [
    k("🏛️", "Total Audits", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("🗓️", "Scheduled", countIf(rows, is("status", "Scheduled")), "purple"),
    k("☑️", "Checklist Items", sumField(rows, "checklist_items"), "purple"),
    k("🟡", "Minor NC", sumField(rows, "minor_nc"), "gold"),
    k("🔴", "Major NC", sumField(rows, "major_nc"), "coral"),
    k("👁️", "Observations", sumField(rows, "observations"), "teal"),
  ],
  "management-visits": (rows) => [
    k("🧑‍💼", "Total Visits", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("⏳", "Action Pending", countIf(rows, is("status", "Action Pending")), "coral"),
    k("👁️", "Observations Made", sumField(rows, "observations_made"), "purple"),
    k("📌", "Actions Raised", sumField(rows, "actions_raised"), "purple"),
    k("✅", "Actions Closed", sumField(rows, "actions_closed"), "teal"),
    k("📈", "Avg Close-out %", `${avgField(rows, "closeout_pct")}%`, "gold"),
    k("🗂️", "Visit Types Covered", distinctField(rows, "visit_type"), "purple"),
  ],
  "management-reviews": (rows) => [
    k("🧭", "Total Reviews", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("📊", "Avg Attendance %", `${avgField(rows, "attendance_pct")}%`, "gold"),
    k("📌", "Decisions Made", sumField(rows, "decisions_made"), "purple"),
    k("📋", "Actions Assigned", sumField(rows, "actions_assigned"), "purple"),
    k("📈", "Avg Close-out %", `${avgField(rows, "closeout_pct")}%`, "teal"),
    k("📄", "MoM Distributed", countIf(rows, is("mom_distributed", "Yes")), "teal"),
  ],
  "disciplinary-actions": (rows) => [
    k("🛑", "Total Cases", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("⏳", "Under Review", countIf(rows, is("status", "Under Review")), "gold"),
    k("📢", "Appealed", countIf(rows, is("status", "Appealed")), "coral"),
    k("🟢", "1st Offense", countIf(rows, is("offense_level", "1st Offense")), "teal"),
    k("🔴", "Repeat Offenders", countIf(rows, isIn("offense_level", ["2nd Offense", "3rd Offense", "Repeat"])), "coral"),
    k("⛔", "Suspensions", countIf(rows, is("action_taken", "Suspension")), "coral"),
    k("🚫", "Terminations", countIf(rows, is("action_taken", "Termination")), "coral"),
  ],
  "safety-awards": (rows) => [
    k("🏅", "Total Awards", rows.length, "teal"),
    k("✅", "Presented", countIf(rows, is("status", "Presented")), "teal"),
    k("🗓️", "Scheduled", countIf(rows, is("status", "Scheduled")), "gold"),
    k("📝", "Nominated", countIf(rows, is("status", "Nominated")), "purple"),
    k("📜", "Certificates", countIf(rows, is("reward_type", "Certificate")), "teal"),
    k("💰", "Cash Bonus", countIf(rows, is("reward_type", "Cash Bonus")), "gold"),
    k("🏆", "Trophies", countIf(rows, is("reward_type", "Trophy")), "purple"),
    k("🎁", "Vouchers", countIf(rows, is("reward_type", "Gift Voucher")), "teal"),
  ],
  "stop-work-authority": (rows) => [
    k("✋", "Total SWA Events", rows.length, "teal"),
    k("✅", "Resolved", countIf(rows, is("resolution", "Resolved")), "teal"),
    k("🔎", "Under Investigation", countIf(rows, is("resolution", "Under Investigation")), "gold"),
    k("🔧", "Permanent Fix Applied", countIf(rows, is("resolution", "Permanent Fix Applied")), "teal"),
    k("🔴", "Critical Severity", countIf(rows, is("severity", "Critical")), "coral"),
    k("🟠", "High Severity", countIf(rows, is("severity", "High")), "gold"),
    k("⏱️", "Total Downtime (min)", sumField(rows, "downtime_min"), "purple"),
    k("🔍", "Investigated", countIf(rows, is("investigation_done", "Yes")), "teal"),
  ],
  "alcohol-tests": (rows) => [
    k("🧪", "Total Tests", rows.length, "teal"),
    k("✅", "Negative", countIf(rows, is("result", "Negative")), "teal"),
    k("🔴", "Positive", countIf(rows, is("result", "Positive")), "coral"),
    k("📊", "Pass Rate %", `${pct(countIf(rows, is("result", "Negative")), rows.length)}%`, "gold"),
    k("🎲", "Random Tests", countIf(rows, is("test_type", "Random")), "purple"),
    k("🌅", "Pre-Shift Tests", countIf(rows, is("test_type", "Pre-Shift")), "purple"),
    k("🚑", "Post-Incident Tests", countIf(rows, is("test_type", "Post-Incident")), "gold"),
    k("🔍", "Reasonable Suspicion", countIf(rows, is("test_type", "Reasonable Suspicion")), "coral"),
  ],
  "ptw-audits": (rows) => [
    k("📝", "Total Audits", rows.length, "teal"),
    k("✅", "Compliant", countIf(rows, is("verdict", "Compliant")), "teal"),
    k("🔴", "Non-Compliant", countIf(rows, is("verdict", "Non-Compliant")), "coral"),
    k("🟡", "Partially Compliant", countIf(rows, is("verdict", "Partially Compliant")), "gold"),
    k("📋", "Permits Reviewed", sumField(rows, "permits_reviewed"), "purple"),
    k("⚠️", "Deviations Found", sumField(rows, "deviations_found"), "coral"),
    k("📊", "Avg Compliance %", `${avgField(rows, "compliance_pct")}%`, "gold"),
    k("📈", "Compliance Rate %", `${pct(countIf(rows, is("verdict", "Compliant")), rows.length)}%`, "teal"),
  ],
  "corrective-actions": (rows) => [
    k("🔧", "Total CAs", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("📊", "Completion %", `${pct(closedCount(rows, "status"), rows.length)}%`, "gold"),
    k("🔴", "High / Critical Priority", countIf(rows, isIn("priority", ["Critical", "High"])), "coral"),
    k("🟡", "Medium Priority", countIf(rows, is("priority", "Medium")), "gold"),
    k("🟢", "Low Priority", countIf(rows, is("priority", "Low")), "teal"),
  ],
  "nc-management": (rows) => [
    k("🚫", "Total NCs", rows.length, "teal"),
    k("✅", "Closed", countIf(rows, is("status", "Closed")), "teal"),
    k("🔓", "Open", countIf(rows, is("status", "Open")), "gold"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("📊", "Closure %", `${pct(closedCount(rows, "status"), rows.length)}%`, "teal"),
    k("🔴", "Major", countIf(rows, is("severity", "Major")), "coral"),
    k("🟡", "Minor", countIf(rows, is("severity", "Minor")), "gold"),
    k("👁️", "Observations", countIf(rows, is("severity", "Observation")), "purple"),
  ],
  "unsafe-acts": (rows) => [
    k("🙅", "Total Reports", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("🔴", "High / Critical Risk", countIf(rows, isIn("risk_level", ["Critical", "High"])), "coral"),
    k("🟡", "Medium Risk", countIf(rows, is("risk_level", "Medium")), "gold"),
    k("🟢", "Low Risk", countIf(rows, is("risk_level", "Low")), "teal"),
    k("📊", "Closure %", `${pct(closedCount(rows, "status"), rows.length)}%`, "purple"),
  ],
  "unsafe-conditions": (rows) => [
    k("⛔", "Total Reports", rows.length, "teal"),
    k("✅", "Completed", countIf(rows, is("status", "Completed")), "teal"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("⏰", "Overdue", countIf(rows, is("status", "Overdue")), "coral"),
    k("🔴", "High / Critical Risk", countIf(rows, isIn("risk_level", ["Critical", "High"])), "coral"),
    k("🟡", "Medium Risk", countIf(rows, is("risk_level", "Medium")), "gold"),
    k("🟢", "Low Risk", countIf(rows, is("risk_level", "Low")), "teal"),
    k("📊", "Closure %", `${pct(closedCount(rows, "status"), rows.length)}%`, "purple"),
  ],
  incidents: (rows) => [
    k("🔥", "Total Incidents", rows.length, "teal"),
    k("🔓", "Open", countIf(rows, is("status", "Open")), "coral"),
    k("🔄", "In Progress", countIf(rows, is("status", "In Progress")), "gold"),
    k("✅", "Closed", countIf(rows, is("status", "Closed")), "teal"),
    k("🟡", "Near Miss", countIf(rows, is("classification", "Near Miss")), "gold"),
    k("🔴", "Recordable", countIf(rows, isIn("classification", RECORDABLE)), "coral"),
    k("⚠️", "LTI + Fatality", countIf(rows, isIn("classification", ["Lost Time Injury", "Fatality"])), "coral"),
    k("📉", "Total Lost Days", sumField(rows, "lost_days"), "purple"),
  ],
  "environmental-performance": (rows) => [
    k("🌱", "Total Records", rows.length, "teal"),
    k("🗑️", "Waste Generated (kg)", sumField(rows, "waste_generated_kg"), "gold"),
    k("♻️", "Waste Recycled (kg)", sumField(rows, "waste_recycled_kg"), "teal"),
    k("📊", "Avg Recycle Rate %", `${avgField(rows, "recycle_rate_pct")}%`, "teal"),
    k("⚡", "Energy Consumed (kWh)", sumField(rows, "energy_kwh"), "purple"),
    k("💧", "Water Consumed (m³)", sumField(rows, "water_m3"), "purple"),
    k("⛽", "Fuel Consumed (L)", sumField(rows, "fuel_l"), "gold"),
    k("☣️", "Hazardous Waste Events", countIf(rows, is("waste_type", "Hazardous Waste")), "coral"),
  ],
};

export function bespokeKpis(trackerKey: string, rows: Row[]): Kpi[] | null {
  const builder = BUILDERS[trackerKey];
  return builder ? builder(rows) : null;
}
