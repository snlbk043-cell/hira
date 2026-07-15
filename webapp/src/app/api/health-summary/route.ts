import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { TRACKERS } from "@/lib/trackers";
import { CLOSED_LIKE } from "@/lib/constants";

export const dynamic = "force-dynamic";

type Row = Record<string, unknown>;

/** RAG health score (0=Red, 1=Amber, 2=Green) for every one of the 25 trackers,
 * matching the Excel Leadership Review's System Health radar. Uses whichever
 * signal each tracker actually has: closed/completed % for trackers with a
 * status field, average of the metric_pct field otherwise, or simple record
 * presence as a last resort - same role-driven approach as computeSnapshot(). */
export async function GET(req: NextRequest) {
  const department = req.nextUrl.searchParams.get("department") || "All";
  const deptFilter = department !== "All";
  const database = db();

  const results: { label: string; icon: string; score: number; detail: string }[] = [];

  for (const t of TRACKERS) {
    const statusField = t.fields.find((f) => f.role === "status");
    const metricField = t.fields.find((f) => f.role === "metric_pct");
    const where = deptFilter ? `WHERE department = $1` : "";
    const params = deptFilter ? [department] : [];

    if (statusField) {
      const rows = (await database.sql.unsafe(
        `SELECT "${statusField.name}" AS v FROM "${t.table}" ${where}`, params
      )) as Row[];
      const total = rows.length;
      const closed = rows.filter((r) => CLOSED_LIKE.has(String(r.v))).length;
      const pct = total ? (100 * closed) / total : 0;
      results.push({ label: t.label, icon: t.icon, score: pct >= 85 ? 2 : pct >= 60 ? 1 : total ? 0 : 1, detail: total ? `${Math.round(pct)}% closed` : "no data" });
    } else if (metricField) {
      const rows = (await database.sql.unsafe(
        `SELECT "${metricField.name}" AS v FROM "${t.table}" ${where}`, params
      )) as Row[];
      const vals = rows.map((r) => Number(r.v)).filter((v) => !isNaN(v));
      const avg = vals.length ? vals.reduce((a, b) => a + b, 0) / vals.length : 0;
      results.push({ label: t.label, icon: t.icon, score: avg >= 85 ? 2 : avg >= 60 ? 1 : vals.length ? 0 : 1, detail: vals.length ? `${Math.round(avg)}% avg` : "no data" });
    } else {
      const rows = (await database.sql.unsafe(
        `SELECT COUNT(*)::int AS n FROM "${t.table}" ${where}`, params
      )) as Row[];
      const n = Number(rows[0]?.n || 0);
      results.push({ label: t.label, icon: t.icon, score: n > 0 ? 2 : 1, detail: `${n} records` });
    }
  }

  return Response.json({ department, results });
}
