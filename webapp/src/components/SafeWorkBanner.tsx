import { Summary } from "@/lib/types";

function StreakStat({ icon, label, value, sub, accent }: { icon: string; label: string; value: string; sub?: string; accent: string }) {
  return (
    <div className="flex-1 min-w-[140px] text-center px-3 py-2">
      <div className="text-2xl mb-1">{icon}</div>
      <div className="text-3xl md:text-4xl font-extrabold tracking-tight" style={{ color: accent, textShadow: `0 0 22px ${accent}55` }}>
        {value}
      </div>
      <div className="text-xs text-grey uppercase tracking-wide mt-1">{label}</div>
      {sub && <div className="text-[11px] text-grey mt-0.5">{sub}</div>}
    </div>
  );
}

export default function SafeWorkBanner({ data }: { data: Summary }) {
  const sw = data.safeWork;
  const noRecordable = sw.safeDaysRecordable === null;
  const accent = noRecordable ? "#14b8a6" : sw.safeDaysRecordable! >= 30 ? "#14b8a6" : sw.safeDaysRecordable! >= 7 ? "#f5a524" : "#f0625a";

  const deptRows = Object.entries(sw.byDepartment)
    .sort((a, b) => (a[1].safeDays ?? 1e9) - (b[1].safeDays ?? 1e9))
    .slice(0, 6);

  return (
    <div
      className="card relative overflow-hidden p-4 mb-4"
      style={{ borderColor: `${accent}40`, boxShadow: `0 0 0 1px ${accent}25, 0 20px 50px -30px ${accent}80` }}
    >
      <div className="pointer-events-none absolute -right-10 -top-10 w-56 h-56 rounded-full opacity-15 blur-3xl" style={{ background: accent }} />
      <div className="relative flex items-center gap-2 mb-2">
        <span className="w-1.5 h-1.5 rounded-full" style={{ background: accent, boxShadow: `0 0 8px 2px ${accent}` }} />
        <div className="text-sm font-semibold text-white tracking-wide">Safe Work Man-Days &amp; Man-Hours</div>
      </div>
      <div className="relative flex flex-wrap divide-x divide-border">
        <StreakStat
          icon="🛡️"
          label="Days Since Last Recordable"
          value={noRecordable ? "—" : String(sw.safeDaysRecordable)}
          sub={noRecordable ? "No recordable incidents on record" : `Last: ${sw.lastRecordableDate}`}
          accent={accent}
        />
        <StreakStat
          icon="⏱️"
          label="Est. Safe Man-Hours"
          value={sw.safeManHoursRecordable !== null ? sw.safeManHoursRecordable.toLocaleString() : "—"}
          sub="Estimated from monthly man-hours"
          accent={accent}
        />
        <StreakStat
          icon="🏆"
          label="Best-Ever Streak"
          value={sw.bestStreakRecordableDays !== null ? `${sw.bestStreakRecordableDays}d` : "—"}
          sub="Longest gap between recordables"
          accent="#f5a524"
        />
        <StreakStat
          icon="🚑"
          label="Days Since Last LTI"
          value={sw.safeDaysLti !== null ? String(sw.safeDaysLti) : "—"}
          sub={sw.lastLtiDate ? `Last: ${sw.lastLtiDate}` : "No LTI on record"}
          accent={sw.safeDaysLti === null ? "#14b8a6" : sw.safeDaysLti >= 90 ? "#14b8a6" : sw.safeDaysLti >= 30 ? "#f5a524" : "#f0625a"}
        />
      </div>
      {deptRows.length > 0 && (
        <div className="relative mt-3 pt-3 border-t border-border">
          <div className="text-[11px] text-grey uppercase tracking-wide mb-2">Department Watchlist — lowest safe-days first</div>
          <div className="flex flex-wrap gap-2">
            {deptRows.map(([dept, v]) => {
              const c = v.safeDays === null ? "#14b8a6" : v.safeDays >= 30 ? "#14b8a6" : v.safeDays >= 7 ? "#f5a524" : "#f0625a";
              return (
                <span key={dept} className="text-xs px-2.5 py-1 rounded-full border" style={{ borderColor: `${c}50`, color: c, background: `${c}15` }}>
                  {dept}: {v.safeDays}d
                </span>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
}
