"use client";
import { DEPARTMENTS, MONTH_NAMES } from "@/lib/constants";

type Props = {
  year: number;
  department: string;
  month: number;
  onYearChange: (y: number) => void;
  onDepartmentChange: (d: string) => void;
  onMonthChange: (m: number) => void;
};

export default function Filters({ year, department, month, onYearChange, onDepartmentChange, onMonthChange }: Props) {
  const years = [year - 1, year, year + 1];
  return (
    <div className="card p-3 flex flex-wrap items-center gap-4 mb-4 no-print">
      <div className="flex items-center gap-2">
        <label className="text-xs text-grey">Year</label>
        <select value={year} onChange={(e) => onYearChange(Number(e.target.value))}>
          {years.map((y) => (
            <option key={y} value={y}>{y}</option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-2">
        <label className="text-xs text-grey">Month</label>
        <select value={month} onChange={(e) => onMonthChange(Number(e.target.value))}>
          <option value={0}>All</option>
          {MONTH_NAMES.map((m, i) => (
            <option key={m} value={i + 1}>{m}</option>
          ))}
        </select>
      </div>
      <div className="flex items-center gap-2">
        <label className="text-xs text-grey">Department</label>
        <select value={department} onChange={(e) => onDepartmentChange(e.target.value)}>
          <option value="All">All</option>
          {DEPARTMENTS.map((d) => (
            <option key={d} value={d}>{d}</option>
          ))}
        </select>
      </div>
    </div>
  );
}
