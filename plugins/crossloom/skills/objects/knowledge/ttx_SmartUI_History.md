# ttx_SmartUI_History — Cheat Sheet

> The change-log for **SmartUI controls**. Each row is a **full snapshot of one
> control's definition** at a point in time — not a sparse delta and not a
> value-free audit marker. SmartUI control edits write **ONLY here**, never to
> `ttx_Messages` (verified in internal testing: 114 history rows → 0 message rows),
> so any `ttx_Messages`-only tool (`changes_audit`, `who_changed_this`,
> `revert_changes`) is structurally blind to SmartUI edits unless it UNIONs this
> table.

## Why this table matters (the audit-completeness asymmetry)
- **Listing** a change rides on the always-recorded part (*what/who/when*).
- **Reverting** a change needs the **before-image** (the prior value).
- The generic `ttx_Messages` trail carries *no* values on creates and is
  write-path-dependent (script-path writes don't auto-audit), so the generic
  `update_revert` verb found **restorable≈0** in internal testing.
- `ttx_SmartUI_History` is the richer alternative for the SmartUI object family:
  it stores the **whole control definition** per row, and SmartUI edits go
  through the UI (command-handler path) → **auto-audited**. This is the bet
  behind the planned SmartUI-scoped update-revert before-image variant.

## Live schema
OT id `f742ee9a-a036-402e-be6a-9df02edf6e8a`. 22 columns:

| Column | Type | Role |
|---|---|---|
| `ID` | uniqueidentifier | the history row's own id (NOT the control id) |
| `SourceID` | uniqueidentifier | **the live SmartUI control** this row snapshots (→ `ttx_SmartUI.ID`) |
| `ChangeType` | nvarchar | `snapshot` \| `create` \| `change` \| `delete` (see below) |
| `UserName` | nvarchar | who — bare SamAccountName (e.g. `devuser`), same format as `ttx_Messages.CreatedBy` |
| `AppID` | uniqueidentifier | the control's own app (NOT the Admin app, unlike `ttx_Messages`) |
| `Created`, `LastUpdate` | datetime | row timestamps; `LastUpdate` is the change instant used by the changes flow |
| `PropertyName`, `PropertyLabel` | nvarchar | the bound property's name + display label (label survives `delete` rows) |
| `ControlType`, `ControlOrderIndex`, `ControlHostSelector` | nvarchar/int | control structure |
| `ControlMaxLength`, `ControlMinValue`, `ControlMaxValue` | int | control constraints |
| `OptionSelection`, `LookupID`, `OptionClass`, `OptionStyle` | nvarchar/uuid | option-source + styling |
| `Description`, `Condition` | nvarchar | control description + visibility condition |
| `ParentID` | uniqueidentifier | (history-row parent; relation to control tree not yet walked) |

The control-defining columns (`ControlType` … `Condition`) mirror `ttx_SmartUI`,
which is what makes a row a reconstructable before-image of the whole control.

## ChangeType values (sparse instance)
- **`snapshot`** — a one-time **baseline** capture (85 controls, all at the
  identical instant 2026-03-08 20:46 — an install/migration seeding). Gives a
  floor before-image even for controls never edited since.
- **`create`** — control created (one row per control; 18).
- **`change`** — control edited (7 rows across only **3 controls** → a real
  snapshot *chain* exists, but the demo instance has almost no SmartUI editing activity).
- **`delete`** — control deleted; the row still carries the full prior snapshot
  (4).

## Before/after semantics — AFTER-value (CONFIRMED via the canonical source)
- The history row is an **after-image**: written *from the post-update live row*.
  Confirmed authoritatively by the canonical TrustedSQL **"SmartUI Editor Save
  Control"** (`165976a2-ef1f-4726-8759-4761302b9fb8`, app `18027c26`): it first
  `UPDATE ttx_SmartUI SET <the 14 control columns> WHERE ID=@ID`, then
  `INSERT INTO ttx_SmartUI_History (...) SELECT ..., getdate(), ..., ID,
  @CurrentUserName, @changetype FROM ttx_SmartUI WHERE ID=@ID` — i.e. it snapshots
  the row it *just wrote*. So the newest history row always == the live control.
  (Corroborated independently by a value-free CHECKSUM probe, n=2, 2026-06-29.)
- **Before-image rule:** to revert a control's changes since window-start `T`,
  restore it to the **newest history row with `LastUpdate < T`** (the last
  committed state before the window); if none, fall back to the `create`/baseline
  `snapshot` row.
- **The audited apply path:** mirror "SmartUI Editor Save Control" faithfully —
  `UPDATE ttx_SmartUI` to the before-image values, then the same history-INSERT —
  so a revert is itself a `ChangeType='change'` snapshot (self-auditing). A raw
  `UPDATE` alone would bypass that audit (there is NO db trigger on `ttx_SmartUI`,
  verified 2026-06-29 — the history is written app-side by this canonical).

## Gotchas
- **SmartUI edits are invisible to `ttx_Messages` tooling** — UNION this table in
  or you silently drop them (the fix shipped in `core/changes.py`).
- **`ttx_SmartUI.LastUpdate` came back NULL** on the live rows probed (2026-06-29)
  — don't rely on the *live* control's `LastUpdate`; use the history row's.
- **Not every `SourceID` resolves to a live control** (deleted controls; 1 of 3
  changed controls had no live `ttx_SmartUI` row) — a revert join must
  tolerate the missing-live case.
- **demo-instance data is sparse** — restorable yield demos here will look ≈0. That is a
  property of the demo instance's data shape, not of the mechanism; a production instance with
  real SmartUI editing is where yield shows.
- Probe this table **value-free** — names/counts/`ChangeType`/classification only,
  never `Value`/`Description`/`Condition` content (data-privacy rule).

## See also
- `core/changes.py` (the "get changes" flow) — the SmartUI special-pack UNION
- `ttx_Translation.md` — the *other* table the changes/changeset flows special-pack
- `core/update_revert.py` — the generic verb whose restorable≈0 ceiling motivates the SmartUI-scoped variant
- `ttx_Messages` MsgType map (1/5/6/11/13) — the generic audit trail this routes around
