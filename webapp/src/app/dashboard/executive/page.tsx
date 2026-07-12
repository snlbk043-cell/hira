"use client";
import { useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, BarChart, Bar, PieChart, Pie, Cell,
  XAxis, YAxis, CartesianGrid, Tooltip, Legend,
} from "recharts";
import Filters from "@/components/Filters";
import KpiCard from "@/components/KpiCard";
import ChartCard from "@/components/ChartCard";
import { useSummary } from "@/lib/useSummary";
import { MONTHS } from "@/lib/types";

const TEAL = "#14b8a6", GOLD = "#f5a524", CORAL = "#f0625a", PURPLE = "#8b5cf6", BLUE = "#0b6ea8";
const AXIS = { stroke: "#94a3b8", fontSize: 11 };
const GRID = "#22314f";

export default function ExecutiveDashboard() {
  const [year, setYear] = useState(new Date().getFullYear());
  const [department, setDepartment] = useState("All");
  const { data, loading, error } = useSummary(year, department);

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

  return (
    <div className="max-w-7xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">🧭 Executive Dashboard</h1>
      <p className="text-grey text-sm mb-4">All key safety indicators for {year}{department !== "All" ? ` · ${department}` : ""}</p>
      <Filters year={year} department={department} onYearChange={setYear} onDepartmentChange={setDepartment} />

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
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
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
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
            </PieChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-4">
        <ChartCard title="TRIR & LTIFR Trend">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={monthly}>
              <CartesianGrid stroke={GRID} />
              <XAxis dataKey="month" tick={AXIS} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              <Line type="monotone" dataKey="trir" name="TRIR" stroke={CORAL} strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="ltifr" name="LTIFR" stroke={GOLD} strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Leading vs Lagging Activity">
          <ResponsiveContainer width="100%" height={240}>
            <LineChart data={monthly}>
              <CartesianGrid stroke={GRID} />
              <XAxis dataKey="month" tick={AXIS} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
              <Legend wrapperStyle={{ fontSize: 11, color: "#94a3b8" }} />
              <Line type="monotone" dataKey="leading" name="Leading" stroke={TEAL} strokeWidth={2} dot={{ r: 3 }} />
              <Line type="monotone" dataKey="lagging" name="Lagging (Incidents)" stroke={CORAL} strokeWidth={2} dot={{ r: 3 }} />
            </LineChart>
          </ResponsiveContainer>
          <p className="text-xs text-grey mt-2">
            Leading:Lagging ratio this year: <span className="text-teal font-semibold">{ratio.toFixed(1)}:1</span>
          </p>
        </ChartCard>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4 mb-6">
        <ChartCard title="Root Cause Pareto">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={rootCauses}>
              <CartesianGrid stroke={GRID} />
              <XAxis dataKey="name" tick={{ ...AXIS, fontSize: 9 }} interval={0} angle={-25} textAnchor="end" height={70} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
              <Bar dataKey="count" fill={CORAL} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
        <ChartCard title="Monthly Incident Volume">
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={monthly}>
              <CartesianGrid stroke={GRID} />
              <XAxis dataKey="month" tick={AXIS} />
              <YAxis tick={AXIS} />
              <Tooltip contentStyle={{ background: "#111c33", border: "1px solid #22314f" }} />
              <Bar dataKey="incidents" fill={BLUE} radius={[4, 4, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </ChartCard>
      </div>
    </div>
  );
}
