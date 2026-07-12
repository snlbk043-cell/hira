import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { RECORDABLE_CLASSIFICATIONS } from "@/lib/constants";

export const dynamic = "force-dynamic";

type Row = Record<string, unknown>;

export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;
  const year = Number(sp.get("year")) || new Date().getFullYear();
  const department = sp.get("department") || "All";
  const database = db();
  const deptFilter = department !== "All";

  // ---- settings / targets ----
  const settingsRows = (await database.sql`SELECT key, value FROM settings`) as Row[];
  const settings: Record<string, number> = {};
  for (const r of settingsRows) settings[r.key as string] = Number(r.value);

  // ---- man-hours (plant-wide) ----
  const mhRows = (await database.sql`
    SELECT month, hours FROM manhours WHERE year = ${year} AND department = 'All' ORDER BY month
  `) as Row[];
  const manhoursByMonth = new Array(12).fill(0);
  for (const r of mhRows) manhoursByMonth[(r.month as number) - 1] = Number(r.hours);
  const totalManhours = manhoursByMonth.reduce((a, b) => a + b, 0) || 1;

  // ---- incidents ----
  const incidentRows = (await database.sql.unsafe(
    `SELECT classification, department, body_part, risk_rating, lost_days, root_cause,
            EXTRACT(MONTH FROM incident_date)::int AS month
     FROM incidents
     WHERE EXTRACT(YEAR FROM incident_date) = $1 ${deptFilter ? "AND department = $2" : ""}`,
    deptFilter ? [year, department] : [year]
  )) as Row[];

  const classificationCounts: Record<string, number> = {};
  const monthlyIncidents = new Array(12).fill(0);
  const monthlyRecordable = new Array(12).fill(0);
  const monthlyLtiFatal = new Array(12).fill(0);
  const rootCauseCounts: Record<string, number> = {};
  const bodyPartCounts: Record<string, number> = {};
  const deptRecordable: Record<string, number> = {};
  const deptNearMiss: Record<string, number> = {};
  const riskRatingByDept: Record<string, Record<string, number>> = {};
  let lostDaysTotal = 0;

  for (const r of incidentRows) {
    const cls = String(r.classification);
    classificationCounts[cls] = (classificationCounts[cls] || 0) + 1;
    const m = (r.month as number) - 1;
    monthlyIncidents[m]++;
    const recordable = RECORDABLE_CLASSIFICATIONS.includes(cls);
    if (recordable) monthlyRecordable[m]++;
    if (cls === "Lost Time Injury" || cls === "Fatality") monthlyLtiFatal[m]++;
    lostDaysTotal += Number(r.lost_days) || 0;
    if (r.root_cause) rootCauseCounts[String(r.root_cause)] = (rootCauseCounts[String(r.root_cause)] || 0) + 1;
    if (r.body_part) bodyPartCounts[String(r.body_part)] = (bodyPartCounts[String(r.body_part)] || 0) + 1;
    const dept = String(r.department);
    if (recordable) deptRecordable[dept] = (deptRecordable[dept] || 0) + 1;
    if (cls === "Near Miss") deptNearMiss[dept] = (deptNearMiss[dept] || 0) + 1;
    if (r.risk_rating) {
      const lvl = String(r.risk_rating);
      riskRatingByDept[lvl] = riskRatingByDept[lvl] || {};
      riskRatingByDept[lvl][dept] = (riskRatingByDept[lvl][dept] || 0) + 1;
    }
  }

  const recordableTotal = monthlyRecordable.reduce((a, b) => a + b, 0);
  const ltiFatalTotal = monthlyLtiFatal.reduce((a, b) => a + b, 0);
  const TRIR = (recordableTotal * (settings.trir_multiplier || 200000)) / totalManhours;
  const LTIFR = (ltiFatalTotal * (settings.ltifr_multiplier || 1000000)) / totalManhours;
  const trirMonthly = monthlyRecordable.map((c, i) =>
    manhoursByMonth[i] ? (c * (settings.trir_multiplier || 200000)) / manhoursByMonth[i] : 0
  );
  const ltifrMonthly = monthlyLtiFatal.map((c, i) =>
    manhoursByMonth[i] ? (c * (settings.ltifr_multiplier || 1000000)) / manhoursByMonth[i] : 0
  );

  // ---- helper for status-based % + monthly count across the other registers ----
  async function statusSummary(table: string, dateCol: string, closedValues: string[]) {
    const rows = (await database.sql.unsafe(
      `SELECT status, EXTRACT(MONTH FROM ${dateCol})::int AS month
       FROM ${table}
       WHERE EXTRACT(YEAR FROM ${dateCol}) = $1 ${deptFilter ? "AND department = $2" : ""}`,
      deptFilter ? [year, department] : [year]
    )) as Row[];
    const monthly = new Array(12).fill(0);
    const monthlyClosed = new Array(12).fill(0);
    const statusCounts: Record<string, number> = {};
    for (const r of rows) {
      const m = (r.month as number) - 1;
      monthly[m]++;
      const st = String(r.status);
      statusCounts[st] = (statusCounts[st] || 0) + 1;
      if (closedValues.includes(st)) monthlyClosed[m]++;
    }
    const total = rows.length;
    const closed = Object.entries(statusCounts)
      .filter(([k]) => closedValues.includes(k))
      .reduce((a, [, v]) => a + v, 0);
    return { total, closed, pct: total ? (100 * closed) / total : 0, monthly, monthlyClosed, statusCounts };
  }

  const training = await statusSummary("training", "training_date", ["Completed"]);
  const obs = await statusSummary("hse_observations", "obs_date", ["Completed"]);
  const ca = await statusSummary("corrective_actions", "date_raised", ["Completed"]);
  const walk = await statusSummary("safety_walkthroughs", "walk_date", ["Completed"]);

  const inspRows = (await database.sql.unsafe(
    `SELECT inspection_type, status, EXTRACT(MONTH FROM inspection_date)::int AS month
     FROM inspections WHERE EXTRACT(YEAR FROM inspection_date) = $1 ${deptFilter ? "AND department = $2" : ""}`,
    deptFilter ? [year, department] : [year]
  )) as Row[];
  const monthlyInspections = new Array(12).fill(0);
  for (const r of inspRows) monthlyInspections[(r.month as number) - 1]++;

  const ptwRows = (await database.sql.unsafe(
    `SELECT verdict, compliance_pct FROM ptw_audits WHERE EXTRACT(YEAR FROM audit_date) = $1 ${deptFilter ? "AND department = $2" : ""}`,
    deptFilter ? [year, department] : [year]
  )) as Row[];
  const ptwTotal = ptwRows.length;
  const ptwCompliant = ptwRows.filter((r) => r.verdict === "Compliant").length;
  const ptwPct = ptwTotal ? (100 * ptwCompliant) / ptwTotal : 0;

  const jsaRows = (await database.sql.unsafe(
    `SELECT approval_status FROM risk_assessments WHERE EXTRACT(YEAR FROM assessment_date) = $1 ${deptFilter ? "AND department = $2" : ""}`,
    deptFilter ? [year, department] : [year]
  )) as Row[];
  const jsaTotal = jsaRows.length;
  const jsaApproved = jsaRows.filter((r) => r.approval_status === "Approved").length;
  const jsaPct = jsaTotal ? (100 * jsaApproved) / jsaTotal : 0;

  // ---- leading vs lagging monthly ----
  const leadingMonthly = new Array(12)
    .fill(0)
    .map((_, i) => training.monthly[i] + obs.monthly[i] + monthlyInspections[i] + walk.monthly[i]);
  const laggingMonthly = monthlyIncidents;

  // ---- department safety score ----
  const allDepts = Array.from(new Set([...Object.keys(deptRecordable), ...Object.keys(deptNearMiss)]));
  const deptScore: Record<string, number> = {};
  for (const d of allDepts) {
    const rec = deptRecordable[d] || 0;
    const nm = deptNearMiss[d] || 0;
    deptScore[d] = Math.max(45, Math.min(100, Math.round(100 - rec * 8 - nm * 1.5)));
  }

  // ---- open/overdue backlog across registers with a due date ----
  async function overdueCount(table: string, dateCol: string) {
    const rows = (await database.sql.unsafe(
      `SELECT COUNT(*)::int AS n FROM ${table} WHERE status = 'Overdue' ${deptFilter ? "AND department = $1" : ""}`,
      deptFilter ? [department] : []
    )) as Row[];
    return Number(rows[0]?.n || 0);
  }
  const backlog = {
    corrective_actions: await overdueCount("corrective_actions", "date_raised"),
    hse_observations: await overdueCount("hse_observations", "obs_date"),
    inspections: await overdueCount("inspections", "inspection_date"),
    safety_walkthroughs: await overdueCount("safety_walkthroughs", "walk_date"),
  };

  return Response.json({
    year,
    department,
    TRIR: round2(TRIR),
    LTIFR: round2(LTIFR),
    trirMonthly: trirMonthly.map(round2),
    ltifrMonthly: ltifrMonthly.map(round2),
    totalIncidents: incidentRows.length,
    recordableTotal,
    lostDaysTotal,
    classificationCounts,
    monthlyIncidents,
    rootCauseCounts,
    bodyPartCounts,
    deptScore,
    riskRatingByDept,
    training: { pct: round1(training.pct), total: training.total, statusCounts: training.statusCounts },
    obs: { pct: round1(obs.pct), total: obs.total, statusCounts: obs.statusCounts },
    ca: { pct: round1(ca.pct), total: ca.total, statusCounts: ca.statusCounts },
    walk: { pct: round1(walk.pct), total: walk.total, statusCounts: walk.statusCounts },
    ptw: { pct: round1(ptwPct), total: ptwTotal },
    jsa: { pct: round1(jsaPct), total: jsaTotal },
    leadingMonthly,
    laggingMonthly,
    backlog,
    settings,
    manhoursByMonth,
  });
}

function round2(n: number) {
  return Math.round(n * 100) / 100;
}
function round1(n: number) {
  return Math.round(n * 10) / 10;
}
