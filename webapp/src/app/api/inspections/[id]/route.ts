import { createItemApi } from "@/lib/tableApi";
import { inspectionColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("inspections", inspectionColumns);
