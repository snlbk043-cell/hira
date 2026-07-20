import { NextRequest } from "next/server";
import { db } from "@/lib/db";

export const dynamic = "force-dynamic";

const FREQUENCY_MONTHS: Record<string, number> = {
  Monthly: 1,
  Quarterly: 3,
  "Half-Yearly": 6,
  Annually: 12,
};

function addMonths(dateStr: string, months: number): string {
  const d = new Date(dateStr + "T00:00:00Z");
  d.setUTCMonth(d.getUTCMonth() + months);
  return d.toISOString().slice(0, 10);
}

type ScheduleRow = {
  id: number;
  tracker_key: string;
  title: string;
  location: string | null;
  frequency: string;
  due_date: string;
  status: string;
  completed_date: string | null;
  notes: string | null;
};

/** Toggles Pending <-> Done. When marking Done on a recurring item, also
 * creates the next occurrence (due_date advanced by the frequency) so the
 * calendar keeps rolling forward automatically. */
export async function PATCH(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const body = await req.json().catch(() => ({}));
  const database = db();

  const rows = (await database.sql`SELECT * FROM compliance_schedule WHERE id = ${Number(id)}`) as ScheduleRow[];
  if (rows.length === 0) return Response.json({ error: "not found" }, { status: 404 });
  const item = rows[0];

  const nextStatus = body.status ?? (item.status === "Done" ? "Pending" : "Done");
  const completedDate = nextStatus === "Done" ? new Date().toISOString().slice(0, 10) : null;

  const updated = await database.sql`
    UPDATE compliance_schedule SET status = ${nextStatus}, completed_date = ${completedDate}
    WHERE id = ${Number(id)} RETURNING id, tracker_key, title, location, frequency, due_date, status, completed_date, notes`;

  let created: ScheduleRow | null = null;
  const monthsToAdd = FREQUENCY_MONTHS[item.frequency];
  if (nextStatus === "Done" && monthsToAdd) {
    const nextDue = addMonths(item.due_date.slice(0, 10), monthsToAdd);
    const createdRows = await database.sql`
      INSERT INTO compliance_schedule (tracker_key, title, location, frequency, due_date, notes)
      VALUES (${item.tracker_key}, ${item.title}, ${item.location}, ${item.frequency}, ${nextDue}, ${item.notes})
      RETURNING id, tracker_key, title, location, frequency, due_date, status, completed_date, notes`;
    created = createdRows[0] as ScheduleRow;
  }

  return Response.json({ updated: updated[0], created });
}

export async function DELETE(_req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  await db().sql`DELETE FROM compliance_schedule WHERE id = ${Number(id)}`;
  return new Response(null, { status: 204 });
}
