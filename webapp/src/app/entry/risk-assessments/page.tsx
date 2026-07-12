"use client";
import EntryPage from "@/components/EntryPage";
import { RISK_LEVELS, JSA_APPROVAL_STATUSES } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="Risk Assessments (JSA)"
      icon="⚠️"
      endpoint="/api/risk-assessments"
      fields={[
        { name: "assessment_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "task", label: "Task / Activity", type: "text" },
        { name: "risk_level", label: "Risk Level", type: "select", options: RISK_LEVELS },
        { name: "hazards_identified", label: "Hazards Identified", type: "number" },
        { name: "approval_status", label: "Approval Status", type: "select", options: JSA_APPROVAL_STATUSES },
        { name: "controls_implemented", label: "Controls Implemented", type: "text" },
      ]}
    />
  );
}
