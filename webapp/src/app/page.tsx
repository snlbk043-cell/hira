import Link from "next/link";
import { TRACKERS } from "@/lib/trackers";

const tiles = [
  { href: "/dashboard/executive", label: "🏆 Executive Dashboard", accent: "border-teal", desc: "KPI wall, trends, pyramid, Pareto" },
  { href: "/dashboard/leadership", label: "🧭 Leadership Review", accent: "border-coral", desc: "Department league table, backlog, insights" },
];

export default function Home() {
  return (
    <div className="max-w-6xl mx-auto p-6">
      <h1 className="text-3xl font-bold text-center mt-6 mb-2">RCPL INTEGRATED SAFETY DASHBOARD</h1>
      <p className="text-grey text-center mb-8">Reliance Consumer Products Ltd · Campa Cola CSD Plant</p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-8">
        {tiles.map((t) => (
          <Link key={t.href} href={t.href} className={`card p-6 border-l-4 ${t.accent} hover:bg-card-2 transition-colors`}>
            <div className="text-lg font-semibold">{t.label}</div>
            <div className="text-sm text-grey mt-1">{t.desc}</div>
          </Link>
        ))}
      </div>

      <h2 className="text-lg font-semibold mb-1">All 25 Trackers</h2>
      <p className="text-grey text-sm mb-3">Same list as the left sidebar — click any tracker for its KPI cards, trend charts and data entry form on one page.</p>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {TRACKERS.map((t) => (
          <Link key={t.key} href={`/tracker/${t.key}`} className="card p-4 text-sm text-center hover:bg-card-2 transition-colors">
            {t.icon} {t.label}
          </Link>
        ))}
      </div>

      <div className="card p-4 mt-8 text-sm text-grey">
        Fully dynamic: every KPI and chart recalculates automatically from what you enter — no page reload. Set your
        man-hours &amp; targets on the <Link href="/settings" className="text-teal">Settings</Link> page first for
        accurate TRIR/LTIFR. Every tracker page can export its current view to PDF, PPT or Excel.
      </div>
    </div>
  );
}
