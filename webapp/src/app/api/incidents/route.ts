import { createTableApi } from "@/lib/tableApi";
import { incidentColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("incidents", "incident_date", incidentColumns);
