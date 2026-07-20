import { NextRequest } from "next/server";
import { trackerByKey, dateFieldOf, toColumnSpecs } from "@/lib/trackers";
import { createTableApi } from "@/lib/tableApi";

export async function GET(req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  const tracker = trackerByKey(key);
  if (!tracker) return Response.json({ error: "unknown tracker" }, { status: 404 });
  const api = createTableApi(tracker.table, dateFieldOf(tracker), toColumnSpecs(tracker));
  return api.GET(req);
}

export async function POST(req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  const tracker = trackerByKey(key);
  if (!tracker) return Response.json({ error: "unknown tracker" }, { status: 404 });
  const api = createTableApi(tracker.table, dateFieldOf(tracker), toColumnSpecs(tracker));
  return api.POST(req);
}

export async function DELETE(_req: NextRequest, ctx: { params: Promise<{ key: string }> }) {
  const { key } = await ctx.params;
  const tracker = trackerByKey(key);
  if (!tracker) return Response.json({ error: "unknown tracker" }, { status: 404 });
  const api = createTableApi(tracker.table, dateFieldOf(tracker), toColumnSpecs(tracker));
  return api.DELETE();
}
