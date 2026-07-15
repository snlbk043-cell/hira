import { notFound } from "next/navigation";
import { trackerByKey } from "@/lib/trackers";
import TrackerPageClient from "@/components/TrackerPageClient";

export default async function Page({ params }: { params: Promise<{ key: string }> }) {
  const { key } = await params;
  const tracker = trackerByKey(key);
  if (!tracker) notFound();
  return <TrackerPageClient trackerKey={key} />;
}
