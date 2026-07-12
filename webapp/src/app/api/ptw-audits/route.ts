import { createTableApi } from "@/lib/tableApi";
import { ptwAuditColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("ptw_audits", "audit_date", ptwAuditColumns);
