export default function ChartCard({
  title,
  children,
  className = "",
}: {
  title: string;
  children: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={`card p-4 ${className}`}>
      <div className="flex items-center gap-2 mb-3">
        <span className="w-1.5 h-1.5 rounded-full bg-teal shadow-[0_0_8px_2px_rgba(20,184,166,0.6)]" />
        <div className="text-sm font-semibold text-white tracking-wide">{title}</div>
      </div>
      {children}
    </div>
  );
}
