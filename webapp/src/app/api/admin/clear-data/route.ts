import { db } from "@/lib/db";
import { TRACKERS } from "@/lib/trackers";

export const dynamic = "force-dynamic";

/** Wipes every row from all 25 tracker tables (demo/seed data cleanup). Does NOT
 * touch settings or manhours - those are configuration, not register entries.
 * Table names come only from the fixed TRACKERS config, never user input. */
export async function POST() {
  const database = db();
  const results: Record<string, string> = {};
  for (const t of TRACKERS) {
    await database.sql.unsafe(`DELETE FROM "${t.table}"`, []);
    results[t.table] = "cleared";
  }
  return Response.json({ ok: true, results });
}
