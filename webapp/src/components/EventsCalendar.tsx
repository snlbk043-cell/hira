"use client";
import { useMemo, useState } from "react";
import ChartCard from "@/components/ChartCard";
import type { Row } from "@/lib/aggregate";

const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const CATEGORY_COLORS: Record<string, string> = {
  "Fun Activity": "#14b8a6",
  "Award Ceremony": "#f5a524",
  "Team Building": "#8b5cf6",
  Wellness: "#14b8a6",
  CSR: "#8b5cf6",
  Sports: "#f5a524",
  Cultural: "#f0625a",
};

export default function EventsCalendar({
  rows,
  dateField,
  nameField,
  categoryField,
  title = "Events Calendar",
}: {
  rows: Row[];
  dateField: string;
  nameField: string;
  categoryField: string;
  title?: string;
}) {
  const [viewMonth, setViewMonth] = useState(() => { const d = new Date(); d.setDate(1); return d; });
  const [selectedDay, setSelectedDay] = useState<string | null>(null);

  const byDay = useMemo(() => {
    const m = new Map<string, Row[]>();
    for (const r of rows) {
      const v = r[dateField];
      if (!v) continue;
      const key = String(v).slice(0, 10);
      if (!m.has(key)) m.set(key, []);
      m.get(key)!.push(r);
    }
    return m;
  }, [rows, dateField]);

  const year = viewMonth.getFullYear();
  const month = viewMonth.getMonth();
  const firstWeekday = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells: (string | null)[] = [...Array(firstWeekday).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => `${year}-${String(month + 1).padStart(2, "0")}-${String(i + 1).padStart(2, "0")}`)];

  const selectedItems = selectedDay ? byDay.get(selectedDay) ?? [] : [];
  const categories = Array.from(new Set(rows.map((r) => String(r[categoryField] ?? "")).filter(Boolean)));

  return (
    <ChartCard title={`🗓️ ${title}`} className="mb-6">
      <div className="flex flex-wrap gap-2 mb-3 text-[11px] text-grey">
        {categories.map((c) => (
          <span key={c} className="flex items-center gap-1">
            <span className="w-2 h-2 rounded-full" style={{ background: CATEGORY_COLORS[c] || "#94a3b8" }} />
            {c}
          </span>
        ))}
      </div>
      <div className="flex items-center justify-between mb-2">
        <button type="button" onClick={() => setViewMonth(new Date(year, month - 1, 1))} className="text-grey hover:text-white px-2">‹</button>
        <div className="text-sm font-semibold">{viewMonth.toLocaleDateString(undefined, { month: "long", year: "numeric" })}</div>
        <button type="button" onClick={() => setViewMonth(new Date(year, month + 1, 1))} className="text-grey hover:text-white px-2">›</button>
      </div>
      <div className="grid grid-cols-7 gap-1 text-center">
        {WEEKDAYS.map((w) => <div key={w} className="text-[10px] text-grey py-1">{w}</div>)}
        {cells.map((dateStr, i) => {
          if (!dateStr) return <div key={i} />;
          const dayItems = byDay.get(dateStr) ?? [];
          const isToday = dateStr === new Date().toISOString().slice(0, 10);
          const c = dayItems.length ? (CATEGORY_COLORS[String(dayItems[0][categoryField] ?? "")] || "#94a3b8") : null;
          return (
            <button
              key={dateStr}
              type="button"
              onClick={() => dayItems.length && setSelectedDay(selectedDay === dateStr ? null : dateStr)}
              className={`aspect-square rounded-md text-[11px] flex items-center justify-center relative transition-transform ${dayItems.length ? "hover:scale-105 cursor-pointer" : "cursor-default"} ${selectedDay === dateStr ? "ring-2 ring-white" : ""}`}
              style={{
                background: c ? `${c}25` : "rgba(148,163,184,0.04)",
                border: isToday ? "1px solid #14b8a6" : "1px solid transparent",
                color: c ? "#fff" : "#94a3b8",
              }}
            >
              {Number(dateStr.slice(8, 10))}
              {c && <span className="absolute bottom-0.5 w-1 h-1 rounded-full" style={{ background: c }} />}
            </button>
          );
        })}
      </div>

      {selectedDay && selectedItems.length > 0 && (
        <div className="mt-3 space-y-1.5">
          <div className="text-[11px] text-grey uppercase tracking-wide">{selectedDay}</div>
          {selectedItems.map((r, i) => (
            <div key={i} className="flex items-center gap-2 card bg-card-2 p-2 text-xs">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ background: CATEGORY_COLORS[String(r[categoryField] ?? "")] || "#94a3b8" }} />
              <div className="min-w-0 flex-1">
                <div className="truncate">{String(r[nameField] ?? "")}</div>
                <div className="text-[10px] text-grey">{String(r[categoryField] ?? "")} · {String(r.department ?? "")}</div>
              </div>
            </div>
          ))}
        </div>
      )}
    </ChartCard>
  );
}
