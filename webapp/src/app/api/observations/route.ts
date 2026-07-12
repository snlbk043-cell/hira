import { createTableApi } from "@/lib/tableApi";
import { observationColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("hse_observations", "obs_date", observationColumns);
