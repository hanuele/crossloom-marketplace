# ttx_Apps — Cheat Sheet

> Quick-reference for CrossLoom Applications (self-contained workspaces:
> ObjectTypes + hierarchy + permissions + a generated SQL view). Depth lives in
> `cl://playbook/09-applications`.

## Checklist (before you call it done)
- [ ] **Title contains no hyphens** — the auto-generated alias feeds the SQL view
      name `View_TTX_App_{Alias}`, and a hyphen breaks view generation silently
      (known platform bug, not validated in the UI).
- [ ] Every ObjectType the app uses is linked via the Objecttypes tab (writes a
      `ttx_Dependency_*` entry).
- [ ] App model (hierarchy) built and saved — containment rules land in
      `ttx_AppsObjectsChildren`.
- [ ] **Generate Application View** run — and re-run after every model change.
- [ ] Owners assigned (App Owner button → `ttx_AppsOwners`).
- [ ] Description is set.

## Required relations
- **`ttx_Dependency_*` entries** — objects not linked to the app return empty
  from the app API (the permission handler blocks them) and are skipped by
  app-scoped Package exports. The #1 dev mistake.
- **`ttx_AppsObjectsChildren`** — stores the app model tree (Join-on/Title/
  Description field mappings per containment rule).
- **`ttx_AppsOwners` / `ttx_AppsOwnerGroups` / `ttx_AppsUserRoles` /
  `ttx_AppsGroupRoles`** — the 4-table permission model.

## Parenting rules
- Valid parent (live appmodel): **`ttx_Menu_CrossLoom`**.
  Valid children: the app's 12 internal menu types (`ttx_Menu_Lookup`,
  `ttx_Menu_TrustedSQL`, `ttx_Menu_UISnippet`, `ttx_Menu_ObjectType`,
  `ttx_Menu_AppModel`, `ttx_Menu_Workflow`, `ttx_Menu_Form`,
  `ttx_Menu_Translation`, `ttx_Menu_Permissions`, `ttx_Menu_ApplicationOwners`,
  `ttx_Menu_OfflineCache`, `ttx_Menu_Script`) — all via ParentID. Inspect with
  `cl appmodel ttx_Apps`.

## Gotchas
- **`View_TTX_App_{Alias}` views don't expose an AppID column** — they are
  already app-filtered; don't write `WHERE AppID = ...` against them.
- **DateTime saves through the default UI need ISO `YYYY-MM-DD`** (hyphens).
  Dot-separated German format fails with a *misleading "not authorized"* error —
  it's a format problem, not a permission problem.
- **Custom tables follow `z{Domain}_{Name}`** (e.g. `zClaude_ToDo`); never
  create `ttx_*` tables — that prefix is reserved for system types.
- Re-generate the app view after ANY model change; a stale view is the usual
  cause of "object saved but not visible in the tree".

## See also
- `cl apps` / `cl app` — list applications, manage the active app context
- `cl appmodel <type>` — valid parents/children per type
- `cl://playbook/09-applications` — full 7-step creation recipe
- `cl://reference/known-pitfalls` §Applications
