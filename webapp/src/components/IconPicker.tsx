"use client";
import { useState } from "react";

export const EHS_EMOJIS: { emoji: string; label: string }[] = [
  { emoji: "🦺", label: "Safety Vest" }, { emoji: "⛑️", label: "Hard Hat" }, { emoji: "🥽", label: "Goggles" },
  { emoji: "🧯", label: "Fire Extinguisher" }, { emoji: "🔥", label: "Fire" }, { emoji: "⚠️", label: "Warning" },
  { emoji: "🚨", label: "Alarm" }, { emoji: "🚧", label: "Barrier" }, { emoji: "⚡", label: "Electrical" },
  { emoji: "☣️", label: "Biohazard" }, { emoji: "☢️", label: "Radiation" }, { emoji: "🧪", label: "Chemical" },
  { emoji: "🧰", label: "Toolbox" }, { emoji: "🛠️", label: "Tools" }, { emoji: "🔧", label: "Wrench" },
  { emoji: "🏗️", label: "Construction" }, { emoji: "🏭", label: "Factory" }, { emoji: "🚜", label: "Machinery" },
  { emoji: "🔍", label: "Inspection" }, { emoji: "📋", label: "Checklist / Audit" }, { emoji: "📝", label: "Report" },
  { emoji: "✅", label: "Compliance" }, { emoji: "🚫", label: "Prohibited" }, { emoji: "🆘", label: "Emergency" },
  { emoji: "🚑", label: "Ambulance" }, { emoji: "🩹", label: "First Aid" }, { emoji: "💉", label: "Medical" },
  { emoji: "🚭", label: "No Smoking" }, { emoji: "🦽", label: "Restricted Work" }, { emoji: "🧑‍⚕️", label: "Health" },
  { emoji: "🌱", label: "Environmental" }, { emoji: "♻️", label: "Recycle" }, { emoji: "💧", label: "Water" },
  { emoji: "⚗️", label: "Lab / Chemical" }, { emoji: "🛡️", label: "Protection" }, { emoji: "📞", label: "Contact" },
  { emoji: "🗣️", label: "Talk / Meeting" }, { emoji: "🎓", label: "Training" }, { emoji: "🏆", label: "Award" },
  { emoji: "🏅", label: "Medal" }, { emoji: "🎉", label: "Celebration" }, { emoji: "👷", label: "Worker" },
  { emoji: "🧑‍🏭", label: "Factory Worker" }, { emoji: "🚶", label: "Walkthrough" }, { emoji: "🗓️", label: "Calendar" },
  { emoji: "📅", label: "Date" }, { emoji: "📊", label: "Chart / Data" }, { emoji: "📈", label: "Trend" },
  { emoji: "🏢", label: "Building" }, { emoji: "🚪", label: "Access" }, { emoji: "🔒", label: "Lock" },
  { emoji: "🪜", label: "Ladder / Height" }, { emoji: "🌡️", label: "Temperature" }, { emoji: "💨", label: "Gas / Air" },
  { emoji: "🛑", label: "Stop" }, { emoji: "✋", label: "Stop Work" }, { emoji: "🧑‍🔧", label: "Technician" },
  { emoji: "📦", label: "Warehouse" }, { emoji: "🚛", label: "Logistics" }, { emoji: "⚙️", label: "Process" },
  { emoji: "📁", label: "General" }, { emoji: "🏛️", label: "Regulatory" }, { emoji: "⏰", label: "Deadline" },
  { emoji: "👥", label: "Team / Engagement" }, { emoji: "🎯", label: "Target" }, { emoji: "🧭", label: "Compass" },
];

export default function IconPicker({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const [open, setOpen] = useState(false);
  const [search, setSearch] = useState("");

  const filtered = search.trim()
    ? EHS_EMOJIS.filter((e) => e.label.toLowerCase().includes(search.trim().toLowerCase()))
    : EHS_EMOJIS;

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        className="w-full text-center text-2xl py-2 rounded-md border border-border bg-card-2 hover:border-teal/50 transition-colors"
      >
        {value || "📁"}
      </button>

      {open && (
        <>
          <div className="fixed inset-0 z-40" onClick={() => setOpen(false)} />
          <div className="modal-pop absolute z-50 mt-1.5 w-72 card p-2.5 shadow-2xl">
            <input
              autoFocus
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search icons (e.g. fire, audit, medal)…"
              className="w-full text-xs mb-2"
            />
            <div className="files-scroll grid grid-cols-7 gap-1 max-h-56 overflow-y-scroll pr-1">
              {filtered.map((e) => (
                <button
                  key={e.emoji}
                  type="button"
                  title={e.label}
                  onClick={() => { onChange(e.emoji); setOpen(false); setSearch(""); }}
                  className={`text-xl p-1.5 rounded-md hover:bg-card-2 transition-colors ${value === e.emoji ? "bg-teal/20 ring-1 ring-teal" : ""}`}
                >
                  {e.emoji}
                </button>
              ))}
              {filtered.length === 0 && <p className="col-span-7 text-xs text-grey text-center py-3">No matching icons.</p>}
            </div>
          </div>
        </>
      )}
    </div>
  );
}
