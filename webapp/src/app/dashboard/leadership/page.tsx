"use client";
import { useEffect, useState } from "react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
  AreaChart, Area,
} from "recharts";
import Filters from "@/components/Filters";
import KpiCard from "@/components/KpiCard";
import ChartCard from "@/components/ChartCard";
import SafeWorkBanner from "@/components/SafeWorkBanner";
import { useSummary } from "@/lib/useSummary";
import { TRACKERS, natureOf } from "@/lib/trackers";

const TEAL = "#14b8a6", CORAL = "#f0625a", GOLD = "#f5a524";
const AXIS = { stroke: "#94a3b8", fontSize: 11 };
const GRID = "#22314f";
const TOOLTIP_STYLE = {
  background: "rgba(17,28,51,0.96)",
  border: "1px solid #22314f",
  borderRadius: 10,
  color: "white",
  boxShadow: "0 12px 28px -12px rgba(0,0,0,0.6)",
  backdropFilter: "blur(6px)",
};
const TOOLTIP_CURSOR = { fill: "rgba(148,163,184,0.06)" };

function scoreColor(score: number) {
  if (score >= 85) return TEAL;
  if (score >= 65) return GOLD;
  return CORAL;
}

function riskCellColor(n: number) {
  if (n === 0) return "#162440";
  if (n === 1) return "#4a3a14";
  if (n === 2) return "#8a5a18";
  return "#f0625a";
}

type HealthEntry = { label: string; icon: string; score: number; detail: string };
type ElementStat = { key: string; label: string; icon: string; memberCount: number; overall: number | null; monthly: (number | null)[]; deptScores: Record<string, number | null> };

export default function LeadershipDashboard() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [department, setDepartment] = useState("All");
  const [month, setMonth] = useState(0);
  const { data, loading, error } = useSummary(year, department, month);

  const [health, setHealth] = useState<HealthEntry[] | null>(null);
  useEffect(() => {
    fetch(`/api/health-summary?department=${encodeURIComponent(department)}`)
      .then((r) => r.json())
      .then((json) => setHealth(json.results));
  }, [department]);

  const [elements, setElements] = useState<ElementStat[] | null>(null);
  useEffect(() => {
    fetch(`/api/ehs-framework?year=${year}&department=${encodeURIComponent(department)}`)
      .then((r) => r.json())
      .then((json) => setElements(json.elements));
  }, [year, department]);

  if (loading) return <div className="max-w-7xl mx-auto p-6 text-grey">Loading…</div>;
  if (error || !data) return <div className="max-w-7xl mx-auto p-6 text-coral">Failed to load: {error}</div>;

  const deptSorted = Object.entries(data.deptScore).sort((a, b) => a[1] - b[1]);
  const worst = deptSorted[0];
  const best = deptSorted[deptSorted.length - 1];
  const totalBacklog = Object.values(data.backlog).reduce((a, b) => a + b, 0);
  const ratio = data.leadingMonthly.reduce((a, b) => a + b, 0) / Math.max(1, data.laggingMonthly.reduce((a, b) => a + b, 0));
  const topCause = Object.entries(data.rootCauseCounts).sort((a, b) => b[1] - a[1])[0];
  const levels = Object.keys(data.riskRatingByDept);
  const depts = Array.from(new Set(levels.flatMap((l) => Object.keys(data.riskRatingByDept[l]))));

  // Top Movers: period-over-period change, normalised so "higher = better" for every row
  function pctChange(cur: number, prev: number, goodDirection: "up" | "down") {
    if (prev === 0) return cur === 0 ? 0 : (goodDirection === "up" ? 1 : -1);
    const raw = (cur - prev) / prev;
    return goodDirection === "up" ? raw : -raw;
  }
  const movers = [
    { label: "Total Incidents", change: pctChange(data.totalIncidents, data.prior.totalIncidents, "down"), cur: data.totalIncidents, prev: data.prior.totalIncidents },
    { label: "Recordable", change: pctChange(data.recordableTotal, data.prior.recordableTotal, "down"), cur: data.recordableTotal, prev: data.prior.recordableTotal },
    { label: "Training Compliance %", change: pctChange(data.training.pct, data.prior.trainingPct, "up"), cur: data.training.pct, prev: data.prior.trainingPct },
    { label: "Obs Closure %", change: pctChange(data.obs.pct, data.prior.obsPct, "up"), cur: data.obs.pct, prev: data.prior.obsPct },
    { label: "CA Closure %", change: pctChange(data.ca.pct, data.prior.caPct, "up"), cur: data.ca.pct, prev: data.prior.caPct },
  ].sort((a, b) => b.change - a.change);
  const bestMovers = movers.slice(0, 3);
  const worstMovers = [...movers].reverse().slice(0, 3);

  // YoY: current YTD vs Settings' prior-year actuals (0 until the user fills them in)
  const yoy = [
    { label: "TRIR", cur: data.TRIR, py: data.settings.py_trir ?? 0 },
    { label: "LTIFR", cur: data.LTIFR, py: data.settings.py_ltifr ?? 0 },
    { label: "Total Incidents", cur: data.totalIncidents, py: data.settings.py_total_incidents ?? 0 },
    { label: "Training Compliance %", cur: data.training.pct, py: data.settings.py_training_pct ?? 0 },
    { label: "Obs Closure %", cur: data.obs.pct, py: data.settings.py_obs_pct ?? 0 },
    { label: "CA Closure %", cur: data.ca.pct, py: data.settings.py_ca_pct ?? 0 },
  ];

  const insights: string[] = [];
  insights.push(
    `TRIR is ${data.TRIR} and LTIFR is ${data.LTIFR} against targets of ≤${data.settings.trir_target ?? 1} and ≤${data.settings.ltifr_target ?? 2} — ${
      data.TRIR <= (data.settings.trir_target ?? 1) && data.LTIFR <= (data.settings.ltifr_target ?? 2) ? "within target" : "requires attention"
    }.`
  );
  if (worst) {
    insights.push(
      `${worst[0]} has the lowest department safety score (${worst[1]}/100) — recommend a focused review of training, observation-closure and CA-closure rates there.${
        best ? ` ${best[0]} leads at ${best[1]}/100.` : ""
      }`
    );
  }
  if (topCause) {
    insights.push(`"${topCause[0]}" is the leading root cause (${topCause[1]} incidents) — a targeted corrective-action campaign here would have outsized impact.`);
  }
  insights.push(`Leading:Lagging ratio is ${ratio.toFixed(1)}:1 this year across all tracked activity.`);
  if (totalBacklog > 0) {
    insights.push(`System-wide backlog: ${totalBacklog} overdue items across Corrective Actions, Observations, Inspections and Walkthroughs.`);
  }

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">🧭 Leadership Review</h1>
      <p className="text-grey text-sm mb-4">Corporate safety scorecard for {year}{department !== "All" ? ` · ${department}` : ""}</p>
      <Filters year={year} department={department} month={month} onYearChange={setYear} onDepartmentChange={setDepartment} onMonthChange={setMonth} />

      <SafeWorkBanner data={data} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <KpiCard icon="⛑️" label="TRIR" value={data.TRIR} accent="coral" />
        <KpiCard icon="🚑" label="LTIFR" value={data.LTIFR} accent="coral" />
        <KpiCard icon="📋" label="Recordable" value={data.recordableTotal} accent="gold" />
        <KpiCard icon="🗂️" label="System-Wide Backlog" value={totalBacklog} sub="Overdue items" accent="coral" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Department League Table (low → high)">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={deptSorted.map(([name, score]) => ({ name, score }))} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={GRID} horizontal={false} />
              <XAxis type="number" domain={[0, 100]} tick={AXIS} />
              <YAxis type="category" dataKey="name" tick={AXIS} width={100} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                {deptSorted.map(([, score], i) => <Cell key={i} fill={scoreColor(score)} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>

        <ChartCard title="System-Wide Action Backlog by Register">
          <div className="space-y-3 mt-2">
            {Object.entries(data.backlog).map(([k, v]) => (
              <div key={k} className="flex items-center justify-between">
                <span className="text-sm text-grey capitalize">{k.replace(/_/g, " ")}</span>
                <span className={`font-bold ${v > 0 ? "text-coral" : "text-teal"}`}>{v}</span>
              </div>
            ))}
          </div>
        </ChartCard>
      </div>

      <ChartCard title="Backlog Ageing (open overdue items, system-wide)" className="mb-4">
        <ResponsiveContainer width="100%" height={200}>
          <BarChart data={Object.entries(data.backlogAging).map(([bucket, count]) => ({ bucket, count }))}>
            <CartesianGrid stroke={GRID} />
            <XAxis dataKey="bucket" tick={AXIS} />
            <YAxis tick={AXIS} allowDecimals={false} />
            <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
            <Bar dataKey="count" radius={[4, 4, 0, 0]}>
              {Object.keys(data.backlogAging).map((bucket, i) => (
                <Cell key={i} fill={bucket === "0-7" ? TEAL : bucket === "8-15" ? GOLD : bucket === "16-30" ? "#f2994a" : CORAL} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </ChartCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <ChartCard title="🟢 Top Movers — Best Improvement (vs prior period)">
          <ul className="mt-2 space-y-2">
            {bestMovers.map((m) => (
              <li key={m.label} className="flex items-center justify-between text-sm border-l-2 border-teal pl-3 py-1">
                <span>{m.label}</span>
                <span className="text-teal font-semibold">{m.prev} → {m.cur}</span>
              </li>
            ))}
          </ul>
        </ChartCard>
        <ChartCard title="🔴 Top Movers — Biggest Regression (vs prior period)">
          <ul className="mt-2 space-y-2">
            {worstMovers.map((m) => (
              <li key={m.label} className="flex items-center justify-between text-sm border-l-2 border-coral pl-3 py-1">
                <span>{m.label}</span>
                <span className="text-coral font-semibold">{m.prev} → {m.cur}</span>
              </li>
            ))}
          </ul>
        </ChartCard>
      </div>

      <ChartCard title="Leading vs Lagging Indicators — all 25 trackers" className="mb-4">
        <p className="text-xs text-grey mb-3">
          Leading = proactive activity that prevents harm (training, inspections, audits, JSA, near-miss reporting…). Lagging = an
          outcome measured only after harm or a violation already occurred.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-teal" />
              <span className="text-sm font-semibold text-teal">Leading Indicators ({TRACKERS.filter((t) => natureOf(t) === "leading").length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {TRACKERS.filter((t) => natureOf(t) === "leading").map((t) => {
                const idx = TRACKERS.indexOf(t);
                const h = health?.[idx];
                return (
                  <span key={t.key} className="text-xs px-2.5 py-1 rounded-full bg-teal/10 border border-teal/25 text-white/90">
                    {t.icon} {t.label}{h ? <span className="text-grey"> · {h.detail}</span> : null}
                  </span>
                );
              })}
            </div>
          </div>
          <div>
            <div className="flex items-center gap-2 mb-2">
              <span className="w-2 h-2 rounded-full bg-coral" />
              <span className="text-sm font-semibold text-coral">Lagging Indicators ({TRACKERS.filter((t) => natureOf(t) === "lagging").length})</span>
            </div>
            <div className="flex flex-wrap gap-1.5">
              {TRACKERS.filter((t) => natureOf(t) === "lagging").map((t) => {
                const idx = TRACKERS.indexOf(t);
                const h = health?.[idx];
                return (
                  <span key={t.key} className="text-xs px-2.5 py-1 rounded-full bg-coral/10 border border-coral/25 text-white/90">
                    {t.icon} {t.label}{h ? <span className="text-grey"> · {h.detail}</span> : null}
                  </span>
                );
              })}
            </div>
            <p className="text-xs text-grey mt-3">
              Leading:Lagging activity ratio this year: <span className="text-teal font-semibold">{ratio.toFixed(1)}:1</span>
            </p>
          </div>
        </div>
      </ChartCard>

      <ChartCard title="EHS Framework — Elemental Score &amp; Trend" className="mb-4">
        <p className="text-xs text-grey mb-3">Every tracker rolled up into 7 EHS management-system elements, scored 0-100 and trended across {year}.</p>
        {elements ? (
          <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-3">
            {elements.map((el) => {
              const c = el.overall === null ? "#475569" : scoreColor(el.overall);
              const trendData = el.monthly.map((v, i) => ({ m: i, v }));
              return (
                <div key={el.key} className="card p-3" style={{ borderLeft: `3px solid ${c}` }}>
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 min-w-0">
                      <span className="text-lg shrink-0">{el.icon}</span>
                      <div className="min-w-0">
                        <div className="text-xs font-semibold text-white truncate">{el.label}</div>
                        <div className="text-[10px] text-grey">{el.memberCount} tracker{el.memberCount > 1 ? "s" : ""}</div>
                      </div>
                    </div>
                    <div className="text-xl font-extrabold shrink-0" style={{ color: c }}>{el.overall ?? "—"}</div>
                  </div>
                  <ResponsiveContainer width="100%" height={44}>
                    <AreaChart data={trendData} margin={{ top: 4, right: 0, bottom: 0, left: 0 }}>
                      <defs>
                        <linearGradient id={`elFill-${el.key}`} x1="0" y1="0" x2="0" y2="1">
                          <stop offset="0%" stopColor={c} stopOpacity={0.45} />
                          <stop offset="100%" stopColor={c} stopOpacity={0} />
                        </linearGradient>
                      </defs>
                      <Area type="monotone" dataKey="v" stroke={c} strokeWidth={1.75} fill={`url(#elFill-${el.key})`} connectNulls dot={false} />
                    </AreaChart>
                  </ResponsiveContainer>
                </div>
              );
            })}
          </div>
        ) : (
          <p className="text-grey text-sm p-4">Loading framework scores…</p>
        )}
        {elements && (
          <div className="overflow-x-auto mt-4 pt-3 border-t border-border">
            <div className="text-[11px] text-grey uppercase tracking-wide mb-2">Department × Element Heatmap</div>
            <table className="w-full text-xs">
              <thead>
                <tr>
                  <th className="text-left p-1.5 text-grey sticky left-0 bg-card">Department</th>
                  {elements.map((el) => <th key={el.key} className="p-1.5 text-grey font-normal">{el.icon}</th>)}
                </tr>
              </thead>
              <tbody>
                {Array.from(new Set(elements.flatMap((el) => Object.keys(el.deptScores)))).map((dept) => (
                  <tr key={dept}>
                    <td className="p-1.5 font-semibold whitespace-nowrap sticky left-0 bg-card">{dept}</td>
                    {elements.map((el) => {
                      const v = el.deptScores[dept];
                      const c = v === null || v === undefined ? "rgba(148,163,184,0.05)" : scoreColor(v);
                      return (
                        <td key={el.key} className="p-1.5 text-center font-bold" style={{ background: v == null ? c : `${c}30`, color: v == null ? "#475569" : c }}>
                          {v ?? "·"}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </ChartCard>

      <ChartCard title="System Health — RAG status of all 25 trackers (spider chart)" className="mb-4">
        {health ? (
          <ResponsiveContainer width="100%" height={420}>
            <RadarChart data={health} outerRadius="75%">
              <PolarGrid stroke={GRID} />
              <PolarAngleAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 2]} tickCount={3} tick={{ fill: "#94a3b8", fontSize: 9 }} />
              <Radar name="Health" dataKey="score" stroke={TEAL} fill={TEAL} fillOpacity={0.35} />
              <Tooltip
                contentStyle={TOOLTIP_STYLE}
                formatter={(value, _name, item) => [`${item.payload.detail} (${value === 2 ? "Green" : value === 1 ? "Amber" : "Red"})`, item.payload.label]}
              />
            </RadarChart>
          </ResponsiveContainer>
        ) : (
          <p className="text-grey text-sm p-4">Loading health scores…</p>
        )}
      </ChartCard>

      <ChartCard title="Incident Risk Rating × Department (real data)" className="mb-4">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left p-2 text-grey">Risk \ Dept</th>
                {depts.map((d) => <th key={d} className="p-2 text-grey">{d}</th>)}
              </tr>
            </thead>
            <tbody>
              {levels.map((lvl) => (
                <tr key={lvl}>
                  <td className="p-2 font-semibold bg-card-2">{lvl}</td>
                  {depts.map((d) => {
                    const n = data.riskRatingByDept[lvl]?.[d] || 0;
                    return (
                      <td key={d} className="p-2 text-center font-bold" style={{ background: riskCellColor(n) }}>
                        {n}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ChartCard>

      <ChartCard title="Year-over-Year Comparison — current YTD vs prior year (set prior-year actuals on Settings)" className="mb-4">
        <div className="overflow-x-auto mt-1">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left p-2 text-grey">Metric</th>
                <th className="text-right p-2 text-grey">Current YTD</th>
                <th className="text-right p-2 text-grey">Prior Year</th>
                <th className="text-left p-2 text-grey w-36">Change</th>
                <th className="text-right p-2 text-grey">Δ vs Prior Year</th>
              </tr>
            </thead>
            <tbody>
              {yoy.map((r) => {
                const deltaPct = r.py === 0 ? 0 : ((r.cur - r.py) / r.py) * 100;
                const good = deltaPct <= 0;
                const magnitude = Math.min(100, Math.abs(deltaPct));
                return (
                  <tr key={r.label} className="border-t border-border">
                    <td className="p-2">{r.label}</td>
                    <td className="p-2 text-right font-semibold">{r.cur}</td>
                    <td className="p-2 text-right text-grey">{r.py}</td>
                    <td className="p-2">
                      {r.py === 0 ? (
                        <span className="text-grey text-xs">—</span>
                      ) : (
                        <div className="h-1.5 w-full rounded-full bg-card-2 overflow-hidden">
                          <div
                            className="h-full rounded-full"
                            style={{ width: `${magnitude}%`, background: good ? TEAL : CORAL }}
                          />
                        </div>
                      )}
                    </td>
                    <td className="p-2 text-right">
                      {r.py === 0 ? (
                        <span className="text-grey text-xs">(enter prior year data)</span>
                      ) : (
                        <span className={good ? "text-teal" : "text-coral"}>{deltaPct.toFixed(1)}%</span>
                      )}
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </ChartCard>

      <ChartCard title="Key Insights for Leadership">
        <ul className="space-y-2 mt-2">
          {insights.map((t, i) => (
            <li key={i} className="text-sm border-l-2 border-teal pl-3 py-1">{t}</li>
          ))}
        </ul>
      </ChartCard>
    </div>
  );
}
