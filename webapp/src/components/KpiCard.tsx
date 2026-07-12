type Props = {
  icon: string;
  label: string;
  value: string | number;
  sub?: string;
  accent?: "teal" | "gold" | "purple" | "coral";
};

const accentClass: Record<string, string> = {
  teal: "border-teal text-teal",
  gold: "border-gold text-gold",
  purple: "border-purple text-purple",
  coral: "border-coral text-coral",
};

export default function KpiCard({ icon, label, value, sub, accent = "teal" }: Props) {
  return (
    <div className={`card p-4 border-l-4 ${accentClass[accent].split(" ")[0]}`}>
      <div className="flex items-start justify-between">
        <div>
          <div className="text-xs font-semibold text-grey uppercase tracking-wide">{label}</div>
          <div className="text-3xl font-bold mt-1">{value}</div>
          {sub && <div className={`text-xs mt-1 ${accentClass[accent].split(" ")[1]}`}>{sub}</div>}
        </div>
        <div className="text-2xl opacity-80">{icon}</div>
      </div>
    </div>
  );
}
