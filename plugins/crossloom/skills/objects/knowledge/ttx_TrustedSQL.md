# ttx_TrustedSQL — Cheat Sheet

> Quick-reference for working with CrossLoom TrustedSQL objects (server-side
> T-SQL modules). This sheet is the *index*, not the manual — depth lives in
> `cl://playbook/08-lookups-and-queries` and
> `cl://playbook/runtime-architecture`.

## Checklist (before you call it done)
- [ ] Description is set (an empty Description makes the module hard to find later).
- [ ] The T-SQL lives in the **`CMD`** property — not `SqlCode`, not `ScriptCode`.
- [ ] `ConnectionID` points at the right database (empty/Local = the instance's own DB).
- [ ] `ReturnsResult` matches what callers expect (result set vs fire-and-forget).
- [ ] If an application calls it: a `ttx_Dependency_TrustedSQL` entry links it to that app.

## Required relations
- **`ttx_Dependency_TrustedSQL`** — an app can only reach the module when this
  dependency entry exists; without it the permission handler blocks the response
  (the same "#1 dev mistake" as for every `ttx_Dependency_*` family member).
- **`ConnectionID`** — optional link to a `ttx_Connection` for external databases.

## Parenting rules
- Valid parent (live appmodel): **`ttx_Menu_CrossLoom`** — a
  TrustedSQL lives under the Admin app's CrossLoom menu folder; it has no valid
  child types. Inspect anytime with `cl appmodel ttx_TrustedSQL`.

## Gotchas
- **`cl read <uuid>` fails on a TrustedSQL** — the no-property default is
  `ScriptCode`, which TrustedSQL does not have. Use `cl read <uuid> -p CMD`.
  Full live column set: `ID, Title, Description, ReturnsResult, CMD, Created,
  LastUpdate, ParentID, RequiredRole, cmdTimeout, ConnectionID, PermissionID,
  ServiceName, LogLevel, AppID, TargetID` (INFORMATION_SCHEMA).
- **`cmdTimeout` is real** — long-running statements get cut; check it before
  blaming the SQL.
- **Date literals**: `cl query` prepends `SET DATEFORMAT ymd;` for you, but a
  TrustedSQL body runs under the connection's own locale (German `dmy`)
  — use ISO-8601 with `T`-separator (`'2026-06-10T10:00:00'`) inside `CMD`.

## See also
- `cl read <uuid> -p CMD` — read the SQL body
- `cl diff <uuid>` — version history from ttx_messages
- `cl://reference/known-pitfalls` §"`cl` CLI / client.py gotchas"
- `cl://playbook/runtime-architecture` — module execution, scheduler binding
