"use client";
import EntryPage from "@/components/EntryPage";
import { CA_STATUSES } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="Corrective Actions"
      icon="🔧"
      endpoint="/api/corrective-actions"
      fields={[
        { name: "date_raised", label: "Date Raised", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "source", label: "Source", type: "text" },
        { name: "priority", label: "Priority", type: "select", options: ["High", "Medium", "Low"] },
        { name: "description", label: "Description", type: "text" },
        { name: "status", label: "Status", type: "select", options: CA_STATUSES },
        { name: "due_date", label: "Due Date", type: "date" },
        { name: "completion_date", label: "Completion Date", type: "date" },
        { name: "assigned_to", label: "Assigned To", type: "text" },
      ]}
    />
  );
}
