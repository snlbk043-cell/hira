"use client";
import EntryPage from "@/components/EntryPage";
import { WALKTHROUGH_STATUSES } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="Safety Walkthroughs"
      icon="🚶"
      endpoint="/api/walkthroughs"
      fields={[
        { name: "walk_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "area", label: "Area", type: "text" },
        { name: "owner", label: "Owner", type: "text" },
        { name: "status", label: "Status", type: "select", options: WALKTHROUGH_STATUSES },
        { name: "completion_pct", label: "Completion %", type: "number" },
        { name: "critical_findings", label: "Critical Findings", type: "number" },
        { name: "due_date", label: "Due Date", type: "date" },
      ]}
    />
  );
}
