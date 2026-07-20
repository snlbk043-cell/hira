"use client";
import ChartCard from "@/components/ChartCard";
import type { Row } from "@/lib/aggregate";

const MEDALS = ["🥇", "🥈", "🥉"];
const PLACE_LABEL = ["1st Place", "2nd Place", "3rd Place"];
const HEIGHT = ["h-32", "h-24", "h-16"];
const GLOW = ["shadow-[0_0_28px_rgba(245,165,36,0.55)]", "shadow-[0_0_20px_rgba(148,163,184,0.4)]", "shadow-[0_0_18px_rgba(240,98,90,0.35)]"];
const BG = ["bg-gradient-to-b from-[#f5a524] to-[#c47f0e]", "bg-gradient-to-b from-[#c9d3e0] to-[#8a97a8]", "bg-gradient-to-b from-[#d98a68] to-[#a45a3c]"];
const ORDER = [1, 0, 2]; // render 2nd, 1st, 3rd for a podium look

export default function SafetyAwardsPodium({ rows }: { rows: Row[] }) {
  const tally = new Map<string, number>();
  for (const r of rows) {
    if (String(r.status) !== "Presented") continue;
    const name = String(r.recipient || "").trim() || String(r.department || "").trim();
    if (!name) continue;
    tally.set(name, (tally.get(name) ?? 0) + 1);
  }
  const winners = [...tally.entries()].sort((a, b) => b[1] - a[1]).slice(0, 3);

  if (winners.length === 0) {
    return (
      <ChartCard title="🏆 Winners Podium" className="mb-6">
        <p className="text-grey text-sm mt-2">No presented awards yet in this period — add a record with status &quot;Presented&quot; to populate the podium.</p>
      </ChartCard>
    );
  }

  return (
    <ChartCard title="🏆 Winners Podium" className="mb-6">
      <div className="flex items-end justify-center gap-4 mt-6 mb-2 flex-wrap">
        {ORDER.filter((idx) => winners[idx]).map((idx) => {
          const [name, count] = winners[idx];
          return (
            <div key={idx} className="flex flex-col items-center gap-2 podium-rise" style={{ animationDelay: `${idx * 120}ms` }}>
              <div className="text-3xl podium-medal-bounce" style={{ animationDelay: `${300 + idx * 150}ms` }}>{MEDALS[idx]}</div>
              <div className="text-sm font-semibold text-center max-w-[120px] truncate" title={name}>{name}</div>
              <div className="text-xs text-grey">{count} award{count === 1 ? "" : "s"}</div>
              <div
                className={`w-24 sm:w-28 ${HEIGHT[idx]} ${BG[idx]} ${GLOW[idx]} rounded-t-lg flex items-start justify-center pt-2 text-[#0b1220] font-bold text-lg`}
              >
                {idx + 1}
              </div>
            </div>
          );
        })}
      </div>
      <div className="text-center text-[11px] text-grey">{PLACE_LABEL.slice(0, winners.length).join(" · ")}</div>
    </ChartCard>
  );
}
