# ttx_Translation — Cheat Sheet

> Quick-reference for translation key/value rows (UI localization per app and
> language). ExampleApp alone carries 14,060 of these — translations are bulk data,
> not tree objects.

## Checklist (before you call it done)
- [ ] `ElementKey` + `ElementValue` + `LanguageCode` set; `ApplicationID`
      scopes the key to its app.
- [ ] After changing translations: **clear the browser localStorage cache** or
      the change stays invisible (see Gotchas).
- [ ] `cl translations gaps` run — missing keys surface there, not in the UI.

## Required relations
- **`ApplicationID`** — the owning app; keys are app-scoped, not global.

## Parenting rules
- **Not part of the app-model tree.** The table has **no ParentID column**
  (INFORMATION_SCHEMA: `ID, ElementKey, ElementValue,
  LanguageCode, ApplicationID, Created, LastUpdate, Column1`) and no
  `ttx_AppsObjectsChildren` rows — rows are keyed by
  `ApplicationID + LanguageCode + ElementKey` and managed through the
  translation editor / `cl translations`.

## Gotchas
- **Saved translation changes don't appear until the browser cache is
  cleared** — translations are cached in localStorage under `cl-tr-*` keys.
  Clear with
  `Object.keys(localStorage).filter(k => k.startsWith('cl-tr-')).forEach(k => localStorage.removeItem(k))`
  or a full page reload. The save worked; the browser is lying.
- The stray `Column1` column exists on the live table — undocumented; don't
  build on it.

## See also
- `cl translations` / `cl translations gaps` — the CLI surface
- `cl howto ttx_Apps` — the owning scope
