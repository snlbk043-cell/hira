# RCPL Safety Dashboard (web app)

A real, hosted Executive & Leadership safety dashboard — day-wise/month-wise data
entry with live-updating KPIs, trends, and infographics. Built with Next.js and
deployed on Netlify with a managed Postgres database (Netlify DB / Neon).

**Live:** https://rcpl-ehs-safety-dashboard.netlify.app

## What's here

- `src/app/dashboard/executive` — KPI wall, Incident Pyramid, TRIR/LTIFR trend,
  Leading-vs-Lagging trend, Root-Cause Pareto, Classification mix.
- `src/app/dashboard/leadership` — Department League Table, System-Wide Action
  Backlog, Risk Rating × Department matrix, auto-generated insights.
- `src/app/entry/*` — day-wise data-entry forms + editable tables for the 8
  tracked categories: Incidents, Training, HSE Observations, Inspections,
  Safety Walkthroughs, Corrective Actions, PTW Audits, Risk Assessments (JSA).
- `src/app/settings` — TRIR/LTIFR targets, industry benchmarks, monthly
  man-hours, and the one-time Excel-data import button.
- `src/app/api/*` — REST API routes (CRUD per register + `/api/summary`, the
  aggregation engine that computes every dashboard number live from whatever's
  in the database).
- `netlify/database/migrations/001_init` — the Postgres schema. Netlify runs
  this automatically on every deploy.
- `src/data/seed/registers.json` — the real register data from the original
  Excel workbook, used by `/api/seed` (POST) to seed history on first deploy.
  Idempotent — safe to call more than once.

## Local development

```bash
npm install
npm run dev
```

Note: local `npm run dev` runs the Next.js app but won't have a live database
connection unless you're authenticated with the Netlify CLI and linked to the
site (`netlify link`, then `netlify dev`). Without that, API routes that touch
the database will fail locally — this is expected; test against the deployed
site instead, or link the CLI.

## Deploying

This site is deployed via the Netlify MCP tooling / `netlify-cli`, not a
git-triggered build (the site isn't connected to auto-deploy on push). To ship
a change:

```bash
cd webapp
npm run build   # sanity-check the build locally first
# then deploy via whichever Netlify tooling is available in your session
```

## Design notes

- Kept deliberately separate from the pre-existing HIRA generator at the repo
  root (`index.html` + `netlify/functions/claude.js`) — different Netlify
  site, different purpose, never touched by this app.
- The data model here is a trimmed version of the 24-tracker Excel system —
  just the 8 categories that drive Executive/Leadership decisions, not the
  full register set. The Excel workbook (`../dashboard/`) remains the
  full-detail, offline-first system; this app is the live, always-on
  companion for day-to-day entry and board-level review.
- `/api/summary` re-implements the same TRIR/LTIFR/leading-lagging/department-
  score logic as the Excel Calculations sheet, as SQL aggregation instead of
  spreadsheet formulas.
