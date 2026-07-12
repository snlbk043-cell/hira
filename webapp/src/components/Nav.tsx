"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Home" },
  { href: "/dashboard/executive", label: "Executive" },
  { href: "/dashboard/leadership", label: "Leadership" },
  { href: "/entry/incidents", label: "Incidents" },
  { href: "/entry/training", label: "Training" },
  { href: "/entry/observations", label: "Observations" },
  { href: "/entry/inspections", label: "Inspections" },
  { href: "/entry/walkthroughs", label: "Walkthroughs" },
  { href: "/entry/corrective-actions", label: "CAPA" },
  { href: "/entry/ptw-audits", label: "PTW" },
  { href: "/entry/risk-assessments", label: "JSA" },
  { href: "/settings", label: "Settings" },
];

export default function Nav() {
  const pathname = usePathname();
  return (
    <nav className="sticky top-0 z-40 border-b border-border bg-[#0b1220]/95 backdrop-blur">
      <div className="max-w-7xl mx-auto px-4 flex items-center gap-1 overflow-x-auto py-2 text-sm">
        <span className="font-bold text-teal mr-3 whitespace-nowrap">🧭 RCPL Safety</span>
        {links.map((l) => {
          const active = pathname === l.href;
          return (
            <Link
              key={l.href}
              href={l.href}
              className={`px-3 py-1.5 rounded-md whitespace-nowrap transition-colors ${
                active ? "bg-teal text-[#0b1220] font-semibold" : "text-grey hover:text-white hover:bg-card-2"
              }`}
            >
              {l.label}
            </Link>
          );
        })}
      </div>
    </nav>
  );
}
