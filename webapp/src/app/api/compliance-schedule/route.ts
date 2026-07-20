import { NextRequest } from "next/server";
import { db } from "@/lib/db";

export const dynamic = "force-dynamic";

export async function GET(req: NextRequest) {
  const trackerKey = req.nextUrl.searchParams.get("trackerKey");
  if (!trackerKey) return Response.json({ error: "trackerKey is required" }, { status: 400 });

  const rows = await db().sql`
    SELECT id, tracker_key, title, location, frequency, due_date, status, completed_date, notes
    FROM compliance_schedule WHERE tracker_key = ${trackerKey} ORDER BY due_date ASC`;
  return Response.json(rows);
}

export async function POST(req: NextRequest) {
  const body = await req.json();
  const { trackerKey, title, location, frequency, due_date, notes } = body as Record<string, string>;
  if (!trackerKey || !title || !due_date) {
    return Response.json({ error: "trackerKey, title and due_date are required" }, { status: 400 });
  }

  const rows = await db().sql`
    INSERT INTO compliance_schedule (tracker_key, title, location, frequency, due_date, notes)
    VALUES (${trackerKey}, ${title}, ${location || null}, ${frequency || "One-time"}, ${due_date}, ${notes || null})
    RETURNING id, tracker_key, title, location, frequency, due_date, status, completed_date, notes`;
  return Response.json(rows[0], { status: 201 });
}
