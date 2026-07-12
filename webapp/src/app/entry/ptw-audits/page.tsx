"use client";
import EntryPage from "@/components/EntryPage";
import { PTW_VERDICTS } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="PTW Audits"
      icon="📝"
      endpoint="/api/ptw-audits"
      fields={[
        { name: "audit_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "permit_type", label: "Permit Type", type: "text" },
        { name: "auditor", label: "Auditor", type: "text" },
        { name: "permits_reviewed", label: "Permits Reviewed", type: "number" },
        { name: "deviations_found", label: "Deviations Found", type: "number" },
        { name: "compliance_pct", label: "Compliance %", type: "number" },
        { name: "verdict", label: "Verdict", type: "select", options: PTW_VERDICTS },
      ]}
    />
  );
}
