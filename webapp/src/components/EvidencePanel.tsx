"use client";
import { useCallback, useEffect, useState } from "react";
import { fileIcon, formatSize } from "@/lib/fileHelpers";

type Attachment = {
  id: number;
  filename: string;
  content_type: string;
  size_bytes: number;
  kind: "photo" | "document";
  uploaded_at: string;
};

export default function EvidencePanel({ trackerKey, recordId, onClose }: { trackerKey: string; recordId: number; onClose: () => void }) {
  const [items, setItems] = useState<Attachment[]>([]);
  const [loading, setLoading] = useState(true);
  const [uploading, setUploading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    fetch(`/api/attachments?trackerKey=${encodeURIComponent(trackerKey)}&recordId=${recordId}`)
      .then((r) => r.json())
      .then(setItems)
      .finally(() => setLoading(false));
  }, [trackerKey, recordId]);

  useEffect(() => { load(); }, [load]);

  async function handleUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const files = e.target.files;
    if (!files || files.length === 0) return;
    setUploading(true);
    setError(null);
    try {
      for (const file of Array.from(files)) {
        const fd = new FormData();
        fd.append("trackerKey", trackerKey);
        fd.append("recordId", String(recordId));
        fd.append("file", file);
        const res = await fetch("/api/attachments", { method: "POST", body: fd });
        if (!res.ok) throw new Error("Upload failed");
      }
      load();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setUploading(false);
      e.target.value = "";
    }
  }

  async function handleDelete(id: number) {
    if (!confirm("Delete this file?")) return;
    await fetch(`/api/attachments/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div className="modal-backdrop fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/60" onClick={onClose}>
      <div className="modal-pop card w-full max-w-lg max-h-[80vh] flex flex-col p-4" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm font-semibold flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-teal shadow-[0_0_8px_2px_rgba(20,184,166,0.6)]" />
            Evidence — Record #{recordId}
          </div>
          <button onClick={onClose} className="text-grey hover:text-white text-lg leading-none">✕</button>
        </div>

        <label className="card p-3 mb-3 flex items-center justify-center gap-2 border-dashed border-2 border-border hover:border-teal/50 cursor-pointer transition-colors text-sm text-grey">
          <input type="file" multiple className="hidden" onChange={handleUpload} disabled={uploading} />
          {uploading ? "Uploading…" : "📤 Click to upload evidence (any file type — photos, PDFs, docs…)"}
        </label>
        {error && <p className="text-coral text-xs mb-2">{error}</p>}

        <div className="overflow-y-auto flex-1 space-y-2">
          {loading ? (
            <p className="text-grey text-sm">Loading…</p>
          ) : items.length === 0 ? (
            <p className="text-grey text-sm text-center py-6">No evidence uploaded yet for this record.</p>
          ) : (
            items.map((a) => (
              <div key={a.id} className="flex items-center gap-3 p-2 rounded-lg border border-border bg-card-2">
                <span className="text-xl shrink-0">{fileIcon(a.content_type)}</span>
                <div className="min-w-0 flex-1">
                  <div className="text-sm truncate">{a.filename}</div>
                  <div className="text-[11px] text-grey">
                    {formatSize(a.size_bytes)} · {new Date(a.uploaded_at).toLocaleDateString()}
                  </div>
                </div>
                <a
                  href={`/api/attachments/${a.id}`}
                  target="_blank"
                  rel="noreferrer"
                  className="text-xs px-2.5 py-1 rounded-md border border-teal/40 text-teal hover:bg-teal/10 shrink-0"
                >
                  View
                </a>
                <button onClick={() => handleDelete(a.id)} className="text-xs px-2 py-1 rounded-md border border-coral/40 text-coral hover:bg-coral/10 shrink-0">
                  ✕
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
