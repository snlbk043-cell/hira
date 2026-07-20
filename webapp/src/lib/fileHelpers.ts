export function fileIcon(contentType: string) {
  if (contentType.startsWith("image/")) return "🖼️";
  if (contentType === "application/pdf") return "📕";
  if (contentType.includes("word")) return "📝";
  if (contentType.includes("sheet") || contentType.includes("excel")) return "📊";
  if (contentType.startsWith("video/")) return "🎥";
  return "📎";
}

export function formatSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
