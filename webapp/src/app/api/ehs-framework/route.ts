import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { TRACKERS, TrackerDef, dateFieldOf } from "@/lib/trackers";
import { CLOSED_LIKE } from "@/lib/constants";

export const dynamic = "force-dynamic";

type Row = Record<string, unknown>;

/** Groups the 25 trackers into EHS management-system "elements" so Leadership
 * can see maturity by pillar, not just by individual register - same idea as
 * an ISO 45001-style elemental scorecard. */
const ELEMENTS: { key: string; label: string; icon: string; trackerKeys: string[] }[] = [
  { key: "leadership_training", label: "Leadership & Training", icon: "🎓", trackerKeys: ["training", "toolbox-talks", "safety-meetings", "management-reviews", "management-visits", "safety-awards", "employee-engagement"] },
  { key: "risk_management", label: "Risk Management (HIRA)", icon: "⚠️", trackerKeys: ["jsa", "hse-observations", "unsafe-acts", "unsafe-conditions", "stop-work-authority"] },
  { key: "inspection_audit", label: "Inspection & Audit", icon: "🔍", trackerKeys: ["workplace-inspections", "equipment-inspections", "safety-walkthroughs", "internal-audits", "external-audits", "ptw-audits", "alcohol-tests", "statutory-compliance"] },
  { key: "incident_ca", label: "Incident & Corrective Action", icon: "🔧", trackerKeys: ["incidents", "corrective-actions", "nc-management", "disciplinary-actions"] },
  { key: "emergency_preparedness", label: "Emergency Preparedness", icon: "🚨", trackerKeys: ["emergency-drills"] },
  { key: "communication", label: "Communication", icon: "📰", trackerKeys: ["safety-bulletins"] },
  { key: "environmental", label: "Environmental", icon: "🌱", trackerKeys: ["environmental-performance"] },
];

function avgIgnoreNull(vals: (number | null)[]): number | null {
  const v = vals.filter((x): x is number => x !== null);
  return v.length ? Math.round(v.reduce((a, b) => a + b, 0) / v.length) : null;
}

function scoreFromRows(rows: Row[], kind: "status" | "metric" | "presence"): number | null {
  if (kind === "status") {
    if (!rows.length) return null;
    const closed = rows.filter((r) => CLOSED_LIKE.has(String(r.v))).length;
    return Math.round((100 * closed) / rows.length);
  }
  if (kind === "metric") {
    const vals = rows.map((r) => Number(r.v)).filter((v) => !isNaN(v));
    if (!vals.length) return null;
    return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
  }
  return rows.length > 0 ? 100 : null;
}

async function trackerYearStats(database: ReturnType<typeof db>, t: TrackerDef, year: number, department: string, deptFilter: boolean) {
  const dateField = dateFieldOf(t);
  const statusField = t.fields.find((f) => f.role === "status");
  const metricField = t.fields.find((f) => f.role === "metric_pct");
  const kind: "status" | "metric" | "presence" = statusField ? "status" : metricField ? "metric" : "presence";
  const col = kind === "status" ? statusField!.name : kind === "metric" ? metricField!.name : null;

  const selectCols = col ? `department, "${col}" AS v, EXTRACT(MONTH FROM "${dateField}")::int AS month` : `department, EXTRACT(MONTH FROM "${dateField}")::int AS month`;
  const params: unknown[] = [year];
  let where = `EXTRACT(YEAR FROM "${dateField}") = $1`;
  if (deptFilter) { params.push(department); where += ` AND department = $${params.length}`; }

  const rows = (await database.sql.unsafe(`SELECT ${selectCols} FROM "${t.table}" WHERE ${where}`, params)) as Row[];

  const monthly: (number | null)[] = [];
  for (let m = 1; m <= 12; m++) monthly.push(scoreFromRows(rows.filter((r) => r.month === m), kind));

  const byDept = new Map<string, Row[]>();
  for (const r of rows) {
    const d = String(r.department);
    if (!byDept.has(d)) byDept.set(d, []);
    byDept.get(d)!.push(r);
  }
  const deptScores: Record<string, number | null> = {};
  for (const [d, rs] of byDept) deptScores[d] = scoreFromRows(rs, kind);

  return { overall: scoreFromRows(rows, kind), monthly, deptScores };
}

export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;
  const year = Number(sp.get("year")) || new Date().getFullYear();
  const department = sp.get("department") || "All";
  const deptFilter = department !== "All";
  const database = db();

  const results = [];
  for (const el of ELEMENTS) {
    const members = el.trackerKeys.map((k) => TRACKERS.find((t) => t.key === k)!).filter(Boolean);
    const memberStats = await Promise.all(members.map((t) => trackerYearStats(database, t, year, department, deptFilter)));

    const overall = avgIgnoreNull(memberStats.map((s) => s.overall));
    const monthly: (number | null)[] = [];
    for (let m = 0; m < 12; m++) monthly.push(avgIgnoreNull(memberStats.map((s) => s.monthly[m])));

    const allDepts = Array.from(new Set(memberStats.flatMap((s) => Object.keys(s.deptScores))));
    const deptScores: Record<string, number | null> = {};
    for (const d of allDepts) deptScores[d] = avgIgnoreNull(memberStats.map((s) => (d in s.deptScores ? s.deptScores[d] : null)));

    results.push({ key: el.key, label: el.label, icon: el.icon, memberCount: members.length, overall, monthly, deptScores });
  }

  return Response.json({ year, department, elements: results });
}
