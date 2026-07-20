import { NextRequest } from "next/server";
import { db } from "@/lib/db";
import { attachmentsStore } from "@/lib/blobs";

export const dynamic = "force-dynamic";

type Row = { id: number; blob_key: string; filename: string; content_type: string };

/** Streams the actual file bytes back - this is the "retrieve for audit" path. */
export async function GET(_req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const database = db();
  const rows = (await database.sql`SELECT id, blob_key, filename, content_type FROM attachments WHERE id = ${Number(id)}`) as Row[];
  if (rows.length === 0) return Response.json({ error: "not found" }, { status: 404 });
  const row = rows[0];

  const blob = await attachmentsStore().get(row.blob_key, { type: "arrayBuffer" });
  if (!blob) return Response.json({ error: "file missing from storage" }, { status: 404 });

  return new Response(blob, {
    headers: {
      "Content-Type": row.content_type,
      "Content-Disposition": `inline; filename="${row.filename.replace(/"/g, "")}"`,
    },
  });
}

export async function DELETE(_req: NextRequest, ctx: { params: Promise<{ id: string }> }) {
  const { id } = await ctx.params;
  const database = db();
  const rows = (await database.sql`SELECT blob_key FROM attachments WHERE id = ${Number(id)}`) as { blob_key: string }[];
  if (rows.length === 0) return new Response(null, { status: 204 });

  await attachmentsStore().delete(rows[0].blob_key);
  await database.sql`DELETE FROM attachments WHERE id = ${Number(id)}`;
  return new Response(null, { status: 204 });
}
