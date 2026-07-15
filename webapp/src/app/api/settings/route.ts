import { NextRequest } from "next/server";
import { db } from "@/lib/db";

export async function GET() {
  const rows = await db().sql`SELECT key, value, note FROM settings ORDER BY key`;
  const map: Record<string, string> = {};
  for (const r of rows as { key: string; value: string }[]) map[r.key] = r.value;
  return Response.json(map);
}

export async function POST(req: NextRequest) {
  const updates = (await req.json()) as Record<string, string>;
  const database = db();
  for (const [key, value] of Object.entries(updates)) {
    await database.sql`
      INSERT INTO settings (key, value) VALUES (${key}, ${String(value)})
      ON CONFLICT (key) DO UPDATE SET value = EXCLUDED.value`;
  }
  return Response.json({ ok: true });
}
