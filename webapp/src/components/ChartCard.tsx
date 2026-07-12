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
      <div className="text-sm font-semibold text-white mb-2">{title}</div>
      {children}
    </div>
  );
}
