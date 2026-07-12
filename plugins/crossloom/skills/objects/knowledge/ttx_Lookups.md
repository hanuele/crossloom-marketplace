# ttx_Lookups — Cheat Sheet

> Quick-reference for CrossLoom Lookups (stored T-SQL queries, the workhorse of
> `cl query`). This sheet is the *index*, not the manual — depth lives in
> `cl://playbook/08-lookups-and-queries`.

## Checklist (before you call it done)
- [ ] The SQL lives in the **`ViewDef`** property.
- [ ] Connection chosen deliberately (`ConnectionID` empty/Local = the instance's
      own DB; a named `ttx_Connection` = external database).
- [ ] `cmdTimeout` sane for the query (default ceiling is 600 seconds).
- [ ] Read queries use `WITH (NOLOCK)` to avoid blocking live sessions.
- [ ] If an application calls it: a `ttx_Dependency_Lookup` entry links it to that app.
- [ ] Description is set.

## Required relations
- **`ttx_Dependency_Lookup`** — required for app-scoped access; without it the
  permission handler returns empty results.
- **`ConnectionID`** — optional link to a `ttx_Connection` for external DBs; the
  dropdown in the Admin UI writes this column.

## Parenting rules
- Valid parent (live appmodel): **`ttx_Menu_CrossLoom`**; no
  valid child types. Inspect with `cl appmodel ttx_Lookups`.

## Gotchas
- **Type name vs table name differ**: the ObjectType is `ttx_Lookups`, the SQL
  table is **`ttx_LookUps`** (capital U — verified live, INFORMATION_SCHEMA).
  Raw SQL against `ttx_Lookups` fails; `cl` verbs take the
  type name. Same anomaly family as `ttx_OrganisationUnit`.
- **The execute endpoint is**
  `POST /data/app/{appID}/object/{ObjectID}/lookup/{lookupID}` — `ObjectID` is
  the object *from which* the lookup is executed; it equals `lookupID` when
  the lookup executes itself (Peter, platform creator, 2026-06-10 — settles a
  prior conflict between playbook ch. 08 and project memory). Response carries
  `Columns` + `Rows` + `DataType` arrays. Prefer `cl query` / the Python
  client over hand-building the POST.
- **History is automatic** — every save versions the SQL (see `cl diff <uuid>`);
  no need to restore the original after a scratch query.
- **Scratchpad discipline**: shared test lookups exist (`Claudes Test Lookup`
  `fff0c798-2e39-4bf8-bf82-366016a65475`) — `cl query` uses one under the hood.
  Don't repurpose production lookups as scratchpads.
- Full live column set: `ID, Title, Description, ViewDef, UpdateDef, InsertDef,
  Created, LastUpdate, ParentID, ReplicationDef, RequiredRole, cmdTimeout,
  ConnectionID, PermissionID, ServiceName, AppID, TargetID`.

## See also
- `cl query "SELECT ..."` — ad-hoc SQL via the test lookup (auto `SET DATEFORMAT ymd`)
- `cl diff <uuid>` — version history; `cl schema tables [filter]`
- `cl://playbook/08-lookups-and-queries` — execute API, full workflow
- `cl://reference/known-pitfalls` — date-literal locale trap for raw callers
