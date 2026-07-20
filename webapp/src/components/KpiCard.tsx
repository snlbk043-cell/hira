type Props = {
  icon: string;
  label: string;
  value: string | number;
  sub?: string;
  accent?: "teal" | "gold" | "purple" | "coral";
};

const ACCENT_HEX: Record<string, string> = {
  teal: "#14b8a6",
  gold: "#f5a524",
  purple: "#8b5cf6",
  coral: "#f0625a",
};

const textClass: Record<string, string> = {
  teal: "text-teal",
  gold: "text-gold",
  purple: "text-purple",
  coral: "text-coral",
};

export default function KpiCard({ icon, label, value, sub, accent = "teal" }: Props) {
  const hex = ACCENT_HEX[accent];
  return (
    <div
      className="card relative p-4 overflow-hidden group"
      style={{ animation: "kpi-rise 320ms ease both" }}
    >
      <div
        className="absolute inset-x-0 top-0 h-[3px]"
        style={{ background: `linear-gradient(90deg, ${hex}, ${hex}00)` }}
      />
      <div
        className="pointer-events-none absolute -right-6 -top-6 w-24 h-24 rounded-full opacity-20 blur-2xl transition-opacity duration-300 group-hover:opacity-35"
        style={{ background: hex }}
      />
      <div className="relative flex items-start justify-between gap-3">
        <div className="min-w-0">
          <div className="text-[0.68rem] font-semibold text-grey uppercase tracking-wider truncate">{label}</div>
          <div className="text-2xl md:text-3xl font-extrabold mt-1.5 tracking-tight text-white">
            {value}
          </div>
          {sub && <div className={`text-xs mt-1 ${textClass[accent]}`}>{sub}</div>}
        </div>
        <div
          className="shrink-0 flex items-center justify-center w-10 h-10 rounded-xl text-lg"
          style={{
            background: `linear-gradient(155deg, ${hex}33, ${hex}12)`,
            border: `1px solid ${hex}40`,
            boxShadow: `0 4px 14px -6px ${hex}80`,
          }}
        >
          {icon}
        </div>
      </div>
    </div>
  );
}
