# RCPL EHS Dashboards

Two deliverables live here:

1. **`RCPL_Integrated_EHS_Management_System.xlsm`** — the full enterprise EHS system
   (24 registers + 24 dashboards + Executive + Leadership + Settings + Help). *Latest.*
2. **`RCPL_Executive_EHS_KPI_Dashboard.xlsm`** — the original single executive dashboard.

---

# RCPL Integrated EHS Management System  *(RCPL_Integrated_EHS_Management_System.xlsm)*

A complete, single-workbook corporate EHS system — structure adopted from the client's
`HSE_Full_System.xlsx` and rebuilt as a fully **live, formula-driven, macro-enabled**
workbook (55 sheets).

## Gap analysis → what was added
The original executive dashboard covered incidents, inspections, audits, training, PTW,
statutory, CAPA. Integrating the client's HSE structure added the **missing registers &
their dashboards**: Safety Walkthroughs, Safety Meetings, Safety Bulletins, Management
Visits, Management Reviews, Disciplinary Actions, Safety Awards, Stop Work Authority,
Alcohol Tests, PTW Audits, NC Management, JSA Risk Assessment, HSE Observations,
Corrective Actions, Internal/External Audits (split), plus **Leadership Review, Settings
and Help** sheets.

## Structure (55 sheets)
| Group | Sheets |
|---|---|
| **Navigation** | `Home` |
| **Rollups** | `Executive Dashboard`, `Leadership Review` |
| **Per-register dashboards (24)** | `Dash · <register>` — one interactive dashboard per register |
| **Registers (24)** | Toolbox Talks, JSA Risk Assessment, Training, HSE Observations, Workplace/Equipment Inspections, Safety Walkthroughs, Safety Meetings, Safety Bulletins, Emergency Drills, Internal/External Audits, Management Visits/Reviews, Disciplinary Actions, Safety Awards, Stop Work Authority, Alcohol Tests, PTW Audits, Corrective Actions, NC Management, Unsafe Acts/Conditions, Incident |
| **Engine & config** | `Calculations`, `Master Data`, `Settings`, `Help` |

## Round 5: per-tracker slicers, real RAG-vs-target on every card, sparklines, radar upgrade,
## department data bars, Top Movers, print-ready layout
- **Per-tracker slicers** — a "🎚 Add Tracker Slicers" button (Home) adds a real, Table-bound
  Department slicer to each of the 21 tracker dashboards whose register has a Department
  column (Bulletins/Drills/Management Reviews don't), independent of the Executive filters.
- **RAG-vs-target on every one of the ~49 KPI cards** — not just the variance arrow. Each
  card's coloured strip is now a live 🟢🟡🔴 status against a real target: percentage KPIs
  compare to explicit corporate targets on Settings (extended with PTW/close-out/attendance/
  alcohol targets), and every count-based KPI (leading activity volumes, lagging incident
  counts) compares against an auto-computed rolling 12-month baseline scaled to the selected
  period — no arbitrary numbers invented, and every card is genuinely evaluated.
- **Sparklines on every KPI card** (Executive + Leadership) — a 12-month inline trend line,
  including on ratio/percentage metrics (which needed new monthly ratio series to support it).
- **Radar chart upgrade** — now plots Actual vs Target as two overlaid rings across 8 axes
  (was 6, value-only).
- **Live Department Performance table** on every tracker dashboard (was chart-only before),
  with a data bar on the Count column for instant ranking.
- **Monthly Performance Matrix RAG colouring** — percentage rows get a green-amber-red colour
  scale across their own 12 months so a missed month jumps out immediately.
- **Top Movers panel** on Leadership Review — the 3 best-improving and 3 worst-regressing KPIs
  this period, ranked by normalised %Δ×polarity so metrics of very different scale are
  comparable (a lagging metric's improvement and a leading metric's improvement rank on the
  same footing).
- **Print-ready layout** — landscape, fit-to-1-page-wide, bounded print areas on every
  dashboard sheet; registers repeat their 3-row header on each printed page.

## Round 4: native pivot tables, sheet protection, real monthly man-hours, board pack
- **Native PivotTables + Slicers** — a "📊 Build Pivot Analysis" button on Home runs a VBA
  macro that creates three genuine, fully-interactive Excel PivotTables (Incident, Training,
  Corrective Actions) with Slicers, built from the real Tables — not a formula substitute.
  Re-runnable any time; rebuilds the sheet fresh.
- **Sheet protection** — every formula/label cell is locked; only genuine input cells (each
  register's data-entry columns, Settings' amber parameters, the Executive filter drop-downs)
  stay editable. Applied via VBA with `UserInterfaceOnly:=True` so the macros themselves can
  still write (refresh stamps, filter resets) while a human can't accidentally overwrite a
  formula. A "🔓 Unlock Sheets to Edit" button is provided for anyone who needs to restructure.
- **Real monthly man-hours** — Settings now has an editable Jan–Dec man-hours table (instead
  of one flat annual number ÷ 12). TRIR/LTIFR use the exact hours for whatever period is
  selected, so a low-hours month (e.g. a shutdown) no longer distorts the rate.
- **Board Pack PDF** — a new Cover Page + "📦 Export Board Pack" button combines the Cover,
  Executive Dashboard and Leadership Review into one ready-to-send PDF.
- **Fixed a real range-limit bug**: formula ranges were capped at 5,000 rows (contradicting
  the "supports 100,000 records" claim); now genuinely 100,000. Auto-calculated columns
  (Attendance %, Ageing, Timeliness, etc.) are also pre-filled with live formulas 1,000 rows
  deep so new data entered below the sample rows works immediately without copying formulas.

## Round 3: every tracker on the Executive Dashboard + rich per-tracker analysis (131 charts)
- **Executive Dashboard KPI wall** now carries a headline KPI from **all 24 trackers** (not
  a subset) — e.g. Toolbox Talks (# + Avg Attendance %), JSA (# + % Approved), Workplace/
  Equipment Inspections (# + Closure %/Critical Findings), Safety Meetings/Bulletins/Visits/
  Reviews (# + Close-out %/Reach %/Attendance %), Internal/External Audits (# + NCs), Safety
  Awards, Stop Work Authority, Alcohol Tests (+ Positive % on the lagging side), Unsafe Act/
  Condition reporting + closure %, NC Management closure %, alongside the incident-driven
  lagging KPIs (TRIR, LTIFR, Recordable, Near Miss, First Aid, Lost Days, Disciplinary). ~49
  variance cards total, split into 🟥 Lagging / 🟩 Leading bands — **every card is a hyperlink
  that drills straight into that tracker's own dashboard.**
- **Full RCPL executive chart suite** — all of the following are on the Executive Dashboard,
  none missing: Monthly Incident Trend, First Aid Trend, Near Miss Trend, TRIR & LTIFR Trend
  (dual-axis), Unsafe Act vs Unsafe Condition (stacked), Incident Classification (doughnut),
  Root Cause Pareto, Department-wise Safety Score, Safety Observation Trend (area), Monthly
  Performance Radar, Heinrich Incident Pyramid, Risk Heat Map (5×5-style, colour-scaled), Top
  10 Unsafe Acts / Unsafe Conditions / High-Risk Areas, and 6 compliance gauges (Training,
  PTW, Obs Closure, CA Closure, Inspection Closure, NC Closure).
- **Every one of the 24 tracker dashboards** now mirrors the client's own `Dashboard – X`
  analysis layout: **8 KPI tiles** (volume/status row + tracker-specific metrics row),
  Monthly Volume + primary Category Breakdown + secondary Distribution charts, a Department
  Performance chart, and a live **Monthly Performance Matrix** (key measures × Jan–Dec + YTD).

## What's live
- **Registers** keep the client's exact column layout with a 3-row header (emoji title /
  legend / column headers), structured Tables, dropdown validation from **Master Data**,
  and **auto-calculated** columns (Attendance %, Close-out %, Reach %, Compliance %,
  Incident Ageing, CA Timeliness) written as formulas.
- **Executive Dashboard** — RCPL-card style with a **period-on-period variance engine**:
  pick a **Period** (any month → vs previous month, or Q1–Q4 → vs previous quarter) and a
  Department; every KPI card shows the current value, the prior-period value and a
  **▲/▼ Δ% vs prior** indicator that is **polarity-coloured** (for lagging metrics a drop is
  green, for leading metrics a rise is green). Cards are split into two clearly-labelled
  bands — **🟥 LAGGING** (TRIR, LTIFR, incidents, recordable, LTI+fatality, near miss, first
  aid, lost days, disciplinary, open NCs) and **🟩 LEADING** (trainings, training compliance,
  observations, obs closure, toolbox, inspections, audits, PTW compliance, drills, CA
  closure). Plus leading-vs-lagging bar pair, a **Heinrich incident pyramid**, 12-month
  trend, four compliance **gauges** and a **RAG (🟢🟡🔴) scorecard** vs the Settings targets.
- **Leadership Review** — condensed corporate scorecard + incident severity mix + trends.
- **24 per-register dashboards** — each with KPI tiles (total, closure %, key metric),
  monthly-volume, category-breakdown and status-distribution charts, all `COUNTIFS`-driven.
- **Settings** — man-hours, TRIR/LTIFR multipliers and RAG targets as named cells; change
  a value and every rate/RAG light updates (the client file showed `#NAME?` here — fixed).
- **Working VBA** — Refresh, Reset Filters, Home, Print, Export PDF; hyperlink navigation
  throughout. Same MS-OVBA/MS-CFB builder, validated with `oletools`.

With the shipped sample data the engine computes a realistic pyramid (≈29 near-miss → 1 LTI),
TRIR ≈ 2.2, LTIFR ≈ 2.0, Training completion ≈ 62 %.

## Regenerating
```bash
cd build && python3 hse_build.py   # -> ../RCPL_Integrated_EHS_Management_System.xlsm
```
`hse_data.py` (specs + sample data), `hse_build.py` (registers/engine/config),
`hse_dash.py` (dashboards), `vba_code_hse.py` (VBA), `vbabin.py` (vbaProject.bin builder).

---

# RCPL Executive EHS KPI Dashboard  *(RCPL_Executive_EHS_KPI_Dashboard.xlsm)*

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
