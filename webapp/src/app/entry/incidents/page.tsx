"use client";
import EntryPage from "@/components/EntryPage";
import { INCIDENT_CLASSIFICATIONS, BODY_PARTS, RISK_LEVELS } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="Incidents"
      icon="🔥"
      endpoint="/api/incidents"
      fields={[
        { name: "incident_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "area", label: "Area", type: "text" },
        { name: "classification", label: "Classification", type: "select", options: INCIDENT_CLASSIFICATIONS, required: true },
        { name: "body_part", label: "Body Part", type: "select", options: BODY_PARTS },
        { name: "risk_rating", label: "Risk Rating", type: "select", options: RISK_LEVELS },
        { name: "lost_days", label: "Lost Days", type: "number" },
        { name: "root_cause", label: "Root Cause", type: "text" },
        { name: "description", label: "Description", type: "text" },
        { name: "status", label: "Status", type: "select", options: ["Open", "In Progress", "Closed"] },
      ]}
    />
  );
}
