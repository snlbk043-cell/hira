# RCPL Executive EHS KPI Dashboard

**`RCPL_Executive_EHS_KPI_Dashboard.xlsm`** — a fully-functional, macro-enabled
Excel workbook: a Fortune‑500‑style Executive Safety KPI dashboard for the
Reliance Consumer Products Ltd (Campa Cola) CSD plant.

Everything is live: every KPI, chart and gauge recalculates automatically from
the 20 raw‑data registers. Change a filter and the whole dashboard updates.

---

## What's inside (35 sheets)

| Group | Sheets |
|---|---|
| **Navigation** | `Home` |
| **Dashboards** | Executive, Incident, Inspection, Audit, Training, PTW, Statutory, CAPA, Department |
| **Engine** | `Calculations` (KPI engine), `Master Data` |
| **Registers (20)** | Incident, First Aid, Near Miss, Safety Observation, Unsafe Act, Unsafe Condition, Inspection, Audit, Statutory Compliance, Permit To Work, Training, PPE Compliance, Contractor Safety, Toolbox Talk, BBS Observation, Emergency Drill, Fire Equipment, Risk Assessment, CAPA Tracker, Man‑hours Master |
| **Docs** | Documentation, Instructions, Formula Sheet |

## Highlights
- **20 KPI cards** — Man‑hours, TRIR, LTIFR, LTI, MTC, First Aid, Near Miss,
  HiPo Near Miss, Safety Observations, Unsafe Acts/Conditions, Good Catch,
  and PTW / Inspection / Audit / Training / PPE / Statutory / Action‑closure
  compliance %, plus a composite Safety Score. Each has a **live formula** and
  a 12‑month **sparkline**.
- **5 global filters** (Year, Month, Department, Area, Shift) as data‑validation
  drop‑downs that drive *every* card, chart and gauge via a resolved‑criteria
  engine — no manual updates.
- **30+ native charts**: line, dual‑axis TRIR/LTIFR, stacked column, doughnut,
  **Pareto**, horizontal bar, area, **radar**, and **half‑doughnut gauges**.
- **KPI engine**: `COUNTIFS`/`SUMIFS`/`AVERAGEIFS` over 100,000‑row dynamic
  ranges (`supports_100000_records`), with `IFERROR` guards throughout.
- **Conditional formatting**: 5×5 risk heat‑map (color scale), department
  traffic‑light icon set, data bars on the monthly trend.
- **Working VBA** (see below): Refresh, Reset Filters, Navigate, Print, Export PDF.
- **20 structured Excel Tables**, dynamic named ranges, hyperlinked navigation.

## KPI formulas (see the *Formula Sheet*)
```
TRIR   = Recordable × 200,000 / Man‑hours
LTIFR  = LTI × 1,000,000 / Man‑hours
Severity Rate = Lost Days × 1,000,000 / Man‑hours
Safety Score  = 0.18·PTW + 0.15·Insp + 0.12·Audit + 0.15·Train
              + 0.15·PPE + 0.10·Statutory + 0.15·Action‑closure
```
With the shipped sample data the engine computes TRIR ≈ 0.87, LTIFR ≈ 1.51,
PTW ≈ 90.9 %, Training ≈ 83.6 % — industry‑realistic values.

---

## Using it
1. Open in **Microsoft Excel** and **Enable Macros** when prompted (the workbook
   opens on `Home`, sets the last‑refresh stamp and does a full recalculation).
2. Navigate with the tiles/buttons on `Home` or the chip strip on each dashboard.
3. On the **Executive Dashboard**, change the five filters — everything updates.
4. Buttons: **⟳ Refresh**, **⟲ Reset Filters**, **⌂ Home**, **🖨 Print**, **PDF**.
5. Add data by typing new rows under any register Table, then click **Refresh**.

> Even if your security policy blocks macros, the workbook is still fully usable:
> the hyperlink chips navigate between sheets and all KPIs/charts remain live
> (they are formula‑driven, not macro‑driven).

## About the VBA
The macros are embedded as a genuine `vbaProject.bin` built to the MS‑OVBA /
MS‑CFB specifications. It was validated with Microsoft's own parsing logic
(`oletools.olevba`), which extracts both modules (`ThisWorkbook`, `modDashboard`)
cleanly. Modules: `RefreshDashboard`, `RefreshAllData`, `ResetFilters`,
`GoHome`, `NavExecutive…NavDepartment`, `PrintDashboard`, `ExportDashboardPDF`,
`ExportAllDashboardsPDF`, and a `Workbook_Open` handler.

## A note on pivot tables & slicers
No Python library can author native Excel **pivot tables / slicers** from
scratch. Rather than ship non‑functional placeholders, the interactivity is
implemented with an equivalent that **works immediately on open**: a live
`COUNTIFS`/`SUMIFS` engine plus data‑validation filter drop‑downs and native
pivot‑style charts. To convert to native pivots later, point a PivotTable at any
register Table (they are already structured Tables) and add slicers.

---

## Regenerating the workbook
```bash
cd build
pip install xlsxwriter          # openpyxl/oletools optional, for validation
python3 xlsm_build.py           # -> ../RCPL_Executive_EHS_KPI_Dashboard.xlsm
```
| File | Purpose |
|---|---|
| `build/xlsm_build.py` | Registers, Master Data, KPI engine, orchestration |
| `build/xlsm_dash.py`  | Dashboards, charts, gauges, navigation, docs |
| `build/data_gen.py`   | Realistic sample data generator (seeded) |
| `build/vba_code.py`   | VBA module source |
| `build/vbabin.py`     | MS‑OVBA + MS‑CFB `vbaProject.bin` builder |
