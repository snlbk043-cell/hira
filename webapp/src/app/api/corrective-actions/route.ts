import { createTableApi } from "@/lib/tableApi";
import { correctiveActionColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("corrective_actions", "date_raised", correctiveActionColumns);
