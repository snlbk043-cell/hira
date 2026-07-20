"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { FieldRole, FieldType } from "@/lib/trackers";

type DraftField = {
  label: string;
  type: FieldType;
  options: string;
  role: FieldRole | "none";
  required: boolean;
};

const TYPE_OPTIONS: { value: FieldType; label: string }[] = [
  { value: "text", label: "Text" },
  { value: "number", label: "Number" },
  { value: "date", label: "Date" },
  { value: "select", label: "Dropdown (select)" },
  { value: "department", label: "Department (standard list)" },
];

const ROLE_OPTIONS: { value: FieldRole | "none"; label: string }[] = [
  { value: "none", label: "— No special role —" },
  { value: "date", label: "Date (required, exactly one)" },
  { value: "department", label: "Department" },
  { value: "status", label: "Status" },
  { value: "category", label: "Category" },
  { value: "risk", label: "Risk / Severity" },
  { value: "metric_pct", label: "Metric % (auto-calculated if target+actual set)" },
  { value: "target_num", label: "Target (number)" },
  { value: "actual_num", label: "Actual (number)" },
];

function slugify(label: string): string {
  return label.toLowerCase().trim().replace(/[^a-z0-9]+/g, "_").replace(/(^_|_$)/g, "");
}

function emptyField(): DraftField {
  return { label: "", type: "text", options: "", role: "none", required: false };
}

export default function NewTrackerPage() {
  const router = useRouter();
  const [label, setLabel] = useState("");
  const [icon, setIcon] = useState("📁");
  const [description, setDescription] = useState("");
  const [fields, setFields] = useState<DraftField[]>([
    { label: "Date", type: "date", options: "", role: "date", required: true },
    { label: "Department", type: "department", options: "", role: "department", required: true },
  ]);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);

  function updateField(i: number, patch: Partial<DraftField>) {
    setFields((fs) => fs.map((f, idx) => (idx === i ? { ...f, ...patch } : f)));
  }
  function addField() {
    setFields((fs) => [...fs, emptyField()]);
  }
  function removeField(i: number) {
    setFields((fs) => fs.filter((_, idx) => idx !== i));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!label.trim()) { setError("Tracker name is required."); return; }
    const usable = fields.filter((f) => f.label.trim());
    if (usable.length === 0) { setError("Add at least one field."); return; }
    if (!usable.some((f) => f.role === "date")) { setError("Exactly one field must be marked as the Date role."); return; }

    const payloadFields = usable.map((f) => ({
      name: slugify(f.label),
      label: f.label,
      type: f.type,
      options: f.type === "select" ? f.options.split(",").map((o) => o.trim()).filter(Boolean) : undefined,
      role: f.role === "none" ? undefined : f.role,
      required: f.required,
    }));

    setSaving(true);
    try {
      const res = await fetch("/api/custom-trackers", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ label, icon, description, fields: payloadFields }),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || "Failed to create tracker");
      }
      const created = await res.json();
      router.push(`/tracker/custom/${created.key}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">➕ Create New Tracker</h1>
      <p className="text-grey text-sm mb-4">
        Define a custom tracker with your own fields. It gets its own KPI cards, charts, entry form, records table,
        evidence uploads and photo gallery — automatically, just like the built-in 25 — and appears in the sidebar.
      </p>

      <form onSubmit={submit} className="space-y-4">
        <div className="card p-4 grid grid-cols-1 md:grid-cols-[80px_1fr] gap-3">
          <div className="flex flex-col gap-1">
            <label className="text-xs text-grey">Icon (emoji)</label>
            <input value={icon} onChange={(e) => setIcon(e.target.value)} maxLength={4} className="text-center text-xl" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-xs text-grey">Tracker Name *</label>
            <input value={label} onChange={(e) => setLabel(e.target.value)} placeholder="e.g. Contractor Safety Audits" required />
          </div>
          <div className="flex flex-col gap-1 md:col-span-2">
            <label className="text-xs text-grey">Description</label>
            <input value={description} onChange={(e) => setDescription(e.target.value)} placeholder="Short description shown under the tracker title" />
          </div>
        </div>

        <div className="card p-4">
          <div className="flex items-center justify-between mb-3">
            <div className="text-sm font-semibold">Fields</div>
            <button type="button" onClick={addField} className="text-xs px-3 py-1.5 rounded-md border border-teal/40 text-teal hover:bg-teal/10">
              + Add Field
            </button>
          </div>
          <div className="space-y-2">
            {fields.map((f, i) => (
              <div key={i} className="grid grid-cols-1 md:grid-cols-[1fr_140px_1fr_90px_28px] gap-2 items-start card p-2 bg-card-2">
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] text-grey">Field Label</label>
                  <input value={f.label} onChange={(e) => updateField(i, { label: e.target.value })} placeholder="e.g. Contractor Name" />
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] text-grey">Type</label>
                  <select value={f.type} onChange={(e) => updateField(i, { type: e.target.value as FieldType })}>
                    {TYPE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div className="flex flex-col gap-1">
                  <label className="text-[10px] text-grey">Role (drives KPIs/charts)</label>
                  <select value={f.role} onChange={(e) => updateField(i, { role: e.target.value as FieldRole | "none" })}>
                    {ROLE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                  </select>
                </div>
                <div className="flex flex-col gap-1 items-center">
                  <label className="text-[10px] text-grey">Required</label>
                  <input type="checkbox" checked={f.required} onChange={(e) => updateField(i, { required: e.target.checked })} className="mt-1.5 w-4 h-4" />
                </div>
                <button type="button" onClick={() => removeField(i)} className="text-coral mt-4" aria-label="Remove field">✕</button>
                {f.type === "select" && (
                  <div className="md:col-span-5 flex flex-col gap-1">
                    <label className="text-[10px] text-grey">Dropdown Options (comma-separated)</label>
                    <input value={f.options} onChange={(e) => updateField(i, { options: e.target.value })} placeholder="Option A, Option B, Option C" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {error && <p className="text-coral text-sm">{error}</p>}

        <button type="submit" disabled={saving} className="bg-teal text-[#0b1220] font-semibold px-5 py-2.5 rounded-md disabled:opacity-50">
          {saving ? "Creating…" : "Create Tracker"}
        </button>
      </form>
    </div>
  );
}
