"use client";
import { useEffect, useState } from "react";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Cell,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from "recharts";
import Filters from "@/components/Filters";
import KpiCard from "@/components/KpiCard";
import ChartCard from "@/components/ChartCard";
import { useSummary } from "@/lib/useSummary";

const TEAL = "#14b8a6", CORAL = "#f0625a", GOLD = "#f5a524";
const AXIS = { stroke: "#94a3b8", fontSize: 11 };
const GRID = "#22314f";

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
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
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

      <ChartCard title="System Health — RAG status of all 25 trackers (spider chart)" className="mb-4">
        {health ? (
          <ResponsiveContainer width="100%" height={420}>
            <RadarChart data={health} outerRadius="75%">
              <PolarGrid stroke={GRID} />
              <PolarAngleAxis dataKey="label" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 2]} tickCount={3} tick={{ fill: "#94a3b8", fontSize: 9 }} />
              <Radar name="Health" dataKey="score" stroke={TEAL} fill={TEAL} fillOpacity={0.35} />
              <Tooltip
                contentStyle={{ background: "#111c33", border: "1px solid #22314f", borderRadius: 8, color: "white" }}
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
