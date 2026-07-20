import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { TrackerField } from "@/lib/trackers";

export const dynamic = "force-dynamic";

type CustomTrackerRow = { id: number; key: string; label: string; icon: string; description: string; fields: TrackerField[] | string; created_at: string };

function parseFields(fields: TrackerField[] | string): TrackerField[] {
  return typeof fields === "string" ? JSON.parse(fields) : fields;
}

export async function GET() {
  const rows = (await db().sql`SELECT id, key, label, icon, description, fields, created_at FROM custom_trackers ORDER BY created_at ASC`) as CustomTrackerRow[];
  return Response.json(rows.map((r) => ({ ...r, fields: parseFields(r.fields) })));
}

function slugify(label: string): string {
  return "custom-" + label.toLowerCase().trim().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "").slice(0, 40);
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { label, icon, description, fields } = body as { label: string; icon: string; description: string; fields: TrackerField[] };

  if (!label || !Array.isArray(fields) || fields.length === 0) {
    return Response.json({ error: "label and at least one field are required" }, { status: 400 });
  }
  if (!fields.some((f) => f.role === "date")) {
    return Response.json({ error: "At least one field must be marked as the Date field" }, { status: 400 });
  }

  const database = db();
  let key = slugify(label);
  const existing = (await database.sql`SELECT 1 FROM custom_trackers WHERE key = ${key}`) as unknown[];
  if (existing.length > 0) key = `${key}-${Date.now().toString(36)}`;

  const rows = await database.sql`
    INSERT INTO custom_trackers (key, label, icon, description, fields)
    VALUES (${key}, ${label}, ${icon || "📁"}, ${description || ""}, ${JSON.stringify(fields)})
    RETURNING id, key, label, icon, description, fields, created_at`;

  return Response.json({ ...rows[0], fields }, { status: 201 });
}
