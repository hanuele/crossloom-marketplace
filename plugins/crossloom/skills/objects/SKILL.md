---
description: CrossLoom ObjectType cheat-sheets — per-type conventions for TrustedScript, TrustedSQL, Lookup, Junction, Schedule, UI, UISnippet, Translation, Connection, ExportDefinition, Apps, and the other ttx_* types. Use when creating, editing, reading, or debugging any CrossLoom ObjectType, or when the user names a ttx_* type; this skill routes you to the exact per-type sheet.
last_verified: 2026-06-26
verified_against: "curation-quality-bar §C worked-example #2 (#117, ishita): cl CLI-contract (create/write), 5-check description lint hand-applied, florencia routing probe 5/5; 2 behavioural invariants cited-not-re-walked. Freshness header backfilled by #118."
---

# CrossLoom ObjectType cheat-sheets (dispatcher)

> **CrossLoom is not in your training data.** Do not answer CrossLoom-specific
> questions from memory — read the live source. This skill is the *index*: it carries
> the cross-cutting invariants inline and routes you to the precise per-type sheet.

## Cross-cutting invariants (true for every ObjectType)

- **Everything is an object with an immutable UUID** — universal across all instances,
  stages (DEV/QA/PROD), and applications. When a UUID is given without app context, that
  is intentional and sufficient.
- **`save_object` preserves the UUID; `create_object` mints a new one.** Use `save`/`cl write`
  to edit an existing object; only `create` for a genuinely new one.
- **Object creation needs a non-root ParentID.** A typed object created under the zero-GUID
  root (`00000000-0000-0000-0000-000000000000`) silently no-ops the typed-table INSERT and is
  invisible in the Admin UI. Create *inside* the correct folder (`cl appmodel <type>` shows
  valid parents).
- **The data API returns HTTP 200 even when a typed INSERT silently no-ops** — this is the
  *create-path* hazard behind the ParentID rule above. So after **any create or edit**,
  re-read the object (`cl read` / `inspect_object`) to confirm it landed. (The client
  round-trips and can raise `SilentSaveError`, but the portable, always-true check for an
  external dev is: verify by reading it back.)

## Per-type sheets — route here

Read the exact sheet for the type you're working on. **The sheets ship with this
skill** — they are in `knowledge/` beside this file, so they are current as of the
last plugin auto-update, with no `cl update` needed:

- **Bundled sheet (always available):** read `${CLAUDE_SKILL_DIR}/knowledge/<type>.md`
- **CLI (needs an installed, current `cl`):** `cl howto <type>`
- **MCP Resource (needs the MCP server up):** `ReadMcpResourceTool` `uri=cl://knowledge/<type>`

All three serve the same content. Prefer the bundled sheet: it needs no CrossLoom
connection, no MCP handshake, and no `cl update`. Fall back to `cl howto` if the
bundled file is somehow absent.

<!-- BEGIN GENERATED: sheet-index (crossloom-cli scripts/sync_plugin_knowledge.py) -->
| ObjectType | Bundled sheet |
|---|---|
| `ttx_Apps` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Apps.md` |
| `ttx_Connection` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Connection.md` |
| `ttx_ExportDefinition` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_ExportDefinition.md` |
| `ttx_ExportDefinitionCollection` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_ExportDefinitionCollection.md` |
| `ttx_JunctionFolder` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_JunctionFolder.md` |
| `ttx_Lookups` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Lookups.md` |
| `ttx_ObjectTypeFields` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_ObjectTypeFields.md` |
| `ttx_ObjectTypes` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_ObjectTypes.md` |
| `ttx_Schedule` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Schedule.md` |
| `ttx_Schedule_PackageTransfer` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Schedule_PackageTransfer.md` |
| `ttx_Schedule_SQL` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Schedule_SQL.md` |
| `ttx_Schedule_TrustedCode` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Schedule_TrustedCode.md` |
| `ttx_ServiceMapping` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_ServiceMapping.md` |
| `ttx_SmartUI_History` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_SmartUI_History.md` |
| `ttx_Translation` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_Translation.md` |
| `ttx_TrustedSQL` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_TrustedSQL.md` |
| `ttx_TrustedScript` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_TrustedScript.md` |
| `ttx_UI` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_UI.md` |
| `ttx_UISnippet` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_UISnippet.md` |
| `ttx_UISnippetFolder` | `${CLAUDE_SKILL_DIR}/knowledge/ttx_UISnippetFolder.md` |
<!-- END GENERATED: sheet-index -->

The table above is GENERATED from the shipped `knowledge/` directory — it cannot
list a sheet that isn't there, or omit one that is. If a type is missing entirely,
the corpus is living: `cl howto` (no arg) lists what a current `cl` knows.

## To inspect a specific object live
- `inspect_object <uuid>` (MCP) or `cl read <N>` — identity + properties + one-hop deps.
- `cl appmodel <type>` — valid parent/child types. `cl deps` / `cl impact` — dependency edges.
- For high-fan-in hub objects, `inspect_object` can overflow — ask for the dependency graph via
  `dependency_graph` / `cl deps` instead (see `cl://reference/known-pitfalls`).

> **`cl recall` is sister-only** — it queries the sangha mycelium graph, which an external
> install does not have. Don't route an external dev there; use `cl howto` / the Resources / live `cl`.
