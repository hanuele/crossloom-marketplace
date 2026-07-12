# Changelog — crossloom plugin

## 0.4.0 — 2026-07-12

**Wheel floor RAISED to `0.5.3`** — this release needs `cl mcp serve` (crossloom-cli #279).
A colleague on an older wheel is told to run `cl update` by the SessionStart version check;
that check is the safety net for this bump.

- **The plugin no longer names a Python interpreter — anywhere.** This is what made the
  plugin **unusable on macOS**, and it was invisible on Windows so nobody hit it.

  `.mcp.json` said `"command": "python"`, and both SessionStart hooks ran `python <hook>.py`.
  **macOS has no `python`**: Apple removed `/usr/bin/python` in 12.3, and Homebrew does not
  put an unversioned `python` on PATH either. On a Mac, as shipped, `/mcp` showed
  `crossloom · ✗ failed` and *both* hooks failed every session.

  The obvious fix — switch to `python3` — is **wrong**: on Windows `python3` resolves to a
  0-byte Microsoft-Store stub. **There is no single interpreter name that is correct on both
  platforms**, so the fix is to stop naming one:

  - **`.mcp.json` → `cl mcp serve`.** `cl` is a console script, so pip bakes the absolute
    path of the interpreter it installed into right into the launcher. Spawning `cl` is
    self-consistent by construction: it always runs the Python that actually has the wheel
    and the `[ai]` extras. This also fixes a latent failure on *any* machine with two
    Pythons, where `python` might not be the one pip used — previously a baffling
    `ModuleNotFoundError` from a client that "worked yesterday".
  - **`hooks/hooks.json` → `"$(command -v python || command -v python3)"`,** pinned to
    `"shell": "bash"`. Hook commands do **not** support arbitrary `${VAR}` expansion (only
    the three `CLAUDE_*` path placeholders), so the shell has to make the choice. `python`
    is tried first on purpose: on Windows it is the real interpreter, and probing `python3`
    first would find the 0-byte stub.

  No env var to set, no symlink to create, no per-platform config.

**Wheel floor: unchanged (`min_cl_version` as in 0.2.4).** This release needs no new `cl`
capability — it *removes* a dependency on one.

- **The 20 ObjectType knowledge sheets now ship IN the plugin (#285).** They live at
  `skills/objects/knowledge/*.md` and the `objects` dispatcher reads them via
  `${CLAUDE_SKILL_DIR}/knowledge/<type>.md`.

  **Why this is a minor bump and not a patch:** before 0.3.0 the plugin shipped only a
  *routing table* — every row pointed at `cl howto <type>` or `cl://knowledge/<type>`, both
  served by the crossloom-cli wheel. The plugin auto-updates; the wheel does not (it moves
  only when a dev runs `cl update`). So curated knowledge rode the train that does not move,
  and a gotcha learned today could not reach a developer automatically — the plugin kept
  auto-updating, just with a signpost to text it did not carry. **A gotcha curated today now
  reaches a developer's next session with no `cl update`.**

  The sheets are a **generated mirror**, not a second authoring surface: crossloom-cli's
  `src/crossloom_cli/knowledge/` remains the only place anyone edits them. Guarded from both
  sides — crossloom-cli's CI opens the mirror PR automatically when a sheet changes and its
  test suite fails on divergence; this repo's CI re-hashes every sheet against the shipped
  `.manifest.json` and fails on any hand-edit. **Do not edit `skills/objects/knowledge/`.**

- **The `objects` dispatcher's routing table is now generated from the corpus.** The
  hand-maintained table had drifted: it listed 19 of the 20 shipped sheets, so
  `ttx_SmartUI_History` was in the wheel but unroutable from the Skill. A generated index
  cannot omit a sheet that exists.

- **This repo has CI for the first time** (`.github/workflows/ci.yml`): the knowledge-mirror
  guard, plugin-JSON validity, and a check that `plugin.json` and `marketplace.json` agree on
  the version (auto-update keys off the marketplace entry, so a stale one means the fix never
  ships).

## 0.2.4 — 2026-07-02
- **Fixed dead doc-pointers in the `connect` + `orient` Skills (#185).** Both Skills
  pointed at a relative `docs/ENV-SETUP.md`, but the plugin's install footprint is the
  `plugins/crossloom/` subtree — `docs/` lives at the marketplace repo root and does NOT
  ship in the installed plugin (empirically confirmed: the active plugin dir carries no
  `docs/`, only the separate marketplace cache does). A stuck dev following the `connect`
  recovery Skill's pointer would hit a non-existent file. Rerouted every `docs/ENV-SETUP.md`
  reference to the durable GitHub URL
  (`https://github.com/hanuele/crossloom-marketplace/blob/main/docs/ENV-SETUP.md`), which
  resolves regardless of install layout; the setup essentials remain inlined in the Skill bodies.
  Wheel floor unchanged (`min_cl_version` = `0.4.0`) — a doc-pointer fix, no new `cl`/MCP capability.

## 0.2.3 — 2026-07-02
- Added a **plugin↔wheel version handshake** (#180): the plugin now declares a
  machine-readable minimum crossloom-cli version in `compat.json`
  (`min_cl_version`), and a new SessionStart hook (`check_wheel_version.py`)
  nudges once at startup if the installed `cl` is older than that floor — closing
  the silent skew where an auto-updated plugin could route to `cl`/MCP capability
  the manually-updated wheel lacks. Three states: older wheel → one-line nudge
  (`cl update`); compliant → silent; `cl` missing → install-docs pointer (also
  surfaces the silent-dead-MCP-server case). The `cl --version` subprocess is
  mtime-cached, so steady-state session-start cost is ~220ms (a cold check after
  `cl update` is ~860ms, once). **This release's wheel floor: `0.4.0`.**

## 0.2.2 — 2026-06-26
- Added the **`crossloom:connect`** auto-firing Skill — guided first-run environment setup
  (register `cl env`, verify with `cl ping`), surfacing when a dev can't connect. Three
  auto-firing Skills now: `objects`, `orient`, `connect`. See #133.
- Distribution: a version bump published to run a **clean silent-auto-update test** on a
  fully-rebooted second machine. That run left *silent-at-startup* **inconclusive**
  (a fresh launch still rendered 0.2.0 while the update check resolved 0.2.1); cross-machine
  *propagation* itself is proven (0.2.0→0.2.1 reached the second machine, no reinstall). See #127.

## 0.2.1 — 2026-06-26
- Distribution: wired marketplace **auto-update** (L2-02). Silent updates flow via the
  per-machine managed-setting `extraKnownMarketplaces.crossloom.autoUpdate: true`; releases
  are cut by bumping the pinned `version`. See [`docs/AUTO-UPDATE.md`](../../docs/AUTO-UPDATE.md).
- No change to plugin behaviour (MCP, Skills, conventions hook) vs 0.2.0 — this release exists
  to ship the distribution wiring and to prove the auto-update path on a second machine.

## 0.2.0 — 2026-06-26
- First real-content release: the CrossLoom MCP server, two auto-firing knowledge Skills
  (ObjectType cheat-sheets dispatcher + first-contact orient), and a SessionStart conventions
  hook. (L2-01 / L2-04.)
