"use client";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";

export default function Gauge({ value, label, color = "#14b8a6" }: { value: number; label: string; color?: string }) {
  const v = Math.max(0, Math.min(100, value));
  const data = [{ v }, { v: 100 - v }];
  return (
    <div className="flex flex-col items-center">
      <ResponsiveContainer width="100%" height={100}>
        <PieChart>
          <Pie data={data} dataKey="v" startAngle={180} endAngle={0} innerRadius="70%" outerRadius="100%" cx="50%" cy="95%">
            <Cell fill={color} />
            <Cell fill="#22314f" />
          </Pie>
        </PieChart>
      </ResponsiveContainer>
      <div className="text-xl font-bold -mt-10" style={{ color }}>{v.toFixed(0)}%</div>
      <div className="text-xs text-grey mt-4 text-center">{label}</div>
    </div>
  );
}
