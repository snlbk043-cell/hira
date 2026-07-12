import { createItemApi } from "@/lib/tableApi";
import { observationColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("hse_observations", observationColumns);
