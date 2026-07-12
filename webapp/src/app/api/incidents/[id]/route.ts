import { createItemApi } from "@/lib/tableApi";
import { incidentColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("incidents", incidentColumns);
