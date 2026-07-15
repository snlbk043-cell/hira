"use client";
import { useState } from "react";
import {
  ResponsiveContainer, AreaChart, Area, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar,
} from "recharts";
import Filters from "@/components/Filters";
import KpiCard from "@/components/KpiCard";
import ChartCard from "@/components/ChartCard";
import Gauge from "@/components/Gauge";
import { useSummary } from "@/lib/useSummary";
import { MONTHS } from "@/lib/types";

const TEAL = "#14b8a6", GOLD = "#f5a524", CORAL = "#f0625a", PURPLE = "#8b5cf6", BLUE = "#0b6ea8";
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
const RAG_PILL: Record<string, string> = {
  "🟢 Green": "bg-teal/15 text-teal border border-teal/30",
  "🟡 Amber": "bg-gold/15 text-gold border border-gold/30",
  "🔴 Red": "bg-coral/15 text-coral border border-coral/30",
};

export default function ExecutiveDashboard() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [department, setDepartment] = useState("All");
  const [month, setMonth] = useState(0);
  const { data, loading, error } = useSummary(year, department, month);

  if (loading) return <div className="max-w-7xl mx-auto p-6 text-grey">Loading…</div>;
  if (error || !data) return <div className="max-w-7xl mx-auto p-6 text-coral">Failed to load: {error}</div>;

  const monthly = MONTHS.map((m, i) => ({
    month: m,
    incidents: data.monthlyIncidents[i],
    trir: data.trirMonthly[i],
    ltifr: data.ltifrMonthly[i],
    leading: data.leadingMonthly[i],
    lagging: data.laggingMonthly[i],
  }));

  const pyramidOrder = ["Fatality", "Lost Time Injury", "Restricted Work", "Medical Treatment", "First Aid", "Near Miss"];
  const pyramid = pyramidOrder.map((k) => ({ name: k, count: data.classificationCounts[k] || 0 }));
  const pyramidColors = [CORAL, "#b91c1c", "#ea580c", GOLD, "#c9a82a", TEAL];

  const rootCauses = Object.entries(data.rootCauseCounts).sort((a, b) => b[1] - a[1]).map(([name, count]) => ({ name, count }));

  const ratio = data.leadingMonthly.reduce((a, b) => a + b, 0) / Math.max(1, data.laggingMonthly.reduce((a, b) => a + b, 0));

  const radarData = [
    { metric: "Training", actual: data.training.pct, target: data.settings.training_target_pct ?? 95 },
    { metric: "Obs Closure", actual: data.obs.pct, target: data.settings.obs_closure_target_pct ?? 90 },
    { metric: "CA Closure", actual: data.ca.pct, target: data.settings.ca_closure_target_pct ?? 90 },
    { metric: "PTW Compliance", actual: data.ptw.pct, target: data.settings.ptw_compliance_target_pct ?? 95 },
    { metric: "JSA Approved", actual: data.jsa.pct, target: 90 },
    { metric: "Walkthroughs Done", actual: data.walk.pct, target: 85 },
  ];

  const settings = data.settings;
  function rag(actual: number, target: number, higherIsBetter = true) {
    const ok = higherIsBetter ? actual >= target : actual <= target;
    const amberBand = settings.amber_band ?? 0.8;
    const nearMiss = higherIsBetter ? actual >= target * amberBand : actual <= target / amberBand;
    return ok ? "🟢 Green" : nearMiss ? "🟡 Amber" : "🔴 Red";
  }
  const ragScorecard = [
    { metric: "TRIR", actual: data.TRIR, target: data.settings.trir_target ?? 1.0, status: rag(data.TRIR, data.settings.trir_target ?? 1.0, false) },
    { metric: "LTIFR", actual: data.LTIFR, target: data.settings.ltifr_target ?? 2.0, status: rag(data.LTIFR, data.settings.ltifr_target ?? 2.0, false) },
    { metric: "Training Compliance %", actual: data.training.pct, target: data.settings.training_target_pct ?? 95, status: rag(data.training.pct, data.settings.training_target_pct ?? 95) },
    { metric: "Obs Closure %", actual: data.obs.pct, target: data.settings.obs_closure_target_pct ?? 90, status: rag(data.obs.pct, data.settings.obs_closure_target_pct ?? 90) },
    { metric: "CA Closure %", actual: data.ca.pct, target: data.settings.ca_closure_target_pct ?? 90, status: rag(data.ca.pct, data.settings.ca_closure_target_pct ?? 90) },
    { metric: "PTW Compliance %", actual: data.ptw.pct, target: data.settings.ptw_compliance_target_pct ?? 95, status: rag(data.ptw.pct, data.settings.ptw_compliance_target_pct ?? 95) },
  ];

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">🏆 Executive Dashboard</h1>
      <p className="text-grey text-sm mb-4">All key safety indicators for {year}{department !== "All" ? ` · ${department}` : ""}</p>
      <Filters year={year} department={department} month={month} onYearChange={setYear} onDepartmentChange={setDepartment} onMonthChange={setMonth} />

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <KpiCard icon="⛑️" label="TRIR" value={data.TRIR} sub={`Target ≤ ${data.settings.trir_target ?? 1.0}`} accent="coral" />
        <KpiCard icon="🚑" label="LTIFR" value={data.LTIFR} sub={`Target ≤ ${data.settings.ltifr_target ?? 2.0}`} accent="coral" />
        <KpiCard icon="⚠️" label="Total Incidents" value={data.totalIncidents} sub="This year" accent="gold" />
        <KpiCard icon="📅" label="Lost Days" value={data.lostDaysTotal} sub="This year" accent="coral" />
        <KpiCard icon="🎓" label="Training Compliance" value={`${data.training.pct}%`} sub={`Target ≥ ${data.settings.training_target_pct ?? 95}%`} accent="teal" />
        <KpiCard icon="👁️" label="Obs Closure" value={`${data.obs.pct}%`} sub={`Target ≥ ${data.settings.obs_closure_target_pct ?? 90}%`} accent="gold" />
        <KpiCard icon="🔧" label="CA Closure" value={`${data.ca.pct}%`} sub={`Target ≥ ${data.settings.ca_closure_target_pct ?? 90}%`} accent="purple" />
        <KpiCard icon="🛡️" label="Near Miss (leading)" value={data.classificationCounts["Near Miss"] || 0} sub="Higher = healthier culture" accent="teal" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Incident Severity Pyramid (Heinrich)">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={pyramid} layout="vertical" margin={{ left: 30 }}>
              <CartesianGrid stroke={GRID} horizontal={false} />
              <XAxis type="number" tick={AXIS} />
              <YAxis type="category" dataKey="name" tick={AXIS} width={130} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" radius={[0, 4, 4, 0]}>
                {pyramid.map((_, i) => <Cell key={i} fill={pyramidColors[i]} />)}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Incident Classification Mix">
          <ResponsiveContainer width="100%" height={260}>
            <PieChart>
              <Pie data={pyramid} dataKey="count" nameKey="name" innerRadius={55} outerRadius={90} paddingAngle={2}>
                {pyramid.map((_, i) => <Cell key={i} fill={pyramidColors[i]} />)}
              </Pie>
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <ChartCard title="TRIR & LTIFR Trend">
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={monthly}>
              <defs>
                <linearGradient id="trirFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={CORAL} stopOpacity={0.35} />
                  <stop offset="100%" stopColor={CORAL} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="ltifrFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={GOLD} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={GOLD} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={AXIS} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ stroke: GRID, strokeWidth: 1 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              <Area type="monotone" dataKey="trir" name="TRIR" stroke={CORAL} strokeWidth={2.25} fill="url(#trirFill)" dot={{ r: 3, fill: CORAL, strokeWidth: 0 }} activeDot={{ r: 5 }} />
              <Area type="monotone" dataKey="ltifr" name="LTIFR" stroke={GOLD} strokeWidth={2.25} fill="url(#ltifrFill)" dot={{ r: 3, fill: GOLD, strokeWidth: 0 }} activeDot={{ r: 5 }} />
            </AreaChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Leading vs Lagging Activity">
          <ResponsiveContainer width="100%" height={240}>
            <AreaChart data={monthly}>
              <defs>
                <linearGradient id="leadingFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={TEAL} stopOpacity={0.4} />
                  <stop offset="100%" stopColor={TEAL} stopOpacity={0} />
                </linearGradient>
                <linearGradient id="laggingFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor={CORAL} stopOpacity={0.3} />
                  <stop offset="100%" stopColor={CORAL} stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid stroke={GRID} strokeDasharray="3 3" vertical={false} />
              <XAxis dataKey="month" tick={AXIS} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={{ stroke: GRID, strokeWidth: 1 }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              <Area type="monotone" dataKey="leading" name="Leading" stroke={TEAL} strokeWidth={2.25} fill="url(#leadingFill)" dot={{ r: 3, fill: TEAL, strokeWidth: 0 }} activeDot={{ r: 5 }} />
              <Area type="monotone" dataKey="lagging" name="Lagging (Incidents)" stroke={CORAL} strokeWidth={2.25} fill="url(#laggingFill)" dot={{ r: 3, fill: CORAL, strokeWidth: 0 }} activeDot={{ r: 5 }} />
            </AreaChart>
          </ResponsiveContainer>
          <p className="text-xs text-grey mt-2">
            Leading:Lagging ratio this year: <span className="text-teal font-semibold">{ratio.toFixed(1)}:1</span>
          </p>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <ChartCard title="Compliance Profile — Actual vs Target (spider chart)">
          <ResponsiveContainer width="100%" height={300}>
            <RadarChart data={radarData} outerRadius="75%">
              <PolarGrid stroke={GRID} />
              <PolarAngleAxis dataKey="metric" tick={{ fill: "#94a3b8", fontSize: 10 }} />
              <PolarRadiusAxis domain={[0, 100]} tickCount={5} tick={{ fill: "#94a3b8", fontSize: 9 }} />
              <Radar name="Actual" dataKey="actual" stroke={TEAL} fill={TEAL} fillOpacity={0.35} />
              <Radar name="Target" dataKey="target" stroke={CORAL} fill={CORAL} fillOpacity={0.08} strokeDasharray="4 3" />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              <Tooltip contentStyle={TOOLTIP_STYLE} />
            </RadarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Root Cause Pareto">
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={rootCauses}>
              <CartesianGrid stroke={GRID} />
              <XAxis dataKey="name" tick={{ ...AXIS, fontSize: 9 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" fill={CORAL} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <ChartCard title="Monthly Incident Volume">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={monthly}>
              <CartesianGrid stroke={GRID} />
              <XAxis dataKey="month" tick={AXIS} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="incidents" fill={BLUE} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Body Part Distribution">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={Object.entries(data.bodyPartCounts).map(([name, count]) => ({ name, count }))} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={GRID} horizontal={false} />
              <XAxis type="number" tick={AXIS} allowDecimals={false} />
              <YAxis type="category" dataKey="name" tick={AXIS} width={90} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" fill={PURPLE} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <ChartCard title="Compliance Gauges — cross-tracker leading vs lagging" className="mb-4">
        <div className="grid grid-cols-2 md:grid-cols-5 gap-2 mt-2">
          <Gauge value={data.training.pct} label="Training Compliance" color={TEAL} />
          <Gauge value={data.obs.pct} label="Obs Closure" color={GOLD} />
          <Gauge value={data.ca.pct} label="CA Closure" color={PURPLE} />
          <Gauge value={data.ptw.pct} label="PTW Compliance" color={BLUE} />
          <Gauge value={data.jsa.pct} label="JSA Approved" color={TEAL} />
        </div>
      </ChartCard>

      <ChartCard title="RAG Compliance Scorecard" className="mb-4">
        <div className="overflow-x-auto mt-1">
          <table className="w-full text-sm">
            <thead>
              <tr>
                <th className="text-left p-2 text-grey">Metric</th>
                <th className="text-right p-2 text-grey">Actual</th>
                <th className="text-right p-2 text-grey">Target</th>
                <th className="text-center p-2 text-grey">Status</th>
              </tr>
            </thead>
            <tbody>
              {ragScorecard.map((r) => (
                <tr key={r.metric} className="border-t border-border">
                  <td className="p-2">{r.metric}</td>
                  <td className="p-2 text-right font-semibold">{r.actual}</td>
                  <td className="p-2 text-right text-grey">{r.target}</td>
                  <td className="p-2 text-center">
                    <span className={`inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold ${RAG_PILL[r.status]}`}>{r.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </ChartCard>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-4">
        <ChartCard title="Top 10 Unsafe Acts">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.top10UnsafeActs.map((d) => ({ name: d.label, count: d.value }))} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={GRID} horizontal={false} />
              <XAxis type="number" tick={AXIS} allowDecimals={false} />
              <YAxis type="category" dataKey="name" tick={{ ...AXIS, fontSize: 9 }} width={110} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" fill={GOLD} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Top 10 Unsafe Conditions">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.top10UnsafeConditions.map((d) => ({ name: d.label, count: d.value }))} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={GRID} horizontal={false} />
              <XAxis type="number" tick={AXIS} allowDecimals={false} />
              <YAxis type="category" dataKey="name" tick={{ ...AXIS, fontSize: 9 }} width={110} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" fill={BLUE} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Top 10 High-Risk Areas">
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={data.top10Areas.map((d) => ({ name: d.label, count: d.value }))} layout="vertical" margin={{ left: 20 }}>
              <CartesianGrid stroke={GRID} horizontal={false} />
              <XAxis type="number" tick={AXIS} allowDecimals={false} />
              <YAxis type="category" dataKey="name" tick={{ ...AXIS, fontSize: 9 }} width={110} />
              <Tooltip contentStyle={TOOLTIP_STYLE} cursor={TOOLTIP_CURSOR} />
              <Bar dataKey="count" fill={CORAL} radius={[0, 4, 4, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
        <KpiCard icon="💰" label="Est. Lost-Day Cost" value={`₹${data.costImpact.lostDayCost.toLocaleString()}`} sub="Incident lost days × rate" accent="coral" />
        <KpiCard icon="⏱️" label="Est. Downtime Cost" value={`₹${data.costImpact.downtimeCost.toLocaleString()}`} sub={`${data.costImpact.downtimeMinTotal} min total`} accent="gold" />
      </div>
    </div>
  );
}
