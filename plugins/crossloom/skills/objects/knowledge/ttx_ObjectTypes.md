# ttx_ObjectTypes — Cheat Sheet

> Quick-reference for ObjectType definitions (CrossLoom's "class definitions":
> a named entity, typed fields, backed by a SQL table, exposed via /data and
> /view). Depth lives in `cl://playbook/07-object-types`.

## Checklist (before you call it done)
- [ ] Table name follows `z{Domain}_{ObjectName}` — `ttx_*` is reserved for
      CrossLoom system tables, never create one.
- [ ] The auto-generated **Title field has a Description** explaining what Title
      means for THIS type (instance name? invoice number? IP?). Future devs
      can't guess.
- [ ] `WildcardPublish` chosen deliberately: `True` (default) publishes all
      fields; `False` for existing/shared tables where only safe fields may be
      exposed (the `ttx_user.Password` rule).
- [ ] Phase 2 done: the type is **linked to its application** (Objecttypes tab →
      writes the dependency) — without it the type is invisible to the app API
      and skipped by app-scoped Package exports.
- [ ] Description is set on the type itself.

## Required relations
- **App dependency link** (Phase 2 above) — mandatory, the #1 dev mistake.
- **`ttx_ObjectTypeFields` rows** — per-field publish/role config (see
  `cl howto ttx_ObjectTypeFields`).
- App-model containment rows in `ttx_AppsObjectsChildren` define where
  instances may live in each app's tree.

## Parenting rules
- Valid parent (live app model): **`ttx_Menu_CrossLoom`**.
  Inspect any type's own containment with `cl appmodel <type>`.

## Gotchas
- **Standard Fields run ALTER TABLE on the live schema** — adding "Queue"
  Standard Fields adds real database columns, irreversible without manual SQL.
  Never flip Standard Fields on a production type without a migration plan.
- **A typed object saved with zero-GUID ParentID silently no-ops** at the
  platform layer (HTTP 200, no row). The `cl` client raises `SilentSaveError`
  pre-flight; raw HTTP and Admin-UI callers stay exposed.
- Live columns: `ID, Title, Description, TableName, FieldList,
  CustomRolesTable, Created, LastUpdate, MainObjectTypeID, ParentID,
  StdContents, StdContent` (INFORMATION_SCHEMA).

## See also
- `cl types` — list all ObjectTypes; `cl appmodel <type>` — containment rules
- `cl howto ttx_ObjectTypeFields` — the per-field config sibling
- `cl://playbook/07-object-types` — two-phase creation recipe
