"use client";
import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TRACKERS } from "@/lib/trackers";

const overview = [
  { href: "/", label: "Home", icon: "🏠" },
  { href: "/dashboard/executive", label: "Executive Dashboard", icon: "🏆" },
  { href: "/dashboard/leadership", label: "Leadership Review", icon: "🧭" },
];

function NavLink({ href, icon, label, active, onClick }: { href: string; icon: string; label: string; active: boolean; onClick?: () => void }) {
  return (
    <Link
      href={href}
      onClick={onClick}
      className={`flex items-center gap-2.5 px-3 py-2 rounded-md text-sm transition-colors ${
        active ? "bg-teal text-[#0b1220] font-semibold" : "text-grey hover:text-white hover:bg-card-2"
      }`}
    >
      <span className="text-base leading-none w-5 text-center shrink-0">{icon}</span>
      <span className="truncate">{label}</span>
    </Link>
  );
}

function SidebarContent({ pathname, onNavigate }: { pathname: string; onNavigate?: () => void }) {
  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="px-4 py-4 border-b border-border">
        <div className="font-bold text-teal text-sm tracking-wide">🧭 RCPL SAFETY</div>
        <div className="text-[11px] text-grey mt-0.5">Campa Cola CSD Plant · EHS System</div>
      </div>

      <div className="px-2 py-3">
        <div className="text-[10px] font-semibold text-grey uppercase tracking-wider px-3 mb-1.5">Overview</div>
        <div className="flex flex-col gap-0.5">
          {overview.map((l) => (
            <NavLink key={l.href} href={l.href} icon={l.icon} label={l.label} active={pathname === l.href} onClick={onNavigate} />
          ))}
        </div>
      </div>

      <div className="px-2 py-1 flex-1">
        <div className="text-[10px] font-semibold text-grey uppercase tracking-wider px-3 mb-1.5">Trackers</div>
        <div className="flex flex-col gap-0.5">
          {TRACKERS.map((t) => {
            const href = `/tracker/${t.key}`;
            return <NavLink key={t.key} href={href} icon={t.icon} label={t.label} active={pathname === href} onClick={onNavigate} />;
          })}
        </div>
      </div>

      <div className="px-2 py-3 border-t border-border">
        <NavLink href="/settings" icon="⚙️" label="Settings" active={pathname === "/settings"} onClick={onNavigate} />
      </div>
    </div>
  );
}

export default function Sidebar() {
  const pathname = usePathname();
  const [open, setOpen] = useState(false);

  return (
    <>
      {/* mobile top bar */}
      <div className="md:hidden sticky top-0 z-40 flex items-center justify-between px-4 py-3 border-b border-border bg-[#0b1220]/95 backdrop-blur">
        <span className="font-bold text-teal text-sm">🧭 RCPL SAFETY</span>
        <button
          onClick={() => setOpen(true)}
          aria-label="Open navigation"
          className="text-white text-xl px-2 py-1 rounded-md border border-border"
        >
          ☰
        </button>
      </div>

      {/* mobile drawer */}
      {open && (
        <div className="md:hidden fixed inset-0 z-50 flex">
          <div className="w-72 bg-[#0b1220] border-r border-border h-full">
            <div className="flex justify-end px-3 pt-3">
              <button onClick={() => setOpen(false)} aria-label="Close navigation" className="text-white text-xl px-2">✕</button>
            </div>
            <SidebarContent pathname={pathname} onNavigate={() => setOpen(false)} />
          </div>
          <div className="flex-1 bg-black/50" onClick={() => setOpen(false)} />
        </div>
      )}

      {/* desktop sidebar */}
      <aside className="hidden md:block w-64 shrink-0 border-r border-border bg-[#0b1220] sticky top-0 h-screen">
        <SidebarContent pathname={pathname} />
      </aside>
    </>
  );
}
