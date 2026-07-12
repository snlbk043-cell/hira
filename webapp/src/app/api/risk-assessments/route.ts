import { createTableApi } from "@/lib/tableApi";
import { riskAssessmentColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("risk_assessments", "assessment_date", riskAssessmentColumns);
