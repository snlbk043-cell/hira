import { NextRequest } from "next/server";
import { brandingStore } from "@/lib/blobs";

export const dynamic = "force-dynamic";

const LOGO_KEY = "logo";

export async function GET() {
  const store = brandingStore();
  const result = await store.getWithMetadata(LOGO_KEY, { type: "arrayBuffer" });
  if (!result) return new Response(null, { status: 404 });
  const contentType = (result.metadata?.contentType as string) || "image/png";
  return new Response(result.data, {
    headers: { "Content-Type": contentType, "Cache-Control": "no-cache" },
  });
}

export async function POST(req: NextRequest) {
  const form = await req.formData();
  const file = form.get("file") as File | null;
  if (!file) return Response.json({ error: "file is required" }, { status: 400 });
  if (!file.type.startsWith("image/")) return Response.json({ error: "logo must be an image" }, { status: 400 });

  const arrayBuf = await file.arrayBuffer();
  await brandingStore().set(LOGO_KEY, arrayBuf, { metadata: { contentType: file.type } });
  return Response.json({ ok: true });
}

export async function DELETE() {
  await brandingStore().delete(LOGO_KEY);
  return new Response(null, { status: 204 });
}
