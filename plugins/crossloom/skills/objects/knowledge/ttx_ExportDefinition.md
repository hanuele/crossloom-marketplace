# ttx_ExportDefinition — Cheat Sheet

> Quick-reference for per-table export definitions — the children of an
> `ttx_ExportDefinitionCollection` that define WHAT a Package carries and HOW
> it applies on import. Depth lives in `cl://playbook/06-packages`.

## Checklist (before you call it done)
- [ ] Created **under its `ttx_ExportDefinitionCollection`** (the only valid
      parent).
- [ ] `TableName` + `PrimaryKey` set for the table this definition exports.
- [ ] `Cmd` / `CmdType` define the row selection — verify the scope is what you
      intend before the first export (an over-broad Cmd ships rows you didn't
      mean to publish).
- [ ] `FullSync` vs merge decided: FullSync **replaces** target data
      (`FullSyncRestriction` bounds it); merge upserts.
- [ ] `ModifyExistingFields` decided — whether the import may alter existing
      rows' fields.

## Required relations
- **Parent `ttx_ExportDefinitionCollection`** (live app model).
- **`ConnectionID`** — optional source connection for cross-DB exports.

## Parenting rules
- Valid parent (live app model):
  **`ttx_ExportDefinitionCollection`** only.

## Gotchas
- **Definition rows travel via PUT, content rows via POST** — this type is the
  "Definition" side of the `.3tp` envelope. A Package whose export produced
  only `Content` will silently no-op under `cl package import-definition`
  (correct semantics, not a bug — a lesson learned in internal testing).
- `TimestampField` drives incremental selection — wrong field means silently
  re-exporting everything or nothing.
- Live columns: `ID, Title, Description, ParentID, Created, LastUpdate, Cmd,
  TableName, PrimaryKey, ModifyExistingFields, CmdType, FullSync,
  FullSyncRestriction, TimestampField, ConnectionID` (INFORMATION_SCHEMA).

## See also
- `cl howto ttx_ExportDefinitionCollection` — the parent container + envelope
  semantics
- `cl package export/import/import-definition` — the transport verbs
- `cl://playbook/06-packages` — decode recipe, verification commands
