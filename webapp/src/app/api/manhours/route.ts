import { NextRequest } from "next/server";
import { db } from "@/lib/db";

export async function GET(req: NextRequest) {
  const year = req.nextUrl.searchParams.get("year");
  const database = db();
  const rows = year
    ? await database.sql`SELECT * FROM manhours WHERE year = ${Number(year)} AND department = 'All' ORDER BY month`
    : await database.sql`SELECT * FROM manhours WHERE department = 'All' ORDER BY year DESC, month`;
  return Response.json(rows);
}

// Upsert one month's plant-wide man-hours.
export async function POST(req: NextRequest) {
  const { year, month, hours } = await req.json();
  if (!year || !month || hours === undefined) {
    return Response.json({ error: "year, month and hours are required" }, { status: 400 });
  }
  const database = db();
  const rows = await database.sql`
    INSERT INTO manhours (year, month, department, hours)
    VALUES (${year}, ${month}, 'All', ${hours})
    ON CONFLICT (year, month, department)
    DO UPDATE SET hours = EXCLUDED.hours
    RETURNING *
  `;
  return Response.json(rows[0], { status: 201 });
}
