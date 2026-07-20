import { TrackerDef, TrackerField, dateFieldOf } from "./trackers";
import { CLOSED_LIKE } from "./constants";
import { bespokeKpis } from "./kpiDefs";

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

const SEVERE_VALUES = new Set(["Critical", "High", "Major"]);

/** Overdue-ageing buckets (0-7/8-15/16-30/30+ days past due, open items only) -
 * generic for any tracker that has both a status field and a "due_date" column,
 * mirroring the Excel Advanced Analysis ageing chart. */
function agingChart(tracker: TrackerDef, rows: Row[]): { label: string; value: number }[] | null {
  const statusField = fieldWithRole(tracker.fields, "status");
  const dueField = tracker.fields.find((f) => f.name === "due_date");
  if (!statusField || !dueField) return null;
  const buckets = { "0-7": 0, "8-15": 0, "16-30": 0, "30+": 0 };
  const now = Date.now();
  for (const r of rows) {
    if (CLOSED_LIKE.has(String(r[statusField.name]))) continue;
    const due = r[dueField.name];
    if (!due) continue;
    const days = Math.floor((now - new Date(String(due)).getTime()) / 86400000);
    if (days < 0) continue;
    if (days <= 7) buckets["0-7"]++;
    else if (days <= 15) buckets["8-15"]++;
    else if (days <= 30) buckets["16-30"]++;
    else buckets["30+"]++;
  }
  return Object.entries(buckets).map(([label, value]) => ({ label, value }));
}

/** Repeat-offender department watchlist: top-5 departments by count of
 * Critical/High/Major severity items - generic for any tracker with both a
 * department field and a risk/severity field. */
function hotspotTable(tracker: TrackerDef, rows: Row[]): { department: string; count: number }[] {
  const deptField = fieldWithRole(tracker.fields, "department");
  const riskField = fieldWithRole(tracker.fields, "risk");
  if (!deptField || !riskField) return [];
  const counts = new Map<string, number>();
  for (const r of rows) {
    if (!SEVERE_VALUES.has(String(r[riskField.name]))) continue;
    const d = String(r[deptField.name] ?? "(blank)");
    counts.set(d, (counts.get(d) || 0) + 1);
  }
  return [...counts.entries()].map(([department, count]) => ({ department, count })).sort((a, b) => b.count - a.count).slice(0, 5);
}

export type ForecastPoint = { label: string; target: number | null; actual: number | null };

/** Target-vs-Actual monthly trend with a 13th "Next (fcst)" point projected by
 * simple linear regression over the 12 actual monthly values - generic for any
 * tracker with a target_num/actual_num field pair, mirrors the Excel system's
 * TREND()-based forecast blocks (a real projection, not a fabricated number). */
function forecastTrend(tracker: TrackerDef, rows: Row[]): ForecastPoint[] | null {
  const targetField = fieldWithRole(tracker.fields, "target_num");
  const actualField = fieldWithRole(tracker.fields, "actual_num");
  if (!targetField || !actualField) return null;
  const dateField = dateFieldOf(tracker);
  const targetSum = new Array(12).fill(0);
  const actualSum = new Array(12).fill(0);
  for (const r of rows) {
    const v = r[dateField];
    if (!v) continue;
    const d = new Date(String(v));
    if (isNaN(d.getTime())) continue;
    const m = d.getMonth();
    targetSum[m] += Number(r[targetField.name]) || 0;
    actualSum[m] += Number(r[actualField.name]) || 0;
  }
  // least-squares linear regression over the 12 actual points -> project month 13
  const n = 12;
  const xs = Array.from({ length: n }, (_, i) => i + 1);
  const xMean = xs.reduce((a, b) => a + b, 0) / n;
  const yMean = actualSum.reduce((a, b) => a + b, 0) / n;
  let num = 0, den = 0;
  for (let i = 0; i < n; i++) { num += (xs[i] - xMean) * (actualSum[i] - yMean); den += (xs[i] - xMean) ** 2; }
  const slope = den ? num / den : 0;
  const intercept = yMean - slope * xMean;
  const forecast = Math.max(0, Math.round(intercept + slope * 13));

  const points: ForecastPoint[] = MONTHS.map((m, i) => ({ label: m, target: targetSum[i], actual: actualSum[i] }));
  points.push({ label: "Next (fcst)", target: targetSum[11], actual: forecast });
  return points;
}

/** Generic KPI + chart computation, driven purely by each tracker's field roles
 * (date/department/status/category/risk/metric_pct) - same spec-driven approach
 * as the Excel system's _kpi_defs/_register_calc, so every one of the 25 trackers
 * gets a sensible dashboard without hand-writing 25 bespoke aggregations. */
function genericKpis(tracker: TrackerDef, rows: Row[]): Kpi[] {
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

  return kpis;
}

export function computeSnapshot(tracker: TrackerDef, rows: Row[]) {
  const kpis: Kpi[] = bespokeKpis(tracker.key, rows) ?? genericKpis(tracker, rows);

  const statusField = fieldWithRole(tracker.fields, "status");
  const riskField = fieldWithRole(tracker.fields, "risk");
  const metricField = fieldWithRole(tracker.fields, "metric_pct");
  const deptField = fieldWithRole(tracker.fields, "department");
  const dateField = dateFieldOf(tracker);

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
    aging: agingChart(tracker, rows),
    hotspot: hotspotTable(tracker, rows),
    forecast: forecastTrend(tracker, rows),
  };
}
