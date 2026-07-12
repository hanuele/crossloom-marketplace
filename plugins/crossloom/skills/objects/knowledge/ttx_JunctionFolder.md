# ttx_JunctionFolder — Cheat Sheet

> Quick-reference for Junction folders — the organizing containers for
> `ttx_ServiceMapping` rows (Junction URL mappings). The folder name is also
> the URL path segment: a mapping with Alias `claude/ping` lives in the
> `claude` folder by convention.

## Checklist (before you call it done)
- [ ] Created under `ttx_Menu_CrossLoom` or nested inside another
      JunctionFolder.
- [ ] Title + Description set — the folder is the Admin UI's grouping surface
      for Junction endpoints.

## Required relations
- None beyond parenting — the folder is a pure container (live columns are only
  the universal six: `ID, Title, Description, ParentID, Created, LastUpdate` —
  INFORMATION_SCHEMA).

## Parenting rules
- Valid parents (live app model): **`ttx_Menu_CrossLoom`** or
  **`ttx_JunctionFolder`** — folders nest.
- This folder type is the **only valid parent of `ttx_ServiceMapping`** — a
  mapping created elsewhere (zero-GUID, app root) is orphaned and invisible in
  the Admin UI. This exact trap cost the 2026-06-09 Aesco session a correction
  round.

## Gotchas
- An orphaned mapping still *serves* its URL — invisibility in the Admin UI
  does not mean the endpoint is down, which makes the orphan harder to notice.
  `cl junctions` lists mappings regardless of parenting; compare against the
  Admin tree when something is "missing".

## See also
- `cl howto ttx_ServiceMapping` — what lives inside
- `cl howto ttx_UISnippetFolder` — the same container pattern for UISnippets
- `cl://playbook/05-junctions` — the two-object Junction model
