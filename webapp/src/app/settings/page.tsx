"use client";
import { useEffect, useState } from "react";
import { MONTH_NAMES } from "@/lib/constants";

const SETTINGS_LABELS: Record<string, string> = {
  trir_target: "TRIR Target (max acceptable)",
  ltifr_target: "LTIFR Target (max acceptable)",
  training_target_pct: "Training Compliance Target %",
  obs_closure_target_pct: "Obs Closure Target %",
  ca_closure_target_pct: "CA Closure Target %",
  ptw_compliance_target_pct: "PTW Compliance Target %",
  amber_band: "RAG Amber Band (fraction of target)",
  trir_multiplier: "TRIR Multiplier (OSHA standard)",
  ltifr_multiplier: "LTIFR Multiplier (per million man-hours)",
  industry_benchmark_trir: "Industry Benchmark TRIR",
  industry_benchmark_ltifr: "Industry Benchmark LTIFR",
};

const COST_LABELS: Record<string, string> = {
  cost_per_lost_day: "Lost-Day Cost per Day (₹)",
  cost_per_downtime_min: "Downtime Cost per Minute (₹)",
};

const PRIOR_YEAR_LABELS: Record<string, string> = {
  py_trir: "Prior Year TRIR",
  py_ltifr: "Prior Year LTIFR",
  py_total_incidents: "Prior Year Total Incidents",
  py_training_pct: "Prior Year Training Compliance %",
  py_obs_pct: "Prior Year Obs Closure %",
  py_ca_pct: "Prior Year CA Closure %",
};

export default function SettingsPage() {
  const [settings, setSettings] = useState<Record<string, string>>({});
  const [year, setYear] = useState(new Date().getFullYear());
  const [manhours, setManhours] = useState<number[]>(new Array(12).fill(0));
  const [message, setMessage] = useState<string | null>(null);
  const [clearing, setClearing] = useState(false);
  const [clearResult, setClearResult] = useState<string | null>(null);

  async function clearAllData() {
    if (!confirm("This permanently deletes every record in all 25 trackers. This cannot be undone. Continue?")) return;
    setClearing(true);
    setClearResult(null);
    try {
      const res = await fetch("/api/admin/clear-data", { method: "POST" });
      const json = await res.json();
      setClearResult(`Cleared ${Object.keys(json.results).length} tables.`);
    } catch (e) {
      setClearResult(String(e));
    } finally {
      setClearing(false);
    }
  }

  useEffect(() => {
    fetch("/api/settings").then((r) => r.json()).then(setSettings);
  }, []);

  useEffect(() => {
    fetch(`/api/manhours?year=${year}`)
      .then((r) => r.json())
      .then((rows: { month: number; hours: number }[]) => {
        const arr = new Array(12).fill(0);
        for (const r of rows) arr[r.month - 1] = Number(r.hours);
        setManhours(arr);
      });
  }, [year]);

  async function saveSettings() {
    await fetch("/api/settings", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(settings),
    });
    setMessage("Settings saved.");
  }

  async function saveManhours(monthIdx: number) {
    await fetch("/api/manhours", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ year, month: monthIdx + 1, hours: manhours[monthIdx] }),
    });
  }

  return (
    <div className="max-w-4xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">⚙️ Settings</h1>
      <p className="text-grey text-sm mb-4">Targets, multipliers and monthly man-hours used across both dashboards.</p>

      <div className="card p-4 mb-6">
        <div className="text-sm font-semibold mb-3">Targets & Benchmarks</div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(SETTINGS_LABELS).map(([key, label]) => (
            <div key={key} className="flex flex-col gap-1">
              <label className="text-xs text-grey">{label}</label>
              <input
                type="number"
                step="any"
                value={settings[key] ?? ""}
                onChange={(e) => setSettings((s) => ({ ...s, [key]: e.target.value }))}
              />
            </div>
          ))}
        </div>
        <button onClick={saveSettings} className="mt-4 bg-teal text-[#0b1220] font-semibold px-4 py-2 rounded-md">
          Save Settings
        </button>
        {message && <span className="ml-3 text-sm text-grey">{message}</span>}
      </div>

      <div className="card p-4 mb-6">
        <div className="text-sm font-semibold mb-1">Cost Parameters</div>
        <p className="text-xs text-grey mb-3">Used only by the optional cost-impact tiles on the Executive Dashboard.</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(COST_LABELS).map(([key, label]) => (
            <div key={key} className="flex flex-col gap-1">
              <label className="text-xs text-grey">{label}</label>
              <input type="number" step="any" value={settings[key] ?? ""} onChange={(e) => setSettings((s) => ({ ...s, [key]: e.target.value }))} />
            </div>
          ))}
        </div>
        <button onClick={saveSettings} className="mt-4 bg-teal text-[#0b1220] font-semibold px-4 py-2 rounded-md">Save Settings</button>
      </div>

      <div className="card p-4 mb-6">
        <div className="text-sm font-semibold mb-1">Prior Year Actuals</div>
        <p className="text-xs text-grey mb-3">
          Type in last year&apos;s year-end figures for a genuine YoY comparison on Leadership Review — left at 0 (and
          hidden from the comparison) until you enter real numbers.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {Object.entries(PRIOR_YEAR_LABELS).map(([key, label]) => (
            <div key={key} className="flex flex-col gap-1">
              <label className="text-xs text-grey">{label}</label>
              <input type="number" step="any" value={settings[key] ?? ""} onChange={(e) => setSettings((s) => ({ ...s, [key]: e.target.value }))} />
            </div>
          ))}
        </div>
        <button onClick={saveSettings} className="mt-4 bg-teal text-[#0b1220] font-semibold px-4 py-2 rounded-md">Save Settings</button>
      </div>

      <div className="card p-4">
        <div className="flex items-center justify-between mb-3">
          <div className="text-sm font-semibold">Monthly Man-Hours (plant-wide)</div>
          <select value={year} onChange={(e) => setYear(Number(e.target.value))}>
            {[year - 1, year, year + 1].map((y) => <option key={y} value={y}>{y}</option>)}
          </select>
        </div>
        <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
          {MONTH_NAMES.map((m, i) => (
            <div key={m} className="flex flex-col gap-1">
              <label className="text-xs text-grey">{m}</label>
              <input
                type="number"
                value={manhours[i]}
                onChange={(e) => setManhours((arr) => arr.map((v, idx) => (idx === i ? Number(e.target.value) : v)))}
                onBlur={() => saveManhours(i)}
              />
            </div>
          ))}
        </div>
        <p className="text-xs text-grey mt-3">Saved automatically when you leave a field (used for TRIR/LTIFR calculation).</p>
      </div>

      <div className="card p-4 mt-6 border-l-4 border-coral">
        <div className="text-sm font-semibold mb-2 text-coral">⚠️ Danger Zone</div>
        <p className="text-xs text-grey mb-3">
          Permanently deletes every record in all 25 trackers (does not touch Settings or man-hours). Use this once
          to clear demo/sample data before your team starts entering real records. Cannot be undone.
        </p>
        <button onClick={clearAllData} disabled={clearing} className="bg-coral text-[#0b1220] font-semibold px-4 py-2 rounded-md disabled:opacity-50">
          {clearing ? "Clearing…" : "Clear All Tracker Data"}
        </button>
        {clearResult && <span className="ml-3 text-sm text-grey">{clearResult}</span>}
      </div>
    </div>
  );
}
