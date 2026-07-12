# ttx_Schedule_TrustedCode — Cheat Sheet

> Quick-reference for scheduled-TrustedCode items: the WHAT of a scheduled
> script job. The WHEN is a `ttx_Schedule` time-config bound to it via
> `ScheduleItemID`.

## Checklist (before you call it done)
- [ ] Created under **`ttx_ScheduleTypes`**.
- [ ] `TrustedCodeID` references the TrustedScript to run (the script holds the
      logic; this item only binds it to the scheduler).
- [ ] A `ttx_Schedule` time-config exists whose `ScheduleItemID` points at this
      item, with `IsActive=True`.
- [ ] The referenced script passes `cl validate-script <uuid>` — a JIT error in
      a scheduled script surfaces only in the system log.

## Required relations
- **`TrustedCodeID`** → the `ttx_TrustedScript` that runs.
- **A `ttx_Schedule` bound via its `ScheduleItemID` column** — live schedule
  rows carry an empty ParentID; the column join is the real binding (see
  `cl howto ttx_Schedule`).

## Parenting rules
- Valid parent (live app model): **`ttx_ScheduleTypes`**.
  The app model also lists `ttx_Schedule` as a valid child, but live binding
  runs through `ScheduleItemID`, not tree parenting.

## Gotchas
- This item is a thin binding — live columns are only `ID, Title, Description,
  ParentID, Created, LastUpdate, LastExecution, TrustedCodeID`
  (INFORMATION_SCHEMA). All execution behavior (timeouts,
  dependencies, JIT invariants) belongs to the referenced TrustedScript.
- Scheduled scripts fail silently from the user's perspective — check
  `cl syslog` (auto-limited) rather than waiting for output; the Workflow
  monitor (`17809a33`) and Scheduler monitor (`74ea96ac`) are the watch
  surfaces (project memory).

## See also
- `cl howto ttx_Schedule` — the time-config child
- `cl howto ttx_TrustedScript` — everything about the referenced script
- `cl howto ttx_Schedule_SQL` / `ttx_Schedule_PackageTransfer` — siblings
