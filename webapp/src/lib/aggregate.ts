import { TrackerDef, TrackerField, dateFieldOf } from "./trackers";
import { CLOSED_LIKE } from "./constants";

export type Row = Record<string, string | number | boolean | null>;

export type Kpi = { icon: string; label: string; value: string; accent: "teal" | "gold" | "purple" | "coral" };
export type ChartSpec =
  | { type: "trend"; title: string; data: { label: string; value: number }[] }
  | { type: "bar"; title: string; data: { label: string; value: number }[] }
  | { type: "donut"; title: string; data: { label: string; value: number }[] };

export type DeptRow = { department: string; count: number; closedPct: number | null; avgMetric: number | null };
export type MonthRow = { month: string; count: number; avgMetric: number | null };

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

function average(vals: number[]) {
  return vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : null;
}

/** Live "Department Performance" table - one row per department: record count,
 * closed/completed % (if this tracker has a status field), average of the
 * headline metric_pct field (if it has one). Mirrors the Excel per-register
 * dashboard's Department Performance block. */
function departmentTable(tracker: TrackerDef, rows: Row[]): DeptRow[] {
  const deptField = fieldWithRole(tracker.fields, "department");
  if (!deptField) return [];
  const statusField = fieldWithRole(tracker.fields, "status");
  const metricField = fieldWithRole(tracker.fields, "metric_pct");
  const byDept = new Map<string, Row[]>();
  for (const r of rows) {
    const d = String(r[deptField.name] ?? "(blank)");
    if (!byDept.has(d)) byDept.set(d, []);
    byDept.get(d)!.push(r);
  }
  return [...byDept.entries()]
    .map(([department, rs]) => {
      const closedPct = statusField
        ? Math.round((100 * rs.filter((r) => CLOSED_LIKE.has(String(r[statusField.name]))).length) / rs.length)
        : null;
      const avgMetric = metricField
        ? (() => {
            const vals = rs.map((r) => Number(r[metricField.name])).filter((v) => !isNaN(v));
            const a = average(vals);
            return a === null ? null : Math.round(a);
          })()
        : null;
      return { department, count: rs.length, closedPct, avgMetric };
    })
    .sort((a, b) => b.count - a.count);
}

/** Live "Monthly Performance Matrix" - one row per month: record count and the
 * average metric_pct for that month, mirroring the Excel per-register
 * dashboard's Monthly Performance Matrix. */
function monthlyMatrix(tracker: TrackerDef, rows: Row[]): MonthRow[] {
  const dateField = dateFieldOf(tracker);
  const metricField = fieldWithRole(tracker.fields, "metric_pct");
  const buckets: Row[][] = Array.from({ length: 12 }, () => []);
  for (const r of rows) {
    const v = r[dateField];
    if (!v) continue;
    const d = new Date(String(v));
    if (isNaN(d.getTime())) continue;
    buckets[d.getMonth()].push(r);
  }
  return MONTHS.map((m, i) => {
    const rs = buckets[i];
    const avgMetric = metricField
      ? (() => {
          const vals = rs.map((r) => Number(r[metricField.name])).filter((v) => !isNaN(v));
          const a = average(vals);
          return a === null ? null : Math.round(a);
        })()
      : null;
    return { month: m, count: rs.length, avgMetric };
  });
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
    const open = rows.filter((r) => !CLOSED_LIKE.has(String(r[statusField.name]))).length;
    kpis.push({ icon: "🔓", label: "Open / In Progress", value: String(open), accent: "gold" });
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
  const now = new Date();
  const thisMonthCount = rows.filter((r) => {
    const v = r[dateField];
    if (!v) return false;
    const d = new Date(String(v));
    return !isNaN(d.getTime()) && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).length;
  kpis.push({ icon: "🗓️", label: "This Month", value: String(thisMonthCount), accent: "purple" });

  const charts: ChartSpec[] = [{ type: "trend", title: "Monthly Trend", data: monthlyTrend(rows, dateField) }];

  if (statusField) charts.push({ type: "donut", title: `${statusField.label} Mix`, data: countBy(rows, statusField.name) });

  const catField = fieldWithRole(tracker.fields, "category");
  if (catField) charts.push({ type: "bar", title: `${catField.label} Breakdown`, data: countBy(rows, catField.name) });

  if (riskField) charts.push({ type: "donut", title: `${riskField.label} Mix`, data: countBy(rows, riskField.name) });

  if (deptField) charts.push({ type: "bar", title: "Department Breakdown", data: countBy(rows, deptField.name) });

  return {
    kpis,
    charts,
    deptTable: departmentTable(tracker, rows),
    monthMatrix: monthlyMatrix(tracker, rows),
    hasMetric: !!metricField,
    metricLabel: metricField?.label,
    hasStatus: !!statusField,
  };
}
