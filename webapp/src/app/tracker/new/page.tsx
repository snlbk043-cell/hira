"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { FieldRole, FieldType } from "@/lib/trackers";
import IconPicker from "@/components/IconPicker";

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

const ROLE_OPTIONS: { value: FieldRole | "none"; label: string; hint: string }[] = [
  { value: "none", label: "— No special role —", hint: "Just a plain data column - shown in the table only." },
  { value: "date", label: "📅 Date (required, exactly one)", hint: "Drives the Monthly Trend chart and Year/Month filters." },
  { value: "department", label: "🏢 Department", hint: "Adds a Department filter and the Department Breakdown chart/table." },
  { value: "status", label: "✅ Status", hint: "Adds Closed %, Overdue and Open KPI cards + a Status Mix donut chart." },
  { value: "category", label: "🏷️ Category", hint: "Adds a Category Breakdown bar chart." },
  { value: "risk", label: "⚠️ Risk / Severity", hint: "Adds a High/Critical KPI card + a Risk Mix donut chart." },
  { value: "metric_pct", label: "📊 Metric % (auto-calculated)", hint: "Shows as an Avg % KPI card. Pair with Target + Actual below to auto-calculate it." },
  { value: "target_num", label: "🎯 Target (number)", hint: "Paired with Actual + Metric % to auto-calculate the percentage." },
  { value: "actual_num", label: "📈 Actual (number)", hint: "Paired with Target + Metric % to auto-calculate the percentage." },
];

const roleHint = (role: FieldRole | "none") => ROLE_OPTIONS.find((r) => r.value === role)?.hint ?? "";

function slugify(label: string): string {
  return label.toLowerCase().trim().replace(/[^a-z0-9]+/g, "_").replace(/(^_|_$)/g, "");
}

function sampleValue(f: DraftField, i: number): string {
  if (f.type === "date") {
    const d = new Date();
    d.setDate(d.getDate() - i * 3);
    return d.toISOString().slice(0, 10);
  }
  if (f.type === "number") return String(10 + i * 7);
  if (f.type === "department") return ["Production", "Maintenance", "Quality"][i % 3];
  if (f.type === "select") {
    const opts = f.options.split(",").map((o) => o.trim()).filter(Boolean);
    return opts.length ? opts[i % opts.length] : "Option A";
  }
  return ["Sample entry", "Example text", "Demo value"][i % 3];
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
  function addField(preset?: Partial<DraftField>) {
    setFields((fs) => [...fs, { label: "", type: "text", options: "", role: "none", required: false, ...preset }]);
  }
  function addTargetActualTrio() {
    setFields((fs) => [
      ...fs,
      { label: "Target", type: "number", options: "", role: "target_num", required: false },
      { label: "Actual", type: "number", options: "", role: "actual_num", required: false },
      { label: "Completion %", type: "number", options: "", role: "metric_pct", required: false },
    ]);
  }
  function removeField(i: number) {
    setFields((fs) => fs.filter((_, idx) => idx !== i));
  }

  const usable = fields.filter((f) => f.label.trim());
  const hasStatus = usable.some((f) => f.role === "status");
  const hasMetric = usable.some((f) => f.role === "metric_pct");
  const hasDept = usable.some((f) => f.role === "department");
  const hasCategory = usable.some((f) => f.role === "category");
  const hasRisk = usable.some((f) => f.role === "risk");
  const metricField = usable.find((f) => f.role === "metric_pct");

  const kpiPreview = [
    "📋 Total Records",
    ...(hasStatus ? ["✅ Closed / Completed %", "⏰ Overdue", "🔓 Open / In Progress"] : []),
    ...(hasRisk ? ["⚠️ High / Critical"] : []),
    ...(hasMetric ? [`📈 Avg ${metricField?.label || "Metric"}`] : []),
    ...(hasDept ? ["🏢 Departments Involved"] : []),
    "🗓️ This Month",
  ];
  const chartPreview = [
    "📈 Monthly Trend",
    ...(hasStatus ? ["🍩 Status Mix"] : []),
    ...(hasCategory ? ["📊 Category Breakdown"] : []),
    ...(hasRisk ? ["🍩 Risk Mix"] : []),
    ...(hasDept ? ["📊 Department Breakdown"] : []),
  ];

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!label.trim()) { setError("Tracker name is required."); return; }
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
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">➕ Create New Tracker</h1>
      <p className="text-grey text-sm mb-4">
        Define a custom tracker with your own fields — watch the live preview on the right update as you go, so you
        know exactly what dashboard and table you&apos;ll get before you create it.
      </p>

      <div className="grid grid-cols-1 2xl:grid-cols-[minmax(0,1fr)_380px] gap-4 items-start">
        <form onSubmit={submit} className="space-y-4 min-w-0">
          <div className="card p-4 grid grid-cols-1 md:grid-cols-[80px_1fr] gap-3">
            <div className="flex flex-col gap-1">
              <label className="text-xs text-grey">Icon</label>
              <IconPicker value={icon} onChange={setIcon} />
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
            <div className="flex items-center justify-between mb-2 flex-wrap gap-2">
              <div className="text-sm font-semibold">Fields</div>
              <div className="flex flex-wrap gap-1.5">
                <button type="button" onClick={() => addField()} className="text-[11px] px-2.5 py-1 rounded-md border border-teal/40 text-teal hover:bg-teal/10">+ Plain Field</button>
                <button type="button" onClick={() => addField({ label: "Status", type: "select", options: "Completed, In Progress, Pending, Overdue", role: "status" })} className="text-[11px] px-2.5 py-1 rounded-md border border-border text-grey hover:text-white hover:bg-card-2">+ Status</button>
                <button type="button" onClick={() => addField({ label: "Category", type: "select", options: "Type A, Type B, Type C", role: "category" })} className="text-[11px] px-2.5 py-1 rounded-md border border-border text-grey hover:text-white hover:bg-card-2">+ Category</button>
                <button type="button" onClick={() => addField({ label: "Risk Level", type: "select", options: "Critical, High, Medium, Low", role: "risk" })} className="text-[11px] px-2.5 py-1 rounded-md border border-border text-grey hover:text-white hover:bg-card-2">+ Risk Level</button>
                <button type="button" onClick={addTargetActualTrio} className="text-[11px] px-2.5 py-1 rounded-md border border-border text-grey hover:text-white hover:bg-card-2">+ Target/Actual %</button>
              </div>
            </div>
            <p className="text-xs text-grey mb-3">
              Use the quick-add buttons for common columns — they&apos;re pre-configured with the right Role so KPIs and charts appear automatically.
            </p>
            <div className="space-y-2">
              {fields.map((f, i) => (
                <div key={i} className="card p-2.5 bg-card-2 min-w-0">
                  <div className="grid grid-cols-2 sm:grid-cols-4 lg:grid-cols-[minmax(0,1fr)_130px_minmax(0,1fr)_70px_22px] gap-2 items-start">
                    <div className="flex flex-col gap-1 col-span-2 sm:col-span-2 lg:col-span-1 min-w-0">
                      <label className="text-[10px] text-grey">Field Label</label>
                      <input value={f.label} onChange={(e) => updateField(i, { label: e.target.value })} placeholder="e.g. Contractor Name" className="w-full min-w-0" />
                    </div>
                    <div className="flex flex-col gap-1 min-w-0">
                      <label className="text-[10px] text-grey">Type</label>
                      <select value={f.type} onChange={(e) => updateField(i, { type: e.target.value as FieldType })} className="w-full min-w-0">
                        {TYPE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    </div>
                    <div className="flex flex-col gap-1 col-span-2 sm:col-span-2 lg:col-span-1 min-w-0">
                      <label className="text-[10px] text-grey">Role (drives KPIs/charts)</label>
                      <select value={f.role} onChange={(e) => updateField(i, { role: e.target.value as FieldRole | "none" })} className="w-full min-w-0">
                        {ROLE_OPTIONS.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
                      </select>
                    </div>
                    <div className="flex flex-col gap-1 items-center">
                      <label className="text-[10px] text-grey whitespace-nowrap">Required</label>
                      <input type="checkbox" checked={f.required} onChange={(e) => updateField(i, { required: e.target.checked })} className="mt-1.5 w-4 h-4" />
                    </div>
                    <button type="button" onClick={() => removeField(i)} className="text-coral mt-4 justify-self-end" aria-label="Remove field">✕</button>
                  </div>
                  {f.role !== "none" && <p className="text-[11px] text-teal mt-1.5">ℹ️ {roleHint(f.role)}</p>}
                  {f.type === "select" && (
                    <div className="mt-2 flex flex-col gap-1">
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

        {/* Live preview */}
        <div className="2xl:sticky 2xl:top-4 space-y-3 min-w-0">
          <div className="card p-4" style={{ animation: "kpi-rise 320ms ease both" }}>
            <div className="flex items-center gap-2 mb-3">
              <span className="w-1.5 h-1.5 rounded-full bg-teal shadow-[0_0_8px_2px_rgba(20,184,166,0.6)]" />
              <div className="text-sm font-semibold text-white">Live Preview</div>
            </div>
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">{icon || "📁"}</span>
              <span className="font-bold text-white">{label || "Untitled Tracker"}</span>
            </div>

            <div className="text-[11px] text-grey uppercase tracking-wide mb-1.5">KPI Cards You&apos;ll Get</div>
            <div className="flex flex-wrap gap-1.5 mb-3">
              {kpiPreview.map((k) => (
                <span key={k} className="text-[11px] px-2 py-1 rounded-md bg-teal/10 border border-teal/25 text-white/90">{k}</span>
              ))}
            </div>

            <div className="text-[11px] text-grey uppercase tracking-wide mb-1.5">Charts You&apos;ll Get</div>
            <div className="flex flex-wrap gap-1.5 mb-3">
              {chartPreview.map((c) => (
                <span key={c} className="text-[11px] px-2 py-1 rounded-md bg-purple/10 border border-purple/25 text-white/90">{c}</span>
              ))}
            </div>

            <div className="text-[11px] text-grey uppercase tracking-wide mb-1.5">Records Table Preview</div>
            {usable.length === 0 ? (
              <p className="text-xs text-grey">Add fields to see a preview.</p>
            ) : (
              <div className="overflow-x-auto rounded-md border border-border">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr>
                      {usable.map((f) => <th key={f.label} className="text-left p-1.5 text-grey whitespace-nowrap bg-card-2">{f.label}</th>)}
                    </tr>
                  </thead>
                  <tbody>
                    {[0, 1].map((i) => (
                      <tr key={i} className="border-t border-border">
                        {usable.map((f) => <td key={f.label} className="p-1.5 whitespace-nowrap text-grey">{sampleValue(f, i)}</td>)}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
            <p className="text-[11px] text-grey mt-3">
              Plus: entry form, evidence uploads, photo gallery, PDF/PPT/Excel export — automatically, same as every built-in tracker.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
