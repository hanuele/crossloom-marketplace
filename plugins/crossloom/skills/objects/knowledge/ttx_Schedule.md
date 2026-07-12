# ttx_Schedule — Cheat Sheet

> Quick-reference for schedule time-configs. **The direction is inverted from
> what you'd guess**: a `ttx_Schedule` (the WHEN) is *bound to* the schedule
> item (the WHAT — `ttx_Schedule_SQL`, `_TrustedCode`, `_PackageTransfer`,
> ...) via its `ScheduleItemID` column. You attach a time-config to a job,
> not a job to a timer.

## Checklist (before you call it done)
- [ ] **`ScheduleItemID` points at the job item** (the `_SQL`/`_TrustedCode`/
      `_PackageTransfer`/... object that defines what runs) and
      `ScheduleTypeID` at that item's type — this is the live binding; the
      schedule's `ParentID` is empty on live rows.
- [ ] `Interval` + `IntervalType` set; `RunOnce` decided.
- [ ] `IsActive` set deliberately — an inactive schedule is the silent
      "why doesn't it run" cause.
- [ ] `ExecuteUntil` set if the job must stop recurring at a date.

## Required relations
- **`ScheduleItemID` → the schedule item** — live-verified join
  (2026-06-10): `ttx_Schedule.ScheduleItemID = ttx_Schedule_SQL.ID` resolves
  every active SQL schedule. `ScheduleTypeID` carries the item's type;
  `ScheduleWorkerID` ties execution to a worker.

## Parenting rules
- The app model lists six valid item-type parents
  (`ttx_Schedule_SQL`, `_TrustedCode`, `_PackageTransfer`, `_Workflow`,
  `_Queue`, `_ActiveDirectory_Import`) — but **live rows carry an empty
  ParentID and bind via the `ScheduleItemID` column** (confirmed by Peter,
  platform creator, 2026-06-10). General principle: `ParentID` is a standard
  field (like ID/Title/Description/Created/LastUpdate) that the app model
  uses *naturally* when a type can have multiple parent ObjectTypes; a
  dedicated binding column (here `ScheduleItemID`) takes its place when the
  relation is specific. When reading or writing schedules, trust the column
  join, not the tree. The items themselves live under `ttx_ScheduleTypes`
  (see the item sheets).

## Gotchas
- **`ttx_Schedule` and `ttx_Scheduler` are different tables.** Time configs
  live in `ttx_Schedule`; the scheduler *service* configs live in
  `ttx_Scheduler`. Querying the wrong one returns confusing data.
- `LastExecution` / `NextExecution` are the run-state columns — check them
  before debugging a job that "never fires" (often: `IsActive` false or
  `NextExecution` in the past with no worker).
- Live columns: `ID, Title, Description, Created, LastUpdate, LastExecution,
  NextExecution, ExecuteUntil, Interval, IntervalType, ScheduleTypeID,
  ScheduleItemID, IsActive, RunOnce, ScheduleWorkerID, ParentID`
  (INFORMATION_SCHEMA).

## See also
- `cl schedulers` — list and manage schedules from the CLI
- `cl howto ttx_Schedule_SQL` / `ttx_Schedule_TrustedCode` /
  `ttx_Schedule_PackageTransfer` — the item siblings
- Scheduler monitor object: `74ea96ac` (project memory)
