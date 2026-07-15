"use client";
import { useEffect, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { TRACKERS } from "@/lib/trackers";

const DEFAULT_SITE_NAME = "RCPL SAFETY";
const DEFAULT_COMPANY_NAME = "Campa Cola CSD Plant · EHS System";

function useBranding() {
  const [siteName, setSiteName] = useState(DEFAULT_SITE_NAME);
  const [companyName, setCompanyName] = useState(DEFAULT_COMPANY_NAME);
  useEffect(() => {
    fetch("/api/settings")
      .then((r) => r.json())
      .then((s: Record<string, string>) => {
        if (s.site_name) setSiteName(s.site_name);
        if (s.company_name) setCompanyName(s.company_name);
      })
      .catch(() => {});
  }, []);
  return { siteName, companyName };
}

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
      className={`relative flex items-center gap-2.5 px-3 py-2 rounded-lg text-sm transition-all duration-150 ${
        active
          ? "bg-gradient-to-r from-teal/25 to-teal/5 text-teal font-semibold shadow-[inset_0_0_0_1px_rgba(20,184,166,0.35)]"
          : "text-grey hover:text-white hover:bg-card-2"
      }`}
    >
      {active && <span className="absolute left-0 top-1/2 -translate-y-1/2 h-4 w-[3px] rounded-full bg-teal shadow-[0_0_8px_2px_rgba(20,184,166,0.7)]" />}
      <span className="text-base leading-none w-5 text-center shrink-0">{icon}</span>
      <span className="truncate">{label}</span>
    </Link>
  );
}

function SidebarContent({ pathname, onNavigate, siteName, companyName }: { pathname: string; onNavigate?: () => void; siteName: string; companyName: string }) {
  return (
    <div className="flex flex-col h-full overflow-y-auto">
      <div className="px-4 py-4 border-b border-border flex items-center gap-2.5">
        <div
          className="w-8 h-8 rounded-lg flex items-center justify-center text-base shrink-0"
          style={{ background: "linear-gradient(155deg, #14b8a633, #14b8a612)", border: "1px solid #14b8a640", boxShadow: "0 4px 14px -6px #14b8a680" }}
        >
          🧭
        </div>
        <div className="min-w-0">
          <div className="font-bold text-white text-sm tracking-wide truncate">{siteName}</div>
          <div className="text-[11px] text-grey mt-0.5 truncate">{companyName}</div>
        </div>
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
  const { siteName, companyName } = useBranding();

  return (
    <>
      {/* mobile top bar */}
      <div className="md:hidden sticky top-0 z-40 flex items-center justify-between px-4 py-3 border-b border-border bg-[#0b1220]/95 backdrop-blur">
        <span className="font-bold text-teal text-sm">🧭 {siteName}</span>
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
            <SidebarContent pathname={pathname} onNavigate={() => setOpen(false)} siteName={siteName} companyName={companyName} />
          </div>
          <div className="flex-1 bg-black/50" onClick={() => setOpen(false)} />
        </div>
      )}

      {/* desktop sidebar */}
      <aside className="hidden md:block w-64 shrink-0 border-r border-border bg-[#0b1220] sticky top-0 h-screen">
        <SidebarContent pathname={pathname} siteName={siteName} companyName={companyName} />
      </aside>
    </>
  );
}
