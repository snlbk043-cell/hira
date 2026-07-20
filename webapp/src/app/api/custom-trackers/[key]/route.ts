import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { TrackerField } from "@/lib/trackers";

export const dynamic = "force-dynamic";

type CustomTrackerRow = { id: number; key: string; label: string; icon: string; description: string; fields: TrackerField[] | string; created_at: string };

function parseFields(fields: TrackerField[] | string): TrackerField[] {
  return typeof fields === "string" ? JSON.parse(fields) : fields;
}

export async function GET(_req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  const rows = (await db().sql`SELECT id, key, label, icon, description, fields, created_at FROM custom_trackers WHERE key = ${key}`) as CustomTrackerRow[];
  if (rows.length === 0) return Response.json({ error: "not found" }, { status: 404 });
  return Response.json({ ...rows[0], fields: parseFields(rows[0].fields) });
}

/** Deletes the tracker definition + all of its records (ON DELETE CASCADE). */
export async function DELETE(_req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  await db().sql`DELETE FROM custom_trackers WHERE key = ${key}`;
  return new Response(null, { status: 204 });
}
