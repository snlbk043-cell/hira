import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { RECORDABLE_CLASSIFICATIONS } from "@/lib/constants";

export const dynamic = "force-dynamic";

type Row = Record<string, unknown>;

/** Builds a WHERE clause + params for year (always) + optional month + optional
 * department, matching Excel's SelPeriod/SelDept filter pair. */
function buildFilter(dateCol: string, year: number, month: number, department: string, deptFilter: boolean) {
  const clauses = [`EXTRACT(YEAR FROM ${dateCol}) = $1`];
  const params: unknown[] = [year];
  if (month) { params.push(month); clauses.push(`EXTRACT(MONTH FROM ${dateCol}) = $${params.length}`); }
  if (deptFilter) { params.push(department); clauses.push(`department = $${params.length}`); }
  return { where: clauses.join(" AND "), params };
}

export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;
  const year = Number(sp.get("year")) || new Date().getFullYear();
  const department = sp.get("department") || "All";
  const month = Number(sp.get("month")) || 0; // 0 = All months
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
  const totalManhours = (month ? manhoursByMonth[month - 1] : manhoursByMonth.reduce((a, b) => a + b, 0)) || 1;

  // ---- incidents ----
  const incF = buildFilter("incident_date", year, month, department, deptFilter);
  const incidentRows = (await database.sql.unsafe(
    `SELECT classification, department, body_part, risk_rating, lost_days, root_cause,
            EXTRACT(MONTH FROM incident_date)::int AS month
     FROM incidents WHERE ${incF.where}`,
    incF.params
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
    const f = buildFilter(dateCol, year, month, department, deptFilter);
    const rows = (await database.sql.unsafe(
      `SELECT status, EXTRACT(MONTH FROM ${dateCol})::int AS month FROM ${table} WHERE ${f.where}`,
      f.params
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

  const inspF = buildFilter("inspection_date", year, month, department, deptFilter);
  const inspRows = (await database.sql.unsafe(
    `SELECT inspection_type, status, EXTRACT(MONTH FROM inspection_date)::int AS month FROM inspections WHERE ${inspF.where}`,
    inspF.params
  )) as Row[];
  const monthlyInspections = new Array(12).fill(0);
  for (const r of inspRows) monthlyInspections[(r.month as number) - 1]++;

  const ptwF = buildFilter("audit_date", year, month, department, deptFilter);
  const ptwRows = (await database.sql.unsafe(
    `SELECT verdict, compliance_pct FROM ptw_audits WHERE ${ptwF.where}`, ptwF.params
  )) as Row[];
  const ptwTotal = ptwRows.length;
  const ptwCompliant = ptwRows.filter((r) => r.verdict === "Compliant").length;
  const ptwPct = ptwTotal ? (100 * ptwCompliant) / ptwTotal : 0;

  const jsaF = buildFilter("assessment_date", year, month, department, deptFilter);
  const jsaRows = (await database.sql.unsafe(
    `SELECT approval_status FROM risk_assessments WHERE ${jsaF.where}`, jsaF.params
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
  async function overdueCount(table: string) {
    const rows = (await database.sql.unsafe(
      `SELECT COUNT(*)::int AS n FROM ${table} WHERE status = 'Overdue' ${deptFilter ? "AND department = $1" : ""}`,
      deptFilter ? [department] : []
    )) as Row[];
    return Number(rows[0]?.n || 0);
  }
  const backlog = {
    corrective_actions: await overdueCount("corrective_actions"),
    hse_observations: await overdueCount("hse_observations"),
    inspections: await overdueCount("inspections"),
    safety_walkthroughs: await overdueCount("safety_walkthroughs"),
  };

  // ---- backlog ageing (system-wide, across the same 4 registers) ----
  async function agingBuckets(table: string) {
    const rows = (await database.sql.unsafe(
      `SELECT due_date FROM ${table} WHERE status = 'Overdue' ${deptFilter ? "AND department = $1" : ""}`,
      deptFilter ? [department] : []
    )) as Row[];
    const buckets = { "0-7": 0, "8-15": 0, "16-30": 0, "30+": 0 };
    const now = Date.now();
    for (const r of rows) {
      if (!r.due_date) continue;
      const days = Math.floor((now - new Date(String(r.due_date)).getTime()) / 86400000);
      if (days <= 7) buckets["0-7"]++;
      else if (days <= 15) buckets["8-15"]++;
      else if (days <= 30) buckets["16-30"]++;
      else buckets["30+"]++;
    }
    return buckets;
  }
  const agingTables = ["corrective_actions", "hse_observations", "inspections", "safety_walkthroughs"];
  const backlogAging = { "0-7": 0, "8-15": 0, "16-30": 0, "30+": 0 };
  for (const t of agingTables) {
    const b = await agingBuckets(t);
    for (const k of Object.keys(backlogAging) as (keyof typeof backlogAging)[]) backlogAging[k] += b[k];
  }

  // ---- Top-10 Pareto lists ----
  async function top10(table: string, dateCol: string, field: string) {
    const f = buildFilter(dateCol, year, month, department, deptFilter);
    const rows = (await database.sql.unsafe(
      `SELECT "${field}" AS v FROM ${table} WHERE ${f.where}`, f.params
    )) as Row[];
    const counts: Record<string, number> = {};
    for (const r of rows) {
      if (!r.v) continue;
      const v = String(r.v);
      counts[v] = (counts[v] || 0) + 1;
    }
    return Object.entries(counts).sort((a, b) => b[1] - a[1]).slice(0, 10).map(([label, value]) => ({ label, value }));
  }
  const top10UnsafeActs = await top10("unsafe_acts", "report_date", "description");
  const top10UnsafeConditions = await top10("unsafe_conditions", "report_date", "description");
  const top10Areas = await top10("incidents", "incident_date", "area");

  // ---- cost impact (real Settings-configured rates, no fabricated numbers) ----
  const swaF = buildFilter("event_date", year, month, department, deptFilter);
  const swaRows = (await database.sql.unsafe(
    `SELECT downtime_min FROM stop_work_authority WHERE ${swaF.where}`, swaF.params
  )) as Row[];
  const downtimeTotal = swaRows.reduce((a, r) => a + (Number(r.downtime_min) || 0), 0);
  const costImpact = {
    lostDayCost: Math.round(lostDaysTotal * (settings.cost_per_lost_day || 8000)),
    downtimeCost: Math.round(downtimeTotal * (settings.cost_per_downtime_min || 150)),
    downtimeMinTotal: downtimeTotal,
  };

  // ---- prior period (for Top Movers) - same key metrics, one period back ----
  async function priorPeriodMetrics() {
    const pYear = month ? year : year - 1;
    const pMonth = month ? (month === 1 ? 12 : month - 1) : 0;
    const pYearForJan = month === 1 ? year - 1 : year;
    const py = month === 1 ? pYearForJan : pYear;

    const pIncF = buildFilter("incident_date", py, pMonth, department, deptFilter);
    const pInc = (await database.sql.unsafe(
      `SELECT classification FROM incidents WHERE ${pIncF.where}`, pIncF.params
    )) as Row[];
    const pRecordable = pInc.filter((r) => RECORDABLE_CLASSIFICATIONS.includes(String(r.classification))).length;
    const pLtiFatal = pInc.filter((r) => r.classification === "Lost Time Injury" || r.classification === "Fatality").length;

    async function pStatusPct(table: string, dateCol: string) {
      const f = buildFilter(dateCol, py, pMonth, department, deptFilter);
      const rows = (await database.sql.unsafe(
        `SELECT status FROM ${table} WHERE ${f.where}`, f.params
      )) as Row[];
      const total = rows.length;
      const closed = rows.filter((r) => r.status === "Completed").length;
      return total ? (100 * closed) / total : 0;
    }
    const pTraining = await pStatusPct("training", "training_date");
    const pObs = await pStatusPct("hse_observations", "obs_date");
    const pCa = await pStatusPct("corrective_actions", "date_raised");

    return {
      totalIncidents: pInc.length,
      recordableTotal: pRecordable,
      ltiFatalTotal: pLtiFatal,
      trainingPct: round1(pTraining),
      obsPct: round1(pObs),
      caPct: round1(pCa),
    };
  }
  const prior = await priorPeriodMetrics();

  return Response.json({
    year,
    department,
    month,
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
    backlogAging,
    top10UnsafeActs,
    top10UnsafeConditions,
    top10Areas,
    costImpact,
    prior,
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
