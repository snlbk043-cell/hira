import { createItemApi } from "@/lib/tableApi";
import { walkthroughColumns } from "@/lib/schemas";

export const { PATCH, DELETE } = createItemApi("safety_walkthroughs", walkthroughColumns);
