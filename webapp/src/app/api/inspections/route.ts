import { createTableApi } from "@/lib/tableApi";
import { inspectionColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("inspections", "inspection_date", inspectionColumns);
