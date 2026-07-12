# ttx_ServiceMapping — Cheat Sheet

> Quick-reference for Junction URL mappings. `ttx_ServiceMapping` IS the
> Junction table: one row binds a URL alias to a handler module. Depth lives in
> `cl://playbook/05-junctions` and `cl://playbook/junction-rest-api`.

## Checklist (before you call it done)
- [ ] Created **under a `ttx_JunctionFolder`** — not at the application root.
- [ ] `Alias` is set (`"folder/name"` becomes `/{instance}/junction/folder/name`).
- [ ] `ModuleID` points at the handler TrustedScript.
- [ ] `ModuleTypeID` = `f08332b3-d990-43b8-8997-c7f37db415b7` (the TrustedScript type).
- [ ] `IsPublic` decided deliberately: `"False"` requires a CrossLoom session.
- [ ] Description is set.

## Required relations
- **A Junction is two objects** — the handler TrustedScript plus this mapping.
  Creating one means two `cl create` calls: handler first, then the mapping
  whose `ModuleID` references it.
- The handler script itself needs its `ttx_Dependency_Script` entries (see
  `cl howto ttx_TrustedScript`).

## Parenting rules
- Valid parent (live appmodel): **`ttx_JunctionFolder`**
  (`81287c91-e775-44fa-8f51-55939c043177`) — and only that. A mapping created
  with a zero-GUID or root parent is orphaned and **invisible in the Admin UI**
  (the exact friction from the 2026-06-09 Aesco session). Inspect with
  `cl appmodel ttx_ServiceMapping`.

## Gotchas
- **The column set is exactly**: `ID, Title, Description, ParentID, Created,
  LastUpdate, ModuleID, ModuleTypeID, IsPublic, Alias` (INFORMATION_SCHEMA).
  There is **no ContentType and no CacheMinutes** — response
  shaping is the handler's job, not the mapping's.
- **`IsPublic` is a string** (`"True"`/`"False"`), matching CrossLoom's
  property-value convention — not a SQL bit you toggle with 1/0 through the API.
- A mapping whose `ModuleID` points at a deleted/recycled script serves errors;
  check `cl junctions` + `cl dig N` before debugging the handler code.

## See also
- `cl junctions` — list all Junction endpoints; `cl junctions open N`
- `cl howto ttx_TrustedScript` — the handler's own cheat sheet
- `cl://playbook/05-junctions` — two-object model, compilable handler template
- `cl://playbook/junction-rest-api` — full REST implementation guide
