import { NextRequest } from "next/server";
import { randomUUID } from "crypto";
import { db } from "@/lib/db";
import { attachmentsStore } from "@/lib/blobs";

export const dynamic = "force-dynamic";

/** List evidence/photos for a record (trackerKey+recordId), or every photo
 * across a whole tracker (trackerKey + kind=photo, no recordId) for the
 * horizontal gallery. */
export async function GET(req: NextRequest) {
  const sp = req.nextUrl.searchParams;
  const trackerKey = sp.get("trackerKey");
  const recordId = sp.get("recordId");
  const kind = sp.get("kind");
  if (!trackerKey) return Response.json({ error: "trackerKey is required" }, { status: 400 });

  const database = db();
  const clauses = [`tracker_key = $1`];
  const params: unknown[] = [trackerKey];
  if (recordId) { params.push(Number(recordId)); clauses.push(`record_id = $${params.length}`); }
  if (kind) { params.push(kind); clauses.push(`kind = $${params.length}`); }

  const rows = await database.sql.unsafe(
    `SELECT id, tracker_key, record_id, filename, content_type, size_bytes, kind, uploaded_at
     FROM attachments WHERE ${clauses.join(" AND ")} ORDER BY uploaded_at DESC`,
    params
  );
  return Response.json(rows);
}

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const trackerKey = String(form.get("trackerKey") || "");
  const recordId = Number(form.get("recordId"));
  const file = form.get("file") as File | null;

  if (!trackerKey || !recordId || !file) {
    return Response.json({ error: "trackerKey, recordId and file are required" }, { status: 400 });
  }

  const arrayBuf = await file.arrayBuffer();
  const blobKey = `${trackerKey}/${recordId}/${randomUUID()}-${file.name}`;
  const kind = file.type.startsWith("image/") ? "photo" : "document";

  await attachmentsStore().set(blobKey, arrayBuf, {
    metadata: { filename: file.name, contentType: file.type || "application/octet-stream" },
  });

  const database = db();
  const rows = await database.sql`
    INSERT INTO attachments (tracker_key, record_id, filename, content_type, size_bytes, blob_key, kind)
    VALUES (${trackerKey}, ${recordId}, ${file.name}, ${file.type || "application/octet-stream"}, ${arrayBuf.byteLength}, ${blobKey}, ${kind})
    RETURNING id, tracker_key, record_id, filename, content_type, size_bytes, kind, uploaded_at`;

  return Response.json(rows[0], { status: 201 });
}
