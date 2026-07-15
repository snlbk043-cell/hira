import { TrackerDef, TrackerField, dateFieldOf } from "./trackers";
import { CLOSED_LIKE } from "./constants";

export type Row = Record<string, string | number | boolean | null>;

export type Kpi = { icon: string; label: string; value: string; accent: "teal" | "gold" | "purple" | "coral" };
export type ChartSpec =
  | { type: "trend"; title: string; data: { label: string; value: number }[] }
  | { type: "bar"; title: string; data: { label: string; value: number }[] }
  | { type: "donut"; title: string; data: { label: string; value: number }[] };

const MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

export function monthlyTrend(rows: Row[], dateField: string) {
  const counts = new Array(12).fill(0);
  for (const r of rows) {
    const v = r[dateField];
    if (!v) continue;
    const d = new Date(String(v));
    if (isNaN(d.getTime())) continue;
    counts[d.getMonth()]++;
  }
  return MONTHS.map((m, i) => ({ label: m, value: counts[i] }));
}

export function countBy(rows: Row[], field: string) {
  const m = new Map<string, number>();
  for (const r of rows) {
    const v = r[field];
    const label = v === null || v === undefined || v === "" ? "(blank)" : String(v);
    m.set(label, (m.get(label) || 0) + 1);
  }
  return [...m.entries()]
    .map(([label, value]) => ({ label, value }))
    .sort((a, b) => b.value - a.value)
    .slice(0, 8);
}

function fieldWithRole(fields: TrackerField[], role: TrackerField["role"]) {
  return fields.find((f) => f.role === role);
}

/** Generic KPI + chart computation, driven purely by each tracker's field roles
 * (date/department/status/category/risk/metric_pct) - same spec-driven approach
 * as the Excel system's _kpi_defs/_register_calc, so every one of the 25 trackers
 * gets a sensible dashboard without hand-writing 25 bespoke aggregations. */
export function computeSnapshot(tracker: TrackerDef, rows: Row[]) {
  const total = rows.length;
  const kpis: Kpi[] = [{ icon: "📋", label: "Total Records", value: String(total), accent: "teal" }];

  const statusField = fieldWithRole(tracker.fields, "status");
  if (statusField) {
    const closed = rows.filter((r) => CLOSED_LIKE.has(String(r[statusField.name]))).length;
    const pct = total ? Math.round((closed / total) * 100) : 0;
    kpis.push({ icon: "✅", label: "Closed / Completed %", value: `${pct}%`, accent: "teal" });
    const overdue = rows.filter((r) => String(r[statusField.name]) === "Overdue").length;
    if (overdue > 0) kpis.push({ icon: "⏰", label: "Overdue", value: String(overdue), accent: "coral" });
  }

  const riskField = fieldWithRole(tracker.fields, "risk");
  if (riskField) {
    const high = rows.filter((r) => ["Critical", "High"].includes(String(r[riskField.name]))).length;
    kpis.push({ icon: "⚠️", label: "High / Critical", value: String(high), accent: "coral" });
  }

  const metricField = fieldWithRole(tracker.fields, "metric_pct");
  if (metricField) {
    const vals = rows.map((r) => Number(r[metricField.name])).filter((v) => !isNaN(v) && v !== null);
    const avg = vals.length ? Math.round(vals.reduce((a, b) => a + b, 0) / vals.length) : 0;
    kpis.push({ icon: "📈", label: `Avg ${metricField.label}`, value: `${avg}%`, accent: "gold" });
  }

  const deptField = fieldWithRole(tracker.fields, "department");
  if (deptField) {
    const byDept = countBy(rows, deptField.name);
    kpis.push({ icon: "🏢", label: "Departments Involved", value: String(byDept.length), accent: "purple" });
  }

  const dateField = dateFieldOf(tracker);
  const charts: ChartSpec[] = [{ type: "trend", title: "Monthly Trend", data: monthlyTrend(rows, dateField) }];

  if (statusField) charts.push({ type: "donut", title: `${statusField.label} Mix`, data: countBy(rows, statusField.name) });

  const catField = fieldWithRole(tracker.fields, "category");
  if (catField) charts.push({ type: "bar", title: `${catField.label} Breakdown`, data: countBy(rows, catField.name) });

  if (deptField) charts.push({ type: "bar", title: "Department Breakdown", data: countBy(rows, deptField.name) });

  return { kpis, charts };
}
