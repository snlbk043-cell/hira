import { createTableApi } from "@/lib/tableApi";
import { walkthroughColumns } from "@/lib/schemas";

export const { GET, POST } = createTableApi("safety_walkthroughs", "walk_date", walkthroughColumns);
