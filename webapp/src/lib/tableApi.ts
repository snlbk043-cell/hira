import { NextRequest } from "next/server";
import { db } from "./db";

export type ColumnSpec = {
  name: string;
  type: "text" | "number" | "date" | "boolean";
  required?: boolean;
};

/**
 * Generic list+create handlers for one register table. Kept deliberately simple
 * (no ORM) since every table here is a flat register, same shape as the Excel
 * registers this app replaces. Dynamic filter/column lists go through
 * db.sql.unsafe() with numbered placeholders (still fully parameterized) since
 * the tagged-template form only supports one complete, static query shape.
 */
export function createTableApi(table: string, dateColumn: string, columns: ColumnSpec[]) {
  assertIdentifier(table);
  assertIdentifier(dateColumn);

  async function GET(req: NextRequest) {
    const sp = req.nextUrl.searchParams;
    const from = sp.get("from");
    const to = sp.get("to");
    const department = sp.get("department");
    const limit = Math.min(Number(sp.get("limit")) || 500, 5000);

    const clauses: string[] = [];
    const params: unknown[] = [];
    if (from) { params.push(from); clauses.push(`"${dateColumn}" >= $${params.length}`); }
    if (to) { params.push(to); clauses.push(`"${dateColumn}" <= $${params.length}`); }
    if (department && department !== "All") { params.push(department); clauses.push(`"department" = $${params.length}`); }
    const where = clauses.length ? `WHERE ${clauses.join(" AND ")}` : "";
    params.push(limit);

    const sql = `SELECT * FROM "${table}" ${where} ORDER BY "${dateColumn}" DESC LIMIT $${params.length}`;
    const rows = await db().sql.unsafe(sql, params);
    return Response.json(rows);
  }

  async function POST(req: NextRequest) {
    const body = await req.json();
    for (const c of columns) {
      if (c.required && (body[c.name] === undefined || body[c.name] === "")) {
        return Response.json({ error: `${c.name} is required` }, { status: 400 });
      }
    }
    const present = columns.filter((c) => body[c.name] !== undefined && body[c.name] !== "");
    const colList = present.map((c) => `"${c.name}"`).join(", ");
    const placeholders = present.map((_, i) => `$${i + 1}`).join(", ");
    const values = present.map((c) => coerce(body[c.name], c.type));

    const sql = `INSERT INTO "${table}" (${colList}) VALUES (${placeholders}) RETURNING *`;
    const rows = await db().sql.unsafe(sql, values);
    return Response.json(rows[0], { status: 201 });
  }

  async function DELETE() {
    await db().sql.unsafe(`DELETE FROM "${table}"`);
    return new Response(null, { status: 204 });
  }

  return { GET, POST, DELETE };
}

export function createItemApi(table: string, columns: ColumnSpec[]) {
  assertIdentifier(table);

  async function PATCH(req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
    const { id } = await ctx.params;
    const body = await req.json();
    const present = columns.filter((c) => body[c.name] !== undefined);
    if (present.length === 0) return Response.json({ error: "no fields to update" }, { status: 400 });

    const setList = present.map((c, i) => `"${c.name}" = $${i + 1}`).join(", ");
    const values = present.map((c) => coerce(body[c.name], c.type));
    values.push(Number(id));

    const sql = `UPDATE "${table}" SET ${setList}, updated_at = NOW() WHERE id = $${values.length} RETURNING *`;
    const rows = await db().sql.unsafe(sql, values);
    if (rows.length === 0) return Response.json({ error: "not found" }, { status: 404 });
    return Response.json(rows[0]);
  }

  async function DELETE(_req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
    const { id } = await ctx.params;
    await db().sql.unsafe(`DELETE FROM "${table}" WHERE id = $1`, [Number(id)]);
    return new Response(null, { status: 204 });
  }

  return { PATCH, DELETE };
}

function coerce(value: unknown, type: ColumnSpec["type"]) {
  if (value === "" || value === undefined || value === null) return null;
  if (type === "number") return typeof value === "number" ? value : Number(value);
  if (type === "boolean") return Boolean(value);
  return value;
}

/** Table/column names here are always fixed string literals from our own route
 * files (never user input), but this guards against a future mistake. */
function assertIdentifier(name: string) {
  if (!/^[a-z_][a-z0-9_]*$/.test(name)) throw new Error(`unsafe identifier: ${name}`);
}
