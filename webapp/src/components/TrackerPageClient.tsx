"use client";
import { useCallback, useEffect, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip,
} from "recharts";
import { trackerByKey } from "@/lib/trackers";
import { computeSnapshot, Row } from "@/lib/aggregate";
import { DEPARTMENTS, MONTH_NAMES } from "@/lib/constants";
import KpiCard from "@/components/KpiCard";
import ChartCard from "@/components/ChartCard";
import RiskMatrix from "@/components/RiskMatrix";
import { exportTrackerPdf, exportTrackerPpt, exportTrackerExcel } from "@/lib/exportUtils";

const TEAL = "#14b8a6", GOLD = "#f5a524", CORAL = "#f0625a", PURPLE = "#8b5cf6";
const PALETTE = [TEAL, GOLD, CORAL, PURPLE, "#0b6ea8", "#22c55e", "#eab308", "#94a3b8"];
const AXIS = { stroke: "#94a3b8", fontSize: 11 };
const GRID = "#22314f";

function monthRange(year: number, month: number) {
  if (!month) return { from: `${year}-01-01`, to: `${year}-12-31` };
  const last = new Date(year, month, 0).getDate();
  const mm = String(month).padStart(2, "0");
  return { from: `${year}-${mm}-01`, to: `${year}-${mm}-${String(last).padStart(2, "0")}` };
}

export default function TrackerPageClient({ trackerKey }: { trackerKey: string }) {
  const tracker = trackerByKey(trackerKey)!;
  const endpoint = `/api/tracker/${trackerKey}`;

  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<Row>({});
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [exporting, setExporting] = useState<string | null>(null);

  const [year, setYear] = useState(new Date().getFullYear());
  const [month, setMonth] = useState(0);
  const [department, setDepartment] = useState("All");

  const load = useCallback(() => {
    setLoading(true);
    const { from, to } = monthRange(year, month);
    const params = new URLSearchParams({ limit: "5000", from, to });
    if (department !== "All") params.set("department", department);
    fetch(`${endpoint}?${params.toString()}`)
      .then((r) => r.json())
      .then(setRows)
      .finally(() => setLoading(false));
  }, [endpoint, year, month, department]);

  useEffect(() => { load(); }, [load]);

  function update(name: string, value: string) {
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const url = editingId ? `${endpoint}/${editingId}` : endpoint;
      const method = editingId ? "PATCH" : "POST";
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `Request failed (${res.status})`);
      }
      setForm({});
      setEditingId(null);
      setMessage(editingId ? "Updated." : "Added — KPIs and charts refreshed below.");
      load();
    } catch (err) {
      setMessage(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  function startEdit(row: Row) {
    setEditingId(Number(row.id));
    const f: Row = {};
    for (const field of tracker.fields) {
      const v = row[field.name];
      f[field.name] = field.type === "date" && typeof v === "string" ? v.slice(0, 10) : (v as string | number);
    }
    setForm(f);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function remove(id: number) {
    if (!confirm("Delete this record?")) return;
    await fetch(`${endpoint}/${id}`, { method: "DELETE" });
    load();
  }

  const snapshot = computeSnapshot(tracker, rows);
  const accentClass: Record<string, string> = { teal: "text-teal", gold: "text-gold", coral: "text-coral", purple: "text-purple" };

  async function doExport(kind: "pdf" | "ppt" | "excel") {
    setExporting(kind);
    try {
      if (kind === "pdf") exportTrackerPdf();
      else if (kind === "ppt") await exportTrackerPpt(tracker, snapshot);
      else await exportTrackerExcel(tracker, rows);
    } finally {
      setExporting(null);
    }
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <div className="flex flex-wrap items-start justify-between gap-3 mb-1">
        <div>
          <h1 className="text-2xl font-bold">{tracker.icon} {tracker.label}</h1>
          <p className="text-grey text-sm mt-1">{tracker.description}</p>
        </div>
        <div className="flex gap-2 no-print">
          <button onClick={() => doExport("pdf")} disabled={!!exporting} className="text-xs px-3 py-1.5 rounded-md border border-border text-grey hover:text-white hover:bg-card-2 disabled:opacity-50">
            {exporting === "pdf" ? "Preparing…" : "📄 Export PDF"}
          </button>
          <button onClick={() => doExport("ppt")} disabled={!!exporting} className="text-xs px-3 py-1.5 rounded-md border border-border text-grey hover:text-white hover:bg-card-2 disabled:opacity-50">
            {exporting === "ppt" ? "Building…" : "📊 Export PPT"}
          </button>
          <button onClick={() => doExport("excel")} disabled={!!exporting} className="text-xs px-3 py-1.5 rounded-md border border-border text-grey hover:text-white hover:bg-card-2 disabled:opacity-50">
            {exporting === "excel" ? "Building…" : "📗 Export Excel"}
          </button>
        </div>
      </div>

      <div className="card p-3 flex flex-wrap items-center gap-4 mb-4 no-print">
        <div className="flex items-center gap-2">
          <label className="text-xs text-grey">Year</label>
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {[year - 1, year, year + 1].map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-grey">Month</label>
          <select value={month} onChange={(e) => setMonth(Number(e.target.value))}>
            <option value={0}>All</option>
            {MONTH_NAMES.map((m, i) => <option key={m} value={i + 1}>{m}</option>)}
          </select>
        </div>
        <div className="flex items-center gap-2">
          <label className="text-xs text-grey">Department</label>
          <select value={department} onChange={(e) => setDepartment(e.target.value)}>
            <option value="All">All</option>
            {DEPARTMENTS.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
      </div>

      {loading ? (
        <p className="text-grey text-sm mt-6">Loading…</p>
      ) : (
        <>
          {/* KPI cards */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3 my-4">
            {snapshot.kpis.map((k) => (
              <KpiCard key={k.label} icon={k.icon} label={k.label} value={k.value} accent={k.accent} />
            ))}
          </div>

          {/* Charts */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {snapshot.charts.map((c) => (
              <ChartCard key={c.title} title={c.title}>
                <ResponsiveContainer width="100%" height={240}>
                  {c.type === "trend" ? (
                    <LineChart data={c.data}>
                      <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
                      <XAxis dataKey="label" tick={AXIS} />
                      <YAxis tick={AXIS} allowDecimals={false} />
                      <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f", borderRadius: 8, color: "white" }} />
                      <Line type="monotone" dataKey="value" stroke={TEAL} strokeWidth={2} dot={{ r: 3 }} />
                    </LineChart>
                  ) : c.type === "bar" ? (
                    <BarChart data={c.data} layout="vertical" margin={{ left: 24 }}>
                      <CartesianGrid stroke={GRID} strokeDasharray="3 3" horizontal={false} />
                      <XAxis type="number" tick={AXIS} allowDecimals={false} />
                      <YAxis type="category" dataKey="label" tick={{ ...AXIS, fontSize: 10 }} width={110} />
                      <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f", borderRadius: 8, color: "white" }} />
                      <Bar dataKey="value" fill={GOLD} radius={[0, 4, 4, 0]} />
                    </BarChart>
                  ) : (
                    <PieChart>
                      <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f", borderRadius: 8, color: "white" }} />
                      <Pie data={c.data} dataKey="value" nameKey="label" innerRadius={50} outerRadius={85} paddingAngle={2}>
                        {c.data.map((_, i) => <Cell key={i} fill={PALETTE[i % PALETTE.length]} />)}
                      </Pie>
                    </PieChart>
                  )}
                </ResponsiveContainer>
              </ChartCard>
            ))}
          </div>

          {tracker.key === "jsa" && <RiskMatrix rows={rows} />}

          {/* Department Performance + Monthly Performance Matrix */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
            {snapshot.deptTable.length > 0 && (
              <ChartCard title="Department Performance">
                <div className="overflow-x-auto mt-1">
                  <table className="w-full text-sm">
                    <thead>
                      <tr>
                        <th className="text-left p-2 text-grey">Department</th>
                        <th className="text-right p-2 text-grey">Count</th>
                        {snapshot.hasStatus && <th className="text-right p-2 text-grey">Closed %</th>}
                        {snapshot.hasMetric && <th className="text-right p-2 text-grey">Avg {snapshot.metricLabel}</th>}
                      </tr>
                    </thead>
                    <tbody>
                      {snapshot.deptTable.map((d) => (
                        <tr key={d.department} className="border-t border-border">
                          <td className="p-2">{d.department}</td>
                          <td className="p-2 text-right font-semibold">{d.count}</td>
                          {snapshot.hasStatus && <td className="p-2 text-right">{d.closedPct ?? "—"}%</td>}
                          {snapshot.hasMetric && <td className="p-2 text-right">{d.avgMetric ?? "—"}%</td>}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </ChartCard>
            )}
            <ChartCard title="Monthly Performance Matrix">
              <div className="overflow-x-auto mt-1">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      <th className="text-left p-2 text-grey">Month</th>
                      <th className="text-right p-2 text-grey">Records</th>
                      {snapshot.hasMetric && <th className="text-right p-2 text-grey">Avg {snapshot.metricLabel}</th>}
                    </tr>
                  </thead>
                  <tbody>
                    {snapshot.monthMatrix.map((m) => (
                      <tr key={m.month} className="border-t border-border">
                        <td className="p-2">{m.month}</td>
                        <td className="p-2 text-right font-semibold">{m.count}</td>
                        {snapshot.hasMetric && <td className="p-2 text-right">{m.avgMetric ?? "—"}%</td>}
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </ChartCard>
          </div>

          {/* Advanced Analysis: overdue ageing + hotspot watchlist (only where applicable) */}
          {(snapshot.aging || snapshot.hotspot.length > 0) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
              {snapshot.aging && (
                <ChartCard title="Overdue Ageing (open items)">
                  <ResponsiveContainer width="100%" height={220}>
                    <BarChart data={snapshot.aging}>
                      <CartesianGrid stroke={GRID} />
                      <XAxis dataKey="label" tick={AXIS} />
                      <YAxis tick={AXIS} allowDecimals={false} />
                      <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
                      <Bar dataKey="value" radius={[4, 4, 0, 0]}>
                        {snapshot.aging.map((d, i) => (
                          <Cell key={i} fill={d.label === "0-7" ? TEAL : d.label === "8-15" ? GOLD : d.label === "16-30" ? "#f2994a" : CORAL} />
                        ))}
                      </Bar>
                    </BarChart>
                  </ResponsiveContainer>
                </ChartCard>
              )}
              {snapshot.hotspot.length > 0 && (
                <ChartCard title="Repeat-Offender Watchlist (top 5 departments, high severity)">
                  <ul className="mt-2 space-y-2">
                    {snapshot.hotspot.map((h) => (
                      <li key={h.department} className="flex items-center justify-between text-sm border-l-2 border-coral pl-3 py-1.5">
                        <span>{h.department}</span>
                        <span className="text-coral font-bold">{h.count}</span>
                      </li>
                    ))}
                  </ul>
                </ChartCard>
              )}
            </div>
          )}

          {snapshot.forecast && (
            <ChartCard title="Target vs Actual + Next-Month Forecast (linear projection)" className="mb-6">
              <ResponsiveContainer width="100%" height={260}>
                <LineChart data={snapshot.forecast}>
                  <CartesianGrid stroke={GRID} strokeDasharray="3 3" />
                  <XAxis dataKey="label" tick={AXIS} />
                  <YAxis tick={AXIS} allowDecimals={false} />
                  <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f", borderRadius: 8, color: "white" }} />
                  <Line type="monotone" dataKey="target" name="Target" stroke={GOLD} strokeWidth={1.75} strokeDasharray="4 3" dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="actual" name="Actual" stroke={TEAL} strokeWidth={2.25} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </ChartCard>
          )}

          {/* Entry form */}
          <div className="no-print">
            <h2 className="text-sm font-semibold text-grey uppercase tracking-wide mb-2">
              {editingId ? "Edit Record" : "Add New Record"}
            </h2>
            <form onSubmit={submit} className="card p-4 mb-6 grid grid-cols-2 md:grid-cols-3 gap-3">
              {tracker.fields.map((f) => (
                <div key={f.name} className="flex flex-col gap-1">
                  <label className="text-xs text-grey">{f.label}{f.required ? " *" : ""}</label>
                  {f.type === "select" || f.type === "department" ? (
                    <select required={f.required} value={(form[f.name] as string) || ""} onChange={(e) => update(f.name, e.target.value)}>
                      <option value="">—</option>
                      {(f.type === "department" ? DEPARTMENTS : f.options || []).map((o) => (
                        <option key={o} value={o}>{o}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      type={f.type === "date" ? "date" : f.type === "number" ? "number" : "text"}
                      required={f.required}
                      value={(form[f.name] as string) ?? ""}
                      onChange={(e) => update(f.name, e.target.value)}
                    />
                  )}
                </div>
              ))}
              <div className="col-span-2 md:col-span-3 flex items-center gap-3 mt-2">
                <button type="submit" disabled={saving} className="bg-teal text-[#0b1220] font-semibold px-4 py-2 rounded-md disabled:opacity-50">
                  {saving ? "Saving…" : editingId ? "Update record" : "Add record"}
                </button>
                {editingId && (
                  <button type="button" onClick={() => { setEditingId(null); setForm({}); }} className="text-grey px-4 py-2 rounded-md border border-border">
                    Cancel
                  </button>
                )}
                {message && <span className="text-sm text-grey">{message}</span>}
              </div>
            </form>
          </div>

          {/* Data table */}
          <div className="card p-4">
            <div className="text-sm font-semibold mb-3">Records ({rows.length})</div>
            {rows.length === 0 ? (
              <p className="text-grey text-sm">No records yet.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr>
                      {tracker.fields.map((f) => <th key={f.name} className="text-left p-2 text-grey whitespace-nowrap">{f.label}</th>)}
                      <th className="p-2 no-print"></th>
                    </tr>
                  </thead>
                  <tbody>
                    {rows.map((row) => (
                      <tr key={String(row.id)} className="border-t border-border">
                        {tracker.fields.map((f) => (
                          <td key={f.name} className="p-2 whitespace-nowrap">
                            {f.type === "date" && row[f.name] ? String(row[f.name]).slice(0, 10) : String(row[f.name] ?? "")}
                          </td>
                        ))}
                        <td className="p-2 whitespace-nowrap no-print">
                          <button onClick={() => startEdit(row)} className={`mr-3 ${accentClass.teal}`}>Edit</button>
                          <button onClick={() => remove(Number(row.id))} className={accentClass.coral}>Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </>
      )}
    </div>
  );
}
