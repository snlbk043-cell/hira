import { Row } from "@/lib/aggregate";
import ChartCard from "@/components/ChartCard";

const LIK_LABELS: Record<number, string> = { 5: "5 Almost Certain", 4: "4 Likely", 3: "3 Possible", 2: "2 Unlikely", 1: "1 Rare" };
const CONS_LABELS: Record<number, string> = { 1: "1 Negligible", 2: "2 Minor", 3: "3 Moderate", 4: "4 Major", 5: "5 Catastrophic" };

function bandColor(score: number) {
  if (score <= 4) return "#14b8a6";   // Low - teal
  if (score <= 9) return "#f5a524";   // Medium - gold
  if (score <= 14) return "#f2994a";  // High - orange
  return "#f0625a";                    // Extreme - coral
}

/** A genuine Likelihood x Consequence 5x5 risk matrix computed live from the
 * JSA Risk Assessment rows. Cell colour is a fixed property of the matrix
 * design (the risk band for that score); the number is a live count -
 * matches the Excel system's risk matrix exactly. */
export default function RiskMatrix({ rows }: { rows: Row[] }) {
  const counts: Record<string, number> = {};
  for (const r of rows) {
    const lik = Number(r.likelihood);
    const cons = Number(r.consequence);
    if (!lik || !cons || lik < 1 || lik > 5 || cons < 1 || cons > 5) continue;
    const key = `${lik}-${cons}`;
    counts[key] = (counts[key] || 0) + 1;
  }
  const rated = rows.filter((r) => r.likelihood && r.consequence).length;

  return (
    <ChartCard title="True Risk Matrix — Likelihood x Consequence (spider-adjacent heat grid)" className="mb-6">
      {rated === 0 ? (
        <p className="text-grey text-sm p-4">
          No JSA records yet have both Likelihood and Consequence rated (1-5). Fill those two fields on new/edited
          records to populate this matrix.
        </p>
      ) : (
        <div className="overflow-x-auto mt-2">
          <table className="w-full text-sm border-separate" style={{ borderSpacing: 4 }}>
            <thead>
              <tr>
                <th className="text-xs text-grey text-left p-1">Likelihood ▼ / Consequence ▶</th>
                {[1, 2, 3, 4, 5].map((c) => (
                  <th key={c} className="text-xs text-grey p-1 text-center">{CONS_LABELS[c]}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {[5, 4, 3, 2, 1].map((lik) => (
                <tr key={lik}>
                  <td className="text-xs text-grey p-1 whitespace-nowrap">{LIK_LABELS[lik]}</td>
                  {[1, 2, 3, 4, 5].map((cons) => {
                    const score = lik * cons;
                    const n = counts[`${lik}-${cons}`] || 0;
                    return (
                      <td
                        key={cons}
                        className="text-center font-bold rounded-md p-3 text-[#0b1220]"
                        style={{ background: bandColor(score) }}
                      >
                        {n}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          <p className="text-xs text-grey mt-3">
            🟢 Low (score 1-4) 🟡 Medium (5-9) 🟠 High (10-14) 🔴 Extreme (15-25) · score = Likelihood × Consequence ·
            {rated} of {rows.length} records rated
          </p>
        </div>
      )}
    </ChartCard>
  );
}
