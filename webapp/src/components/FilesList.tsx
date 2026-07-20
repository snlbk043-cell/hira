"use client";
import { useEffect, useState } from "react";
import ChartCard from "@/components/ChartCard";
import { fileIcon, formatSize } from "@/lib/fileHelpers";

type FileEntry = {
  id: number;
  record_id: number;
  filename: string;
  content_type: string;
  size_bytes: number;
  kind: "photo" | "document";
  uploaded_at: string;
};

export default function FilesList({ trackerKey }: { trackerKey: string }) {
  const [files, setFiles] = useState<FileEntry[] | null>(null);

  useEffect(() => {
    fetch(`/api/attachments?trackerKey=${encodeURIComponent(trackerKey)}`)
      .then((r) => r.json())
      .then(setFiles);
  }, [trackerKey]);

  if (files === null || files.length === 0) return null;

  return (
    <ChartCard title={`All Evidence Files — Date-wise (${files.length})`} className="mb-6">
      <div className="max-h-80 overflow-y-auto divide-y divide-border">
        {files.map((f) => (
          <a
            key={f.id}
            href={`/api/attachments/${f.id}`}
            target="_blank"
            rel="noreferrer"
            className="flex items-center gap-3 py-2.5 px-1 hover:bg-card-2 rounded-md transition-colors group"
          >
            <span className="text-lg shrink-0">{fileIcon(f.content_type)}</span>
            <div className="min-w-0 flex-1">
              <div className="text-sm truncate group-hover:text-teal transition-colors">{f.filename}</div>
              <div className="text-[11px] text-grey">Record #{f.record_id} · {formatSize(f.size_bytes)}</div>
            </div>
            <div className="text-xs text-grey shrink-0 tabular-nums">
              {new Date(f.uploaded_at).toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })}
            </div>
            <span className="text-teal text-xs shrink-0 opacity-0 group-hover:opacity-100 transition-opacity">Open ↗</span>
          </a>
        ))}
      </div>
    </ChartCard>
  );
}
