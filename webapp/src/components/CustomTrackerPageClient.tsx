"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { TrackerDef } from "@/lib/trackers";
import TrackerPageClient from "@/components/TrackerPageClient";

export default function CustomTrackerPageClient({ trackerKey }: { trackerKey: string }) {
  const [tracker, setTracker] = useState<TrackerDef | null>(null);
  const [notFound, setNotFound] = useState(false);

  useEffect(() => {
    fetch(`/api/custom-trackers/${trackerKey}`)
      .then((r) => {
        if (!r.ok) { setNotFound(true); return null; }
        return r.json();
      })
      .then((data) => { if (data) setTracker(data); })
      .catch(() => setNotFound(true));
  }, [trackerKey]);

  if (notFound) {
    return (
      <div className="max-w-2xl mx-auto p-6 text-center">
        <p className="text-grey">This custom tracker doesn&apos;t exist (it may have been deleted).</p>
        <Link href="/tracker/new" className="text-teal underline text-sm mt-2 inline-block">Create a new tracker</Link>
      </div>
    );
  }
  if (!tracker) return <div className="max-w-6xl mx-auto p-4 text-grey text-sm">Loading…</div>;

  return <TrackerPageClient trackerKey={trackerKey} customTracker={tracker} endpointOverride={`/api/custom-trackers/${trackerKey}/records`} />;
}
