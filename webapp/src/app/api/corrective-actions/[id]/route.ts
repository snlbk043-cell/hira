import { createItemApi } from "@/lib/tableApi";
import { correctiveActionColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("corrective_actions", correctiveActionColumns);
