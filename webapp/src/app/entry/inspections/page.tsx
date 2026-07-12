"use client";
import EntryPage from "@/components/EntryPage";
import { INSPECTION_STATUSES } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="Inspections (Workplace / Equipment)"
      icon="🔍"
      endpoint="/api/inspections"
      fields={[
        { name: "inspection_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "inspection_type", label: "Type", type: "select", options: ["Workplace", "Equipment"], required: true },
        { name: "status", label: "Status", type: "select", options: INSPECTION_STATUSES },
        { name: "critical_findings", label: "Critical Findings", type: "number" },
        { name: "non_conformances", label: "Non-Conformances", type: "number" },
        { name: "due_date", label: "Due Date", type: "date" },
      ]}
    />
  );
}
