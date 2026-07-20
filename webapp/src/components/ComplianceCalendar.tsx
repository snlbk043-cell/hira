"use client";
import { useCallback, useEffect, useMemo, useState } from "react";
import ChartCard from "@/components/ChartCard";

type ScheduleItem = {
  id: number;
  tracker_key: string;
  title: string;
  location: string | null;
  frequency: string;
  due_date: string;
  status: "Pending" | "Done";
  completed_date: string | null;
  notes: string | null;
};

const FREQUENCIES = ["One-time", "Monthly", "Quarterly", "Half-Yearly", "Annually"];
const WEEKDAYS = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];
const TEAL = "#14b8a6", GOLD = "#f5a524", CORAL = "#f0625a", SLATE = "#475569";

function todayStr() {
  return new Date().toISOString().slice(0, 10);
}
function daysFromToday(dateStr: string) {
  return Math.floor((new Date(dateStr + "T00:00:00Z").getTime() - new Date(todayStr() + "T00:00:00Z").getTime()) / 86400000);
}
function itemColor(item: ScheduleItem): string {
  if (item.status === "Done") return TEAL;
  const d = daysFromToday(item.due_date);
  if (d < 0) return CORAL;
  if (d <= 7) return GOLD;
  return SLATE;
}
/** Worst (most urgent) color among a day's items - overdue beats due-soon beats upcoming beats done. */
function worstColor(items: ScheduleItem[]): string {
  const colors = items.map(itemColor);
  if (colors.includes(CORAL)) return CORAL;
  if (colors.includes(GOLD)) return GOLD;
  if (colors.includes(SLATE)) return SLATE;
  return TEAL;
}

export default function ComplianceCalendar({ trackerKey, title = "Compliance Calendar" }: { trackerKey: string; title?: string }) {
  const [items, setItems] = useState<ScheduleItem[] | null>(null);
  const [viewMonth, setViewMonth] = useState(() => { const d = new Date(); d.setDate(1); return d; });
  const [selectedDay, setSelectedDay] = useState<string | null>(null);
  const [showAdd, setShowAdd] = useState(false);
  const [saving, setSaving] = useState(false);
  const [form, setForm] = useState({ title: "", location: "", frequency: "Monthly", due_date: "", notes: "" });

  const load = useCallback(() => {
    fetch(`/api/compliance-schedule?trackerKey=${encodeURIComponent(trackerKey)}`)
      .then((r) => r.json())
      .then(setItems);
  }, [trackerKey]);

  useEffect(() => { load(); }, [load]);

  const byDay = useMemo(() => {
    const m = new Map<string, ScheduleItem[]>();
    for (const it of items ?? []) {
      const key = it.due_date.slice(0, 10);
      if (!m.has(key)) m.set(key, []);
      m.get(key)!.push(it);
    }
    return m;
  }, [items]);

  const year = viewMonth.getFullYear();
  const month = viewMonth.getMonth();
  const firstWeekday = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells: (string | null)[] = [...Array(firstWeekday).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => `${year}-${String(month + 1).padStart(2, "0")}-${String(i + 1).padStart(2, "0")}`)];

  const upcoming = (items ?? [])
    .filter((it) => it.status === "Pending")
    .sort((a, b) => a.due_date.localeCompare(b.due_date))
    .slice(0, 8);

  async function toggleDone(item: ScheduleItem) {
    const res = await fetch(`/api/compliance-schedule/${item.id}`, { method: "PATCH", headers: { "Content-Type": "application/json" }, body: JSON.stringify({}) });
    if (res.ok) load();
  }
  async function removeItem(id: number) {
    if (!confirm("Delete this schedule item?")) return;
    await fetch(`/api/compliance-schedule/${id}`, { method: "DELETE" });
    if (selectedDay) setSelectedDay(null);
    load();
  }
  async function addItem(e: React.FormEvent) {
    e.preventDefault();
    if (!form.title || !form.due_date) return;
    setSaving(true);
    try {
      const res = await fetch("/api/compliance-schedule", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ trackerKey, ...form }),
      });
      if (res.ok) {
        setForm({ title: "", location: "", frequency: "Monthly", due_date: "", notes: "" });
        setShowAdd(false);
        load();
      }
    } finally {
      setSaving(false);
    }
  }

  const selectedItems = selectedDay ? byDay.get(selectedDay) ?? [] : [];

  return (
    <ChartCard title={`🗓️ ${title}`} className="mb-6">
      <div className="flex items-center gap-3 mb-3 text-[11px] text-grey">
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: CORAL }} />Overdue</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: GOLD }} />Due ≤7d</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: SLATE }} />Upcoming</span>
        <span className="flex items-center gap-1"><span className="w-2 h-2 rounded-full" style={{ background: TEAL }} />Done</span>
        <button type="button" onClick={() => setShowAdd((s) => !s)} className="ml-auto text-xs px-2.5 py-1 rounded-md border border-teal/40 text-teal hover:bg-teal/10">
          {showAdd ? "Cancel" : "+ Schedule Item"}
        </button>
      </div>

      {showAdd && (
        <form onSubmit={addItem} className="card bg-card-2 p-3 mb-3 grid grid-cols-1 md:grid-cols-5 gap-2 items-end">
          <div className="flex flex-col gap-1 md:col-span-2">
            <label className="text-[10px] text-grey">What / Task *</label>
            <input value={form.title} onChange={(e) => setForm((f) => ({ ...f, title: e.target.value }))} placeholder="e.g. Fire Extinguisher Check" required />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-grey">Location</label>
            <input value={form.location} onChange={(e) => setForm((f) => ({ ...f, location: e.target.value }))} placeholder="e.g. Block A" />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-grey">Due Date *</label>
            <input type="date" value={form.due_date} onChange={(e) => setForm((f) => ({ ...f, due_date: e.target.value }))} required />
          </div>
          <div className="flex flex-col gap-1">
            <label className="text-[10px] text-grey">Frequency</label>
            <select value={form.frequency} onChange={(e) => setForm((f) => ({ ...f, frequency: e.target.value }))}>
              {FREQUENCIES.map((fr) => <option key={fr} value={fr}>{fr}</option>)}
            </select>
          </div>
          <button type="submit" disabled={saving} className="md:col-span-5 justify-self-start bg-teal text-[#0b1220] font-semibold text-xs px-4 py-2 rounded-md disabled:opacity-50">
            {saving ? "Saving…" : "Add to Calendar"}
          </button>
        </form>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_260px] gap-4">
        <div>
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
              const isToday = dateStr === todayStr();
              const c = dayItems.length ? worstColor(dayItems) : null;
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
              {selectedItems.map((it) => (
                <div key={it.id} className="flex items-center gap-2 card bg-card-2 p-2 text-xs">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: itemColor(it) }} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate">{it.title}{it.location ? ` · ${it.location}` : ""}</div>
                    <div className="text-[10px] text-grey">{it.frequency}{it.status === "Done" && it.completed_date ? ` · done ${it.completed_date}` : ""}</div>
                  </div>
                  <button
                    onClick={() => toggleDone(it)}
                    className={`text-[10px] px-2 py-1 rounded-md border shrink-0 ${it.status === "Done" ? "border-teal/40 text-teal hover:bg-teal/10" : "border-gold/40 text-gold hover:bg-gold/10"}`}
                  >
                    {it.status === "Done" ? "✓ Done" : "Mark Done"}
                  </button>
                  <button onClick={() => removeItem(it.id)} className="text-coral text-[10px] shrink-0">✕</button>
                </div>
              ))}
            </div>
          )}
        </div>

        <div>
          <div className="text-[11px] text-grey uppercase tracking-wide mb-1.5">Upcoming &amp; Overdue</div>
          <div className="files-scroll max-h-72 overflow-y-scroll space-y-1.5 pr-1">
            {upcoming.length === 0 ? (
              <p className="text-xs text-grey">Nothing scheduled yet.</p>
            ) : (
              upcoming.map((it) => (
                <div key={it.id} className="flex items-center gap-2 card bg-card-2 p-2 text-xs">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ background: itemColor(it) }} />
                  <div className="min-w-0 flex-1">
                    <div className="truncate">{it.title}</div>
                    <div className="text-[10px] text-grey truncate">{it.location ? `${it.location} · ` : ""}{it.due_date}</div>
                  </div>
                  <button onClick={() => toggleDone(it)} className="text-[10px] px-2 py-1 rounded-md border border-teal/40 text-teal hover:bg-teal/10 shrink-0">✓</button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </ChartCard>
  );
}
