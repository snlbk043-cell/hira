"use client";
import { useEffect, useState, useCallback } from "react";
import { DEPARTMENTS } from "@/lib/constants";

export type Field = {
  name: string;
  label: string;
  type: "date" | "text" | "number" | "select" | "department";
  options?: string[];
  required?: boolean;
};

type Row = Record<string, string | number | boolean | null>;

export default function EntryPage({
  title,
  icon,
  endpoint,
  fields,
}: {
  title: string;
  icon: string;
  endpoint: string;
  fields: Field[];
}) {
  const [rows, setRows] = useState<Row[]>([]);
  const [loading, setLoading] = useState(true);
  const [form, setForm] = useState<Row>({});
  const [editingId, setEditingId] = useState<number | null>(null);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);

  const load = useCallback(() => {
    setLoading(true);
    fetch(`${endpoint}?limit=200`)
      .then((r) => r.json())
      .then(setRows)
      .finally(() => setLoading(false));
  }, [endpoint]);

  useEffect(() => { load(); }, [load]);

  function update(name: string, value: string) {
    setForm((f) => ({ ...f, [name]: value }));
  }

  async function submit(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true);
    setMessage(null);
    try {
      const url = editingId ? `${endpoint}/${editingId}` : endpoint;
      const method = editingId ? "PATCH" : "POST";
      const res = await fetch(url, {
        method,
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });
      if (!res.ok) {
        const err = await res.json().catch(() => ({}));
        throw new Error(err.error || `Request failed (${res.status})`);
      }
      setForm({});
      setEditingId(null);
      setMessage(editingId ? "Updated." : "Added.");
      load();
    } catch (err) {
      setMessage(String(err instanceof Error ? err.message : err));
    } finally {
      setSaving(false);
    }
  }

  function startEdit(row: Row) {
    setEditingId(Number(row.id));
    const f: Row = {};
    for (const field of fields) {
      const v = row[field.name];
      f[field.name] = field.type === "date" && typeof v === "string" ? v.slice(0, 10) : (v as string | number);
    }
    setForm(f);
    window.scrollTo({ top: 0, behavior: "smooth" });
  }

  async function remove(id: number) {
    if (!confirm("Delete this record?")) return;
    await fetch(`${endpoint}/${id}`, { method: "DELETE" });
    load();
  }

  return (
    <div className="max-w-6xl mx-auto p-4">
      <h1 className="text-2xl font-bold mb-1">{icon} {title}</h1>
      <p className="text-grey text-sm mb-4">{editingId ? "Editing record — update and save, or scroll down and cancel." : "Enter a new record below."}</p>

      <form onSubmit={submit} className="card p-4 mb-6 grid grid-cols-2 md:grid-cols-3 gap-3">
        {fields.map((f) => (
          <div key={f.name} className="flex flex-col gap-1">
            <label className="text-xs text-grey">{f.label}{f.required ? " *" : ""}</label>
            {f.type === "select" || f.type === "department" ? (
              <select
                required={f.required}
                value={(form[f.name] as string) || ""}
                onChange={(e) => update(f.name, e.target.value)}
              >
                <option value="">—</option>
                {(f.type === "department" ? DEPARTMENTS : f.options || []).map((o) => (
                  <option key={o} value={o}>{o}</option>
                ))}
              </select>
            ) : (
              <input
                type={f.type === "date" ? "date" : f.type === "number" ? "number" : "text"}
                required={f.required}
                value={(form[f.name] as string) ?? ""}
                onChange={(e) => update(f.name, e.target.value)}
              />
            )}
          </div>
        ))}
        <div className="col-span-2 md:col-span-3 flex items-center gap-3 mt-2">
          <button
            type="submit"
            disabled={saving}
            className="bg-teal text-[#0b1220] font-semibold px-4 py-2 rounded-md disabled:opacity-50"
          >
            {saving ? "Saving…" : editingId ? "Update record" : "Add record"}
          </button>
          {editingId && (
            <button
              type="button"
              onClick={() => { setEditingId(null); setForm({}); }}
              className="text-grey px-4 py-2 rounded-md border border-border"
            >
              Cancel
            </button>
          )}
          {message && <span className="text-sm text-grey">{message}</span>}
        </div>
      </form>

      <div className="card p-4">
        <div className="text-sm font-semibold mb-3">Recent records ({rows.length})</div>
        {loading ? (
          <p className="text-grey text-sm">Loading…</p>
        ) : rows.length === 0 ? (
          <p className="text-grey text-sm">No records yet.</p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr>
                  {fields.map((f) => <th key={f.name} className="text-left p-2 text-grey whitespace-nowrap">{f.label}</th>)}
                  <th className="p-2"></th>
                </tr>
              </thead>
              <tbody>
                {rows.map((row) => (
                  <tr key={String(row.id)} className="border-t border-border">
                    {fields.map((f) => (
                      <td key={f.name} className="p-2 whitespace-nowrap">
                        {f.type === "date" && row[f.name] ? String(row[f.name]).slice(0, 10) : String(row[f.name] ?? "")}
                      </td>
                    ))}
                    <td className="p-2 whitespace-nowrap">
                      <button onClick={() => startEdit(row)} className="text-teal mr-3">Edit</button>
                      <button onClick={() => remove(Number(row.id))} className="text-coral">Delete</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
