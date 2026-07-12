# ttx_Schedule_SQL — Cheat Sheet

> Quick-reference for scheduled-SQL items: the WHAT of a scheduled SQL job.
> The WHEN is a `ttx_Schedule` time-config bound to it via `ScheduleItemID`.

## Checklist (before you call it done)
- [ ] Created under **`ttx_ScheduleTypes`** (the schedule-item category
      container).
- [ ] **`TrustedSQLID` references the `ttx_TrustedSQL` that runs** — this is
      the live convention: 9/9 rows bind via `TrustedSQLID`, and the
      `CMD` column is empty on every one (verified 2026-06-10). Put the SQL in
      the referenced TrustedSQL, not here.
- [ ] `cmdTimeout` sane for the workload.
- [ ] A `ttx_Schedule` time-config exists whose `ScheduleItemID` points at this
      item, with `IsActive=True` — without it the item never runs.

## Required relations
- **`TrustedSQLID`** → the `ttx_TrustedSQL` module holding the SQL (9/9 live
  rows use this path).
- **A `ttx_Schedule` bound via its `ScheduleItemID` column** — the join
  `ttx_Schedule.ScheduleItemID = ttx_Schedule_SQL.ID` is live-verified; the schedule's `ParentID` is empty on live rows.

## Parenting rules
- Valid parent (live app model): **`ttx_ScheduleTypes`**.
- The app model also lists `ttx_Schedule` as a valid child, but live schedule
  rows do NOT use tree parenting — the binding is the `ScheduleItemID` column
  (see Required relations). Both facts recorded; trust the column join.

## Gotchas
- **The `CMD` column is legacy** — 0 of 9 live rows carry inline SQL, and the
  platform creator confirmed it as legacy ("I did not know it existed" —
  Peter, 2026-06-10). Always bind via `TrustedSQLID`; never put SQL in `CMD`.
- The DATEFORMAT locale trap applies to the *referenced TrustedSQL's* body —
  use ISO-8601 `T`-separator date literals there; nobody is watching the
  German out-of-range error at 3am (see `cl howto ttx_TrustedSQL`).
- Live columns: `ID, Title, Description, ParentID, Created, LastUpdate,
  LastExecution, cmdTimeout, CMD, TrustedSQLID` (INFORMATION_SCHEMA). `LastExecution` here is the item-level run marker — the
  schedule's own `LastExecution`/`NextExecution` live on the time-config row.

## See also
- `cl howto ttx_Schedule` — the time-config child (inverted hierarchy explained)
- `cl howto ttx_TrustedSQL` — the referenced module type
- `cl howto ttx_Schedule_TrustedCode` / `ttx_Schedule_PackageTransfer` — siblings
- `cl schedulers` — CLI surface
