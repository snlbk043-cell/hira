import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { TrackerField } from "@/lib/trackers";

export const dynamic = "force-dynamic";

type Row = Record<string, unknown>;

async function getFields(database: ReturnType<typeof db>, key: string): Promise<TrackerField[] | null> {
  const rows = (await database.sql`SELECT fields FROM custom_trackers WHERE key = ${key}`) as { fields: TrackerField[] | string }[];
  if (rows.length === 0) return null;
  const f = rows[0].fields;
  return typeof f === "string" ? JSON.parse(f) : f;
}

export async function GET(req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  const database = db();
  const fields = await getFields(database, key);
  if (!fields) return Response.json({ error: "unknown tracker" }, { status: 404 });

  const sp = req.nextUrl.searchParams;
  const from = sp.get("from");
  const to = sp.get("to");
  const department = sp.get("department");
  const limit = Math.min(Number(sp.get("limit")) || 500, 5000);

  const dateFieldName = fields.find((f) => f.role === "date")?.name;
  const rows = (await database.sql`
    SELECT id, data FROM custom_tracker_records WHERE tracker_key = ${key} ORDER BY id DESC LIMIT ${limit}`) as { id: number; data: Row | string }[];

  const parsed = rows.map((r) => ({ id: r.id, ...(typeof r.data === "string" ? JSON.parse(r.data) : r.data) }));

  const filtered = parsed.filter((r) => {
    if (dateFieldName && (from || to)) {
      const v = r[dateFieldName];
      if (!v) return false;
      const s = String(v).slice(0, 10);
      if (from && s < from) return false;
      if (to && s > to) return false;
    }
    if (department && department !== "All" && r.department !== department) return false;
    return true;
  });

  return Response.json(filtered);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  const database = db();
  const fields = await getFields(database, key);
  if (!fields) return Response.json({ error: "unknown tracker" }, { status: 404 });

  const body = (await req.json()) as Row;
  for (const f of fields) {
    if (f.required && (body[f.name] === undefined || body[f.name] === "")) {
      return Response.json({ error: `${f.name} is required` }, { status: 400 });
    }
  }

  const data: Row = {};
  for (const f of fields) {
    if (body[f.name] !== undefined && body[f.name] !== "") data[f.name] = body[f.name];
  }

  const rows = await database.sql`
    INSERT INTO custom_tracker_records (tracker_key, data) VALUES (${key}, ${JSON.stringify(data)})
    RETURNING id, data`;
  const r = rows[0] as { id: number; data: Row | string };
  return Response.json({ id: r.id, ...(typeof r.data === "string" ? JSON.parse(r.data) : r.data) }, { status: 201 });
}

/** Clears every record for this custom tracker (keeps the tracker definition itself). */
export async function DELETE(_req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  await db().sql`DELETE FROM custom_tracker_records WHERE tracker_key = ${key}`;
  return new Response(null, { status: 204 });
}
