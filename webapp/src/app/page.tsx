import Link from "next/link";

const tiles = [
  { href: "/dashboard/executive", label: "🏆 Executive Dashboard", accent: "border-teal", desc: "KPI wall, trends, pyramid, Pareto" },
  { href: "/dashboard/leadership", label: "🧭 Leadership Review", accent: "border-coral", desc: "Department league table, backlog, insights" },
];

const entries = [
  { href: "/entry/incidents", label: "🔥 Incidents" },
  { href: "/entry/training", label: "🎓 Training" },
  { href: "/entry/observations", label: "👁️ HSE Observations" },
  { href: "/entry/inspections", label: "🔍 Inspections" },
  { href: "/entry/walkthroughs", label: "🚶 Safety Walkthroughs" },
  { href: "/entry/corrective-actions", label: "🔧 Corrective Actions" },
  { href: "/entry/ptw-audits", label: "📝 PTW Audits" },
  { href: "/entry/risk-assessments", label: "⚠️ Risk Assessments (JSA)" },
];

export default function Home() {
  return (
    <div className="max-w-5xl mx-auto p-6">
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

      <h2 className="text-lg font-semibold mb-3">Enter Data</h2>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        {entries.map((e) => (
          <Link key={e.href} href={e.href} className="card p-4 text-sm text-center hover:bg-card-2 transition-colors">
            {e.label}
          </Link>
        ))}
      </div>

      <div className="card p-4 mt-8 text-sm text-grey">
        Fully dynamic: every KPI and chart recalculates automatically from what you enter. Set your man-hours &
        targets on the <Link href="/settings" className="text-teal">Settings</Link> page first for accurate TRIR/LTIFR.
      </div>
    </div>
  );
}
