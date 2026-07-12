# ttx_Schedule_PackageTransfer — Cheat Sheet

> Quick-reference for scheduled package transfers: the WHAT of an automated
> stage-promotion job (export from source, import to destination). The WHEN is
> a `ttx_Schedule` time-config bound to it via `ScheduleItemID`.

## Checklist (before you call it done)
- [ ] Created under **`ttx_ScheduleTypes`**.
- [ ] `ExportDefinitionCollectionID` points at the Package definition to
      transfer.
- [ ] Source and destination configured deliberately: `Source_ServiceURL` /
      `Source_ConnectionID` / `Source_PackageID` / `Source_PackageType` and
      `Destination_ServiceURL` / `Destination_ConnectionID`.
- [ ] `Validate_Certificate` decided (security posture, not a convenience flag).
- [ ] `Timeout` sane for the package size.
- [ ] A `ttx_Schedule` time-config exists whose `ScheduleItemID` points at this
      item, with `IsActive=True`.

## Required relations
- **`ExportDefinitionCollectionID`** → the Package authoring object (see
  `cl howto ttx_ExportDefinitionCollection`).
- **A `ttx_Schedule` bound via its `ScheduleItemID` column** — live schedule
  rows carry an empty ParentID; the column join is the real binding (see
  `cl howto ttx_Schedule`).
- Source/Destination credentials: `Source_Username`/`Source_Password` and
  `Destination_Username`/`Destination_Password` columns exist — treat rows of
  this type as **credential-bearing** (handle like `ttx_Credential`-adjacent
  data; don't paste row dumps into tickets or chat).

## Parenting rules
- Valid parent (live app model): **`ttx_ScheduleTypes`**.
  The app model also lists `ttx_Schedule` as a valid child, but live binding
  runs through `ScheduleItemID`, not tree parenting.

## Gotchas
- An automated transfer is a **publishing pipeline** — the wave-1 packaging
  trap applies doubly: a dev instance can BE the update server, and a scheduled
  transfer repeats the mistake every interval. Verify `cl config` →
  `UpdateServer` and the destination URL before activating.
- Live columns (INFORMATION_SCHEMA): `ID, Title, Description,
  ParentID, Created, LastUpdate, Destination_ServiceURL, Destination_Username,
  Destination_Password, ExportDefinitionCollectionID, Source_ServiceURL,
  Source_Username, Source_Password, Validate_Certificate, LastExecution,
  Source_ConnectionID, Source_PackageID, Destination_ConnectionID,
  Source_PackageType, Timeout`.

## See also
- `cl howto ttx_Schedule` — the time-config child
- `cl howto ttx_ExportDefinitionCollection` / `ttx_ExportDefinition` — what travels
- `cl howto ttx_Schedule_SQL` / `ttx_Schedule_TrustedCode` — siblings
- `cl package` — the manual transport verbs
