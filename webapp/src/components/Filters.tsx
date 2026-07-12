"use client";
import { DEPARTMENTS } from "@/lib/constants";

type Props = {
  year: number;
  department: string;
  onYearChange: (y: number) => void;
  onDepartmentChange: (d: string) => void;
};

export default function Filters({ year, department, onYearChange, onDepartmentChange }: Props) {
  const years = [year - 1, year, year + 1];
  return (
    <div className="card p-3 flex flex-wrap items-center gap-4 mb-4">
      <div className="flex items-center gap-2">
        <label className="text-xs text-grey">Year</label>
        <select value={year} onChange={(e) => onYearChange(Number(e.target.value))}>
          {years.map((y) => (
            <option key={y} value={y}>{y}</option>
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
