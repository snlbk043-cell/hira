"use client";
import EntryPage from "@/components/EntryPage";
import { TRAINING_STATUSES } from "@/lib/constants";

export default function Page() {
  return (
    <EntryPage
      title="Training"
      icon="🎓"
      endpoint="/api/training"
      fields={[
        { name: "training_date", label: "Date", type: "date", required: true },
        { name: "department", label: "Department", type: "department", required: true },
        { name: "course_name", label: "Course Name", type: "text" },
        { name: "training_type", label: "Training Type", type: "text" },
        { name: "status", label: "Status", type: "select", options: TRAINING_STATUSES },
        { name: "attendance_pct", label: "Attendance %", type: "number" },
        { name: "assessment_result", label: "Assessment Result", type: "select", options: ["Pass", "Fail", "N/A"] },
      ]}
    />
  );
}
