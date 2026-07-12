# ttx_ExportDefinitionCollection — Cheat Sheet

> Quick-reference for the **Package authoring surface**. A "CrossLoom Package"
> (`.3tp` file) is exported from an ExportDefinitionCollection whose children
> define which tables/objects travel. Depth lives in
> `cl://playbook/06-packages`.

## Checklist (before you call it done)
- [ ] Collection created with a meaningful Title + Description (it names the
      Package in every target instance's Package Manager).
- [ ] One **`ttx_ExportDefinition`** child per table scope (its `Cmd`,
      `TableName`, `PrimaryKey`, `CmdType` define what is exported and how it
      applies).
- [ ] `FullSync` vs merge decided per definition — `FullSync` replaces, merge
      upserts; `FullSyncRestriction` bounds a full sync.
- [ ] When testing on a dev instance: **`Published = False`** until verified.

## Required relations
- **`ttx_ExportDefinition` children** — the collection is a pure container (live
  columns: only the 6 universal ones); all export semantics live on the
  children: `Cmd, TableName, PrimaryKey, ModifyExistingFields, CmdType,
  FullSync, FullSyncRestriction, TimestampField, ConnectionID`
  (INFORMATION_SCHEMA).

## Parenting rules
- Valid parent (live appmodel): **`ttx_Menu_CrossLoom`**.
  Valid child: **`ttx_ExportDefinition`** via ParentID. Inspect with
  `cl appmodel ttx_ExportDefinitionCollection`.

## Gotchas
- **"Package" is the colloquial name, not the type name.** There is no
  `ttx_Package` ObjectType on the instance (verified against all 329 live types)
  — the authoring objects are ExportDefinitionCollection +
  ExportDefinition; the `.3tp` file is the transport.
- **The `.3tp` envelope is `base64(gzip(JSON))`** — base64 prefix `H4sI` is the
  gzip magic's literal. Three top-level keys: `Details`, `Definition`, `Content`.
- **The two import verbs read different keys** — `cl package import-definition`
  (PUT) applies only `Definition` (object templates); `cl package import` (POST)
  applies only `Content` (table rows). PUT against a Content-only package
  **silently no-ops — that is correct semantics, not a bug**. When
  import-definition "succeeds" but nothing changed, suspect envelope-key scope
  before the implementation (a lesson that cost two sessions of internal debugging).
- **The dev instance can BE the update server** — publishing a test package can
  reach other instances. Check `cl config` → `UpdateServer` before publishing;
  keep `Published = False` while testing.

## See also
- `cl package export/import/import-definition` — the transport verbs
- `cl://playbook/06-packages` — envelope decode recipe, verification commands
- `cl://playbook/runtime-architecture` — stage promotion via Packages
