"use client";
import EntryPage from "@/components/EntryPage";
import { OBS_STATUSES, RISK_LEVELS } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="HSE Observations"
      icon="👁️"
      endpoint="/api/observations"
      fields={[
        { name: "obs_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "observation_type", label: "Type", type: "select", options: ["Safe Act", "Unsafe Act", "Safe Condition", "Unsafe Condition", "Near Miss"] },
        { name: "risk_level", label: "Risk Level", type: "select", options: RISK_LEVELS },
        { name: "status", label: "Status", type: "select", options: OBS_STATUSES },
        { name: "due_date", label: "Due Date", type: "date" },
        { name: "description", label: "Description", type: "text" },
      ]}
    />
  );
}
