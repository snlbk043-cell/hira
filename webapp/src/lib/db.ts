import { getDatabase } from "@netlify/database";

// Single shared driver instance; @netlify/database picks the right connection
// (pooled/direct) for whichever environment this code is running in.
export function db() {
  return getDatabase();
}
