import { db } from "@/lib/db";
import seedData from "@/data/seed/registers.json";

export const dynamic = "force-dynamic";

type SeedRow = Record<string, string | number | null>;

/**
 * One-time import of the real register data from the original Excel system.
 * Idempotent: skips any table that already has rows, so calling this more
 * than once (or on every deploy) never duplicates data.
 */
export async function POST() {
  const database = db();
  const results: Record<string, string> = {};

  const tables: { key: keyof typeof seedData; table: string; columns: string[] }[] = [
    { key: "incidents", table: "incidents", columns: ["incident_date","department","area","classification","body_part","risk_rating","lost_days","root_cause","description","status","closure_date"] },
    { key: "training", table: "training", columns: ["training_date","department","course_name","training_type","status","attendance_pct","assessment_result"] },
    { key: "observations", table: "hse_observations", columns: ["obs_date","department","observation_type","risk_level","status","due_date","description"] },
    { key: "inspections", table: "inspections", columns: ["inspection_date","department","inspection_type","status","critical_findings","non_conformances","due_date"] },
    { key: "walkthroughs", table: "safety_walkthroughs", columns: ["walk_date","department","area","owner","status","completion_pct","critical_findings","due_date"] },
    { key: "corrective_actions", table: "corrective_actions", columns: ["date_raised","department","source","priority","description","status","due_date","completion_date","assigned_to"] },
    { key: "ptw_audits", table: "ptw_audits", columns: ["audit_date","department","permit_type","auditor","permits_reviewed","deviations_found","compliance_pct","verdict"] },
    { key: "risk_assessments", table: "risk_assessments", columns: ["assessment_date","department","task","risk_level","hazards_identified","approval_status","controls_implemented"] },
  ];

  for (const { key, table, columns } of tables) {
    const countRows = (await database.sql.unsafe(`SELECT COUNT(*)::int AS n FROM "${table}"`, [])) as { n: number }[];
    if (countRows[0].n > 0) {
      results[table] = `skipped (already has ${countRows[0].n} rows)`;
      continue;
    }
    const rows = seedData[key] as SeedRow[];
    let inserted = 0;
    for (const row of rows) {
      const present = columns.filter((c) => row[c] !== undefined);
      const colList = present.map((c) => `"${c}"`).join(", ");
      const placeholders = present.map((_, i) => `$${i + 1}`).join(", ");
      const values = present.map((c) => row[c] ?? null);
      await database.sql.unsafe(`INSERT INTO "${table}" (${colList}) VALUES (${placeholders})`, values);
      inserted++;
    }
    results[table] = `inserted ${inserted} rows`;
  }

  // seed man-hours for the current year at a plausible plant-wide rate, if empty
  const year = new Date().getFullYear();
  const mhCount = (await database.sql`SELECT COUNT(*)::int AS n FROM manhours WHERE year = ${year}`) as { n: number }[];
  if (mhCount[0].n === 0) {
    for (let m = 1; m <= 12; m++) {
      await database.sql`INSERT INTO manhours (year, month, department, hours) VALUES (${year}, ${m}, 'All', ${83333})`;
    }
    results.manhours = `seeded 12 months for ${year}`;
  } else {
    results.manhours = "skipped (already present)";
  }

  return Response.json({ ok: true, results });
}
