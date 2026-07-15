import type { TrackerDef } from "./trackers";
import type { Row, Kpi, ChartSpec } from "./aggregate";

/** PDF: the browser's native print-to-PDF, driven by the @media print rules in
 * globals.css (hides the sidebar/buttons, forces readable colours). No server
 * rendering needed, works reliably in a serverless deployment. */
export function exportTrackerPdf() {
  window.print();
}

function downloadBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** PPT: a real, editable .pptx - KPI table + one native (not image) chart per
 * chart on the page, built directly from the same aggregated numbers shown on
 * screen so the export always matches what's currently visible. */
export async function exportTrackerPpt(tracker: TrackerDef, snapshot: { kpis: Kpi[]; charts: ChartSpec[] }) {
  const PptxGenJS = (await import("pptxgenjs")).default;
  const pptx = new PptxGenJS();
  pptx.defineLayout({ name: "RCPL", width: 10, height: 5.63 });
  pptx.layout = "RCPL";

  const NAVY = "0B1220", CARD = "111C33", TEAL = "14B8A6", TXT = "E5E9F0", MUTED = "93A2BE";

  // Title slide
  const title = pptx.addSlide();
  title.background = { color: NAVY };
  title.addText(`${tracker.icon}  ${tracker.label}`, { x: 0.6, y: 2.0, w: 8.8, h: 1, fontSize: 32, bold: true, color: TXT, fontFace: "Segoe UI" });
  title.addText(tracker.description, { x: 0.6, y: 2.9, w: 8.8, h: 0.6, fontSize: 14, color: TEAL, fontFace: "Segoe UI" });
  title.addText(`RCPL — Campa Cola CSD Plant  ·  generated ${new Date().toLocaleDateString()}`, { x: 0.6, y: 4.9, w: 8.8, h: 0.4, fontSize: 10, color: MUTED, fontFace: "Segoe UI" });

  // KPI slide
  const kpiSlide = pptx.addSlide();
  kpiSlide.background = { color: NAVY };
  kpiSlide.addText("Headline KPIs", { x: 0.5, y: 0.3, fontSize: 20, bold: true, color: TEAL, fontFace: "Segoe UI" });
  const kpiRows = [
    [{ text: "Metric", options: { bold: true, color: NAVY, fill: { color: TEAL } } }, { text: "Value", options: { bold: true, color: NAVY, fill: { color: TEAL } } }],
    ...snapshot.kpis.map((k) => [
      { text: `${k.icon}  ${k.label}`, options: { color: TXT, fill: { color: CARD } } },
      { text: k.value, options: { color: TXT, fill: { color: CARD }, bold: true } },
    ]),
  ];
  kpiSlide.addTable(kpiRows, { x: 0.5, y: 0.9, w: 9, colW: [6, 3], fontSize: 12, fontFace: "Segoe UI", border: { type: "solid", color: "22314F", pt: 1 } });

  // one slide per chart, native pptxgenjs chart
  for (const c of snapshot.charts) {
    const slide = pptx.addSlide();
    slide.background = { color: NAVY };
    slide.addText(c.title, { x: 0.5, y: 0.3, fontSize: 18, bold: true, color: TEAL, fontFace: "Segoe UI" });
    const labels = c.data.map((d) => d.label);
    const values = c.data.map((d) => d.value);
    const chartData = [{ name: c.title, labels, values }];
    const chartType = c.type === "trend" ? pptx.ChartType.line : c.type === "donut" ? pptx.ChartType.pie : pptx.ChartType.bar;
    slide.addChart(chartType, chartData, {
      x: 0.5, y: 1.0, w: 9, h: 4.3,
      chartColors: ["14B8A6", "F5A524", "F0625A", "8B5CF6", "0B6EA8", "22C55E", "EAB308", "94A3B8"],
      showLegend: c.type === "donut",
      showTitle: false,
      dataLabelColor: TXT,
      catAxisLabelColor: MUTED,
      valAxisLabelColor: MUTED,
      chartColorsOpacity: 100,
    });
  }

  await pptx.writeFile({ fileName: `RCPL_${tracker.key}_report.pptx` });
}

/** Excel: raw records (exact column headers, same shape as the Excel registers
 * this replaces) so the export can be handed off / archived like any other
 * register extract. */
export async function exportTrackerExcel(tracker: TrackerDef, rows: Row[]) {
  const ExcelJS = (await import("exceljs")).default;
  const wb = new ExcelJS.Workbook();
  wb.creator = "RCPL EHS Dashboard";
  wb.created = new Date();

  const sheet = wb.addWorksheet(tracker.label.slice(0, 31));
  sheet.columns = tracker.fields.map((f) => ({ header: f.label, key: f.name, width: Math.max(14, f.label.length + 2) }));
  sheet.getRow(1).font = { bold: true, color: { argb: "FFFFFFFF" } };
  sheet.getRow(1).fill = { type: "pattern", pattern: "solid", fgColor: { argb: "FF14B8A6" } };
  for (const r of rows) {
    const record: Record<string, unknown> = {};
    for (const f of tracker.fields) {
      const v = r[f.name];
      record[f.name] = f.type === "date" && typeof v === "string" ? v.slice(0, 10) : v;
    }
    sheet.addRow(record);
  }
  sheet.autoFilter = { from: "A1", to: `${String.fromCharCode(64 + tracker.fields.length)}1` };

  const buf = await wb.xlsx.writeBuffer();
  downloadBlob(new Blob([buf], { type: "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" }), `RCPL_${tracker.key}_export.xlsx`);
}
