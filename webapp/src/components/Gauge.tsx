"use client";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

export default function Gauge({ value, label, color = "#14b8a6" }: { value: number; label: string; color?: string }) {
  const v = Math.max(0, Math.min(100, value));
  const data = [{ v }, { v: 100 - v }];
  const gid = `gaugeGrad-${label.replace(/[^a-zA-Z0-9]/g, "")}`;
  return (
    <div className="flex flex-col items-center">
      <div className="relative w-full" style={{ filter: `drop-shadow(0 0 10px ${color}55)` }}>
        <ResponsiveContainer width="100%" height={100}>
          <PieChart>
            <defs>
              <linearGradient id={gid} x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%" stopColor={color} stopOpacity={0.55} />
                <stop offset="100%" stopColor={color} stopOpacity={1} />
              </linearGradient>
            </defs>
            <Pie
              data={data}
              dataKey="v"
              startAngle={180}
              endAngle={0}
              innerRadius="72%"
              outerRadius="100%"
              cx="50%"
              cy="95%"
              stroke="none"
              cornerRadius={6}
            >
              <Cell fill={`url(#${gid})`} />
              <Cell fill="#1b2740" />
            </Pie>
          </PieChart>
        </ResponsiveContainer>
        <div
          className="absolute inset-x-0 top-[52px] text-center text-xl font-extrabold"
          style={{ color, textShadow: `0 0 16px ${color}70` }}
        >
          {v.toFixed(0)}%
        </div>
      </div>
      <div className="text-xs text-grey mt-3 text-center font-medium">{label}</div>
    </div>
  );
}
