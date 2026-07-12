import { createTableApi } from "@/lib/tableApi";
import { trainingColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("training", "training_date", trainingColumns);
