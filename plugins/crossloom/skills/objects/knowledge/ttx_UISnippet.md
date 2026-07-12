# ttx_UISnippet — Cheat Sheet

> Quick-reference for UISnippets — reusable HTML/JS fragments injected into
> CrossLoom Admin and app UIs (connector config panels, SmartUI controls,
> custom widgets).

## Checklist (before you call it done)
- [ ] Created **under a `ttx_UISnippetFolder`** — the only valid parent.
- [ ] The markup/JS lives in the **`Content`** property.
- [ ] `IsPublic` decided deliberately.
- [ ] If it's a SmartUI control: Description contains the **`SUIE:`** tag (see
      Gotchas — that tag IS the registration).
- [ ] Description set regardless — it's also the SmartUI discovery surface.

## Required relations
- **Connector snippets**: CrossLoom Admin loads the matching UISnippet by
  connector type (16 exist: MSSQL, MySQL, Oracle, PostgreSQL, iDB2, SAP,
  MongoDB, CouchDB, FTP, SFTP/SCP, IMAP, SMTP, LDAP, PowerShell, Web, HTTP).
  Config fields bind via `cl-connection-config="FieldName"` HTML attributes;
  credentials use `id="UserIdentity"` / `id="UserKey"` and are stored
  separately via the Connection's `CredentialID`.

## Parenting rules
- Valid parent (live app model): **`ttx_UISnippetFolder`**
  only.

## Gotchas
- **SmartUI discovers controls dynamically — there is no ControlType enum.**
  Any snippet whose Description contains `SUIE:your-control-name` appears in
  the SmartUI editor (loaded via the "SmartUI Get available Snippets" lookup
  each time). The Description tag is the registration mechanism.
- **Bind to the `ConfigInitialized` DOM event, not `$(document).ready`** —
  CrossLoom Admin fires it after injecting the snippet and populating existing
  config values; ready-handlers run too early to see them.
- Live columns: `ID, Title, Description, ParentID, Created, LastUpdate,
  Content, IsPublic, CarouselObjectTypeID, AppID, TargetID`
  (INFORMATION_SCHEMA).

## See also
- `cl howto ttx_UISnippetFolder` — the container
- `cl howto ttx_Connection` — where connector snippets plug in
- `docs/LESSONS-LEARNED.md` (crossloom repo) — connector UISnippet + SUIE patterns
