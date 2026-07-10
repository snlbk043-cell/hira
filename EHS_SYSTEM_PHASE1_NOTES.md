# Enterprise EHS Management System — Phase 1

Deliverable: **`HSE_Full_System.xlsx`** (enhanced from the uploaded `HSE_Full_System_1.xlsx`).

Phase 1 focused on the highest-value, lowest-risk improvements: fixing a critical
scalability bug and introducing centralized master data — **without removing or
degrading any existing feature**. All 93 charts, 115 conditional-formatting rules,
styling, tab colors, and the original data-entry UX are preserved intact.

## What changed

### 1. Fixed the critical 20-row scalability bug 🔴→✅
Every dashboard previously read only rows `6:25` of its register (20 records),
even though data validation allowed entry down to row 506. **Records 21+ were
silently dropped from every KPI and chart.**

- Repaired **2,626 formula ranges** across all 23 dashboards: `$6:$25 → $6:$506`.
- Two-criteria `COUNTIFS` and single `COUNTIF/SUM/AVERAGE` ranges all corrected.
- Result: dashboards now scale to **500+ records** per register automatically.

### 2. Centralized Master Data (new `01_Master_Data` sheet)
- Consolidated all **44 distinct dropdown lists** (previously hard-coded inside
  each of the 100 data-validation rules) into one maintainable sheet.
- Each list is exposed as a **non-volatile dynamic named range** using
  `INDEX()`+`COUNTA()` (per the "avoid volatile formulas" requirement — no
  `OFFSET`). Lists auto-grow up to 100 items.
- **Re-pointed all 100 data-validation dropdowns** to these named ranges.
  Adding a new Department/Location/Status now means editing **one cell**, not ~40.

### 3. Auto-formula fill-down (scalable data entry)
- Extended `S.No`, `Month`, `Attendance %` and other `⚙️ AUTO` columns down to
  row 506 on all 23 registers (**11,178 rows** seeded).
- New formulas are guarded (`=IF($B{row}="","", …)`) so blank rows stay clean —
  columns auto-calculate the moment a new record's Ref No. is entered.

### 4. Recalculate-on-open
- `fullCalcOnLoad` enabled so all rebuilt formulas populate immediately in Excel.

## Integrity verification
| Check | Original | Phase 1 |
|---|---|---|
| Chart objects | 93 | 93 ✅ |
| Conditional-formatting blocks | 115 | 115 ✅ |
| Sheets | 46 | 47 (+ `01_Master_Data`) |
| Existing sample data / formulas | — | untouched ✅ |

## Roadmap (proposed, pending approval)
- **Phase 2** — Add missing registers (Incident, Near Miss, First Aid, MTC, RWC,
  LTI, Fatality, Environmental, Fire, Chemical Spill, CAPA, Legal, Waste/Water/Energy,
  additional inspection types) using the established design + master data.
- **Phase 3** — Enrich action-tracking registers with risk matrix, priority,
  ageing, target/closure dates, week/quarter/FY, production line, shift, root cause.
- **Phase 4** — `06_Executive_Dashboard`: TRIR, LTIFR, incident pyramid, RAG,
  leading/lagging indicators, 12-month trend, forecast.
- **Phase 5** — Interactivity (slicers, timeline), `08_Settings`, `09_Help`,
  print/report layouts, and Power Query/Power Pivot foundation for Power BI.
