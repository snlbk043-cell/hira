import { createItemApi } from "@/lib/tableApi";
import { riskAssessmentColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("risk_assessments", riskAssessmentColumns);
