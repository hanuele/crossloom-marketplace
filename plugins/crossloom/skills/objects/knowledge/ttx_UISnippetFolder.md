# ttx_UISnippetFolder — Cheat Sheet

> Quick-reference for UISnippet folders — the organizing containers for
> `ttx_UISnippet` objects.

## Checklist (before you call it done)
- [ ] Created under `ttx_Menu_CrossLoom` or nested inside another
      UISnippetFolder.
- [ ] Title + Description set (folders are navigation surface — an unnamed
      folder hides its snippets).

## Required relations
- None beyond parenting — the folder is a pure container (live columns are only
  the universal six: `ID, Title, Description, ParentID, Created, LastUpdate` —
  INFORMATION_SCHEMA).

## Parenting rules
- Valid parents (live app model): **`ttx_Menu_CrossLoom`** or
  **`ttx_UISnippetFolder`** — folders nest.
- This folder type is the **only valid parent of `ttx_UISnippet`** — a snippet
  created elsewhere is orphaned and invisible in the Admin UI (same trap class
  as ServiceMapping/JunctionFolder).

## Gotchas
- Folder structure is also the discovery surface for developers browsing the Admin
  UI — keep connector snippets, SmartUI controls, and app-specific snippets in
  separate folders rather than one flat pile.

## See also
- `cl howto ttx_UISnippet` — what lives inside
- `cl howto ttx_JunctionFolder` — the same container pattern for Junctions
