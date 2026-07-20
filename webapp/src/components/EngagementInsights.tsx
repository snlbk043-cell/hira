"use client";
import ChartCard from "@/components/ChartCard";
import type { Row } from "@/lib/aggregate";

export default function EngagementInsights({ rows }: { rows: Row[] }) {
  if (rows.length === 0) return null;

  const now = new Date();
  const thisMonthCount = rows.filter((r) => {
    const d = new Date(String(r.event_date));
    return !isNaN(d.getTime()) && d.getMonth() === now.getMonth() && d.getFullYear() === now.getFullYear();
  }).length;

  const byCategory = new Map<string, number>();
  const byDept = new Map<string, number>();
  let totalParticipation = 0;
  let feedbackSum = 0;
  let feedbackCount = 0;

  for (const r of rows) {
    const cat = String(r.category ?? "");
    if (cat) byCategory.set(cat, (byCategory.get(cat) ?? 0) + 1);
    const dept = String(r.department ?? "");
    const participation = Number(r.participation_count) || 0;
    totalParticipation += participation;
    if (dept) byDept.set(dept, (byDept.get(dept) ?? 0) + participation);
    const fb = Number(r.feedback_score_pct);
    if (!isNaN(fb) && r.feedback_score_pct !== null && r.feedback_score_pct !== "") {
      feedbackSum += fb;
      feedbackCount++;
    }
  }

  const topCategory = [...byCategory.entries()].sort((a, b) => b[1] - a[1])[0];
  const topDept = [...byDept.entries()].sort((a, b) => b[1] - a[1])[0];
  const avgFeedback = feedbackCount ? Math.round((feedbackSum / feedbackCount) * 10) / 10 : null;
  const completed = rows.filter((r) => String(r.status) === "Completed").length;

  const insights: string[] = [];
  insights.push(`${rows.length} engagement events tracked, ${completed} completed and ${rows.length - completed} planned — ${thisMonthCount} scheduled this month.`);
  if (topCategory) insights.push(`"${topCategory[0]}" is the most frequent event type (${topCategory[1]} event${topCategory[1] === 1 ? "" : "s"}) — a good sign of where team energy is going.`);
  if (topDept) insights.push(`${topDept[0]} leads participation with ${topDept[1]} attendee-events recorded — a strong culture indicator for that team.`);
  insights.push(`Total participation across all events: ${totalParticipation.toLocaleString()} attendee-visits.`);
  if (avgFeedback !== null) {
    insights.push(`Average feedback score is ${avgFeedback}% — ${avgFeedback >= 85 ? "employees are highly satisfied with engagement activities" : avgFeedback >= 60 ? "feedback is positive but there's room to improve" : "feedback suggests activities need a rethink"}.`);
  }

  return (
    <ChartCard title="✨ Key Insights" className="mb-6">
      <ul className="space-y-2 mt-2">
        {insights.map((t, i) => (
          <li key={i} className="text-sm border-l-2 border-teal pl-3 py-1">{t}</li>
        ))}
      </ul>
    </ChartCard>
  );
}
