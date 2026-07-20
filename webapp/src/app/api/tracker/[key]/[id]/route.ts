import { NextRequest } from "next/server";
import { trackerByKey, toColumnSpecs } from "@/lib/trackers";
import { createItemApi } from "@/lib/tableApi";

export async function PATCH(req: NextRequest, ctx: { params: Promise<{ key: string; id: string }> }) {
  const { key, id } = await ctx.params;
  const tracker = trackerByKey(key);
  if (!tracker) return Response.json({ error: "unknown tracker" }, { status: 404 });
  const api = createItemApi(tracker.table, toColumnSpecs(tracker));
  return api.PATCH(req, { params: Promise.resolve({ id }) });
}

export async function DELETE(req: NextRequest, ctx: { params: Promise<{ key: string; id: string }> }) {
  const { key, id } = await ctx.params;
  const tracker = trackerByKey(key);
  if (!tracker) return Response.json({ error: "unknown tracker" }, { status: 404 });
  const api = createItemApi(tracker.table, toColumnSpecs(tracker));
  return api.DELETE(req, { params: Promise.resolve({ id }) });
}
