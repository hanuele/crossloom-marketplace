# ttx_Connection — Cheat Sheet

> Quick-reference for Connections — named external data sources (databases,
> FTP, mail, LDAP, web/HTTP, SAP, ...) used by Lookups, TrustedSQL, exports,
> and connectors.

## Checklist (before you call it done)
- [ ] Created **under the right `ttx_ConnectionType`** — the parent IS the
      type; there is no ConnectionTypeID column.
- [ ] Config lives in **`Content`** (collected as a JSON array from the
      type-specific UISnippet's `cl-connection-config` fields).
- [ ] Credentials stored via **`CredentialID`** → `ttx_Credential`
      (UserIdentity + UserKey + SecuredContent, encrypted) — never inline in
      `Content`.
- [ ] Description set.

## Required relations
- **Parent `ttx_ConnectionType`** — verified live from the app model: the
  connection's type is encoded purely by parenting.
- **`CredentialID`** → `ttx_Credential` for auth material.
- Consumers reference the connection by `ConnectionID` columns
  (ttx_LookUps, ttx_TrustedSQL, ttx_ExportDefinition, ...).

## Parenting rules
- Valid parent (live app model): **`ttx_ConnectionType`**
  only.

## Gotchas
- **There is no `ConnectionTypeID` column** — live columns are exactly `ID,
  Title, Description, ParentID, Created, LastUpdate, Content, CredentialID`
  (INFORMATION_SCHEMA). Queries filtering connections by
  type must JOIN on `ParentID`.
- **Each connector type has its own config UISnippet** (16 exist — MSSQL,
  MySQL, Oracle, PostgreSQL, iDB2, SAP, MongoDB, CouchDB, FTP, SFTP/SCP, IMAP,
  SMTP, LDAP, PowerShell, Web, HTTP). The Admin UI loads the snippet by
  connector type; fields bind via `cl-connection-config="FieldName"`.
- Schema work against an *external* DB goes through the ISQL gateway
  (`CrossLoom.GetConnectionProvider(ConnectionID)` → `AddColumn` etc.) — not
  `AlterTable*`, which targets CrossLoom's own tables. Confusing the two
  fails silently or throws.

## See also
- `cl connections` — list connection pools by type
- `cl howto ttx_UISnippet` — the config-panel mechanism
- `docs/LESSONS-LEARNED.md` (crossloom repo) — the two schema-management APIs
