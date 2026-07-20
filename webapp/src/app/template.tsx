/** Remounts on every navigation (unlike layout.tsx), giving every page a
 * consistent fade+rise entrance instead of an abrupt swap. */
export default function Template({ children }: { children: React.ReactNode }) {
  return <div className="page-enter">{children}</div>;
}
