import { createItemApi } from "@/lib/tableApi";
import { ptwAuditColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("ptw_audits", ptwAuditColumns);
