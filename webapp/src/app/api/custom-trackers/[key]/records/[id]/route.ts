import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { TrackerField } from "@/lib/trackers";

export const dynamic = "force-dynamic";

type Row = Record<string, unknown>;

export async function PATCH(req: NextRequest, ctx: { params: Promise<{ key: string; id: string }> }) {
  const { key, id } = await ctx.params;
  const database = db();
  const trackerRows = (await database.sql`SELECT fields FROM custom_trackers WHERE key = ${key}`) as { fields: TrackerField[] | string }[];
  if (trackerRows.length === 0) return Response.json({ error: "unknown tracker" }, { status: 404 });
  const fields: TrackerField[] = typeof trackerRows[0].fields === "string" ? JSON.parse(trackerRows[0].fields as string) : (trackerRows[0].fields as TrackerField[]);

  const existingRows = (await database.sql`SELECT data FROM custom_tracker_records WHERE id = ${Number(id)} AND tracker_key = ${key}`) as { data: Row | string }[];
  if (existingRows.length === 0) return Response.json({ error: "not found" }, { status: 404 });
  const existing: Row = typeof existingRows[0].data === "string" ? JSON.parse(existingRows[0].data as string) : existingRows[0].data;

  const body = (await req.json()) as Row;
  const merged: Row = { ...existing };
  for (const f of fields) {
    if (body[f.name] !== undefined) merged[f.name] = body[f.name];
  }

  const rows = await database.sql`
    UPDATE custom_tracker_records SET data = ${JSON.stringify(merged)}, updated_at = NOW()
    WHERE id = ${Number(id)} AND tracker_key = ${key} RETURNING id, data`;
  const r = rows[0] as { id: number; data: Row | string };
  return Response.json({ id: r.id, ...(typeof r.data === "string" ? JSON.parse(r.data) : r.data) });
}

export async function DELETE(_req: NextRequest, ctx: { params: Promise<{ key: string; id: string }> }) {
  const { key, id } = await ctx.params;
  await db().sql`DELETE FROM custom_tracker_records WHERE id = ${Number(id)} AND tracker_key = ${key}`;
  return new Response(null, { status: 204 });
}
