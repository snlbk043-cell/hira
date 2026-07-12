import { createItemApi } from "@/lib/tableApi";
import { trainingColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("training", trainingColumns);
