"use client";
import { useEffect, useState } from "react";
import { Summary } from "./types";

export function useSummary(year: number, department: string, month: number = 0) {
  const [data, setData] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    fetch(`/api/summary?year=${year}&department=${encodeURIComponent(department)}&month=${month}`)
      .then((r) => {
        if (!r.ok) throw new Error(`summary fetch failed: ${r.status}`);
        return r.json();
      })
      .then((json) => {
        if (!cancelled) { setData(json); setError(null); }
      })
      .catch((e) => {
        if (!cancelled) setError(String(e));
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });
    return () => { cancelled = true; };
  }, [year, department, month]);

  return { data, loading, error };
}
