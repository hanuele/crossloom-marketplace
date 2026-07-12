# ttx_UI — Cheat Sheet

> Quick-reference for ttx_UI objects — **every page in a CrossLoom application
> IS a ttx_UI object**, including every page of the Admin app itself (the
> platform self-hosts its own UI). A ttx_UI holds a complete HTML document
> (`<!DOCTYPE html>` …) rendered by the /view handler for a given scope.
> Source: Peter (platform creator) + Admin-UI walkthrough, 2026-06-10.

## Checklist (before you call it done)
- [ ] Created under `ttx_Menu_CrossLoom` or `ttx_Menu_Form` (the two valid
      parents).
- [ ] Scope bound correctly: `AppID` (owning app) + `ObjTypeID` (the
      ObjectType whose pages this UI renders) + `ObjID` where the UI is for
      one specific object instance (e.g. the Admin "CL Menu ObjectTypes" page
      binds ObjID = the menu object it renders).
- [ ] `DefaultContent` holds the full HTML document; `MobileContent` only if
      the mobile rendering differs — they are separate documents, edited via
      the Default / Mobile tabs in the page editor.

## Required relations
- **`AppID`** — the owning application; **`ObjTypeID`** / **`ObjID`** — the
  type or instance scope the /view handler matches when serving the page.

## Parenting rules
- Valid parents (live app model): **`ttx_Menu_CrossLoom`**
  or **`ttx_Menu_Form`**.

## Gotchas
- **To find the ttx_UI behind any page you are looking at**: Dev Mode →
  context menu → **Edit Page** opens that page's ttx_UI object directly in
  the editor (Admin app, settings menu). Faster and surer than searching by
  title.
- **Default and Mobile are separate full documents** — editing only
  `DefaultContent` leaves a stale mobile variant in place; check both tabs
  when changing shared markup.
- The editor shows Title / Description / Objecttype / Object ID above the
  HTML — the green Object ID field is the `ObjID` binding; an unexpected
  binding here is why "my edit shows on the wrong page".
- Live columns: `ID, Title, Description, ParentID, Created, LastUpdate,
  AppID, ObjTypeID, ObjID, DefaultContent, MobileContent`
  (INFORMATION_SCHEMA; 110 rows live).

## See also
- `cl howto ttx_UISnippet` — reusable fragments injected INTO pages
  (different concept: a ttx_UI is the page itself)
- `cl read <uuid> -p DefaultContent` — read a page's HTML from the CLI
- `cl://playbook/runtime-architecture` — the /view handler rendering path
