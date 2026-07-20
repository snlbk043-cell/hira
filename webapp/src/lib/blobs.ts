import { getStore } from "@netlify/blobs";

/** Single shared blob store for all tracker evidence/photo uploads (any file
 * type - PDFs, images, docs). Keyed as `${trackerKey}/${recordId}/${uuid}-${filename}`
 * so listing/deleting by tracker+record is a simple prefix operation. */
export function attachmentsStore() {
  return getStore("attachments");
}
