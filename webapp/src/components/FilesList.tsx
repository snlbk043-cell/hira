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
      <div className="files-scroll max-h-64 overflow-y-scroll pr-1 -mr-1">
        <div className="divide-y divide-border">
          {files.map((f) => (
            <a
              key={f.id}
              href={`/api/attachments/${f.id}`}
              target="_blank"
              rel="noreferrer"
              className="flex items-center gap-2.5 py-1.5 hover:bg-card-2 rounded-md transition-colors group px-1"
            >
              <span className="text-base shrink-0 w-6 text-center">{fileIcon(f.content_type)}</span>
              <span className="text-xs truncate flex-1 min-w-0 group-hover:text-teal transition-colors">{f.filename}</span>
              <span
                className={`text-[10px] px-1.5 py-0.5 rounded-full shrink-0 ${
                  f.kind === "photo" ? "bg-purple/15 text-purple border border-purple/25" : "bg-gold/15 text-gold border border-gold/25"
                }`}
              >
                {f.kind === "photo" ? "📷 Photo" : "📄 Document"}
              </span>
              <span className="text-[10px] text-grey shrink-0 hidden sm:inline">Rec #{f.record_id} · {formatSize(f.size_bytes)}</span>
              <span className="text-[10px] text-grey shrink-0 tabular-nums w-16 text-right">
                {new Date(f.uploaded_at).toLocaleDateString(undefined, { month: "short", day: "numeric" })}
              </span>
              <span className="text-teal text-[10px] shrink-0 opacity-0 group-hover:opacity-100 transition-opacity w-10 text-right">Open ↗</span>
            </a>
          ))}
        </div>
      </div>
    </ChartCard>
  );
}
