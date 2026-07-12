# ttx_ObjectTypeFields — Cheat Sheet

> Quick-reference for per-field configuration rows (publish + permission gates
> per ObjectType field). Depth lives in `cl://playbook/07-object-types`
> §Field Properties.

## Checklist (before you call it done)
- [ ] Every field has a Description — especially Title (its meaning differs per
      type).
- [ ] `Publish` set deliberately per field: `True` exposes via /data and /view;
      `False` is the security boundary (the field never leaves the backend).
- [ ] `RequiredRole` set where a field needs a per-field permission gate
      (None = everyone with app access).

## Required relations
- **`ObjectTypeID`** — every row belongs to exactly one ObjectType; this is the
  key, not a ParentID.

## Parenting rules
- **Not part of the app-model tree.** The table has **no ParentID column**
  (INFORMATION_SCHEMA: `ID, Created, LastUpdate,
  ObjectTypeID, FieldName, RequiredRole, Description, Publish`) and no
  `ttx_AppsObjectsChildren` rows — rows are keyed by `ObjectTypeID` and managed
  through the ObjectType editor, not the object tree.

## Gotchas
- **`FieldName = '*'` is intentional, not a bug** — the wildcard means all
  fields of that type are accessible to the given role. Common on simple types.
- `WildcardPublish=True` on the ObjectType overrides per-field `Publish` — if a
  field must stay private, the type needs `WildcardPublish=False` AND the safe
  fields explicitly published.

## See also
- `cl howto ttx_ObjectTypes` — the parent concept (two-phase creation,
  WildcardPublish semantics)
- `cl://playbook/07-object-types` §Field Properties, §WildcardPublish
- `docs/LESSONS-LEARNED.md` (crossloom repo) — the `'*'` wildcard anti-pattern note
