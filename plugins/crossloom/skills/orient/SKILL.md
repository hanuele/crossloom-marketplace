---
description: First-contact orientation for CrossLoom — the object model, the cl/MCP surface map, and where to start. Use when the user is new to CrossLoom, asks "how do I start / where do I begin / I just got access", is setting up or installing CrossLoom for the first time, or needs the 5-minute on-ramp before working on the platform.
last_verified: 2026-07-02
verified_against: "florencia routing probe 2026-06-26 (orient HIT, discoverability); content is portable platform axioms (CLAUDE.md/MISSION), not individually re-walked this pass. Freshness header backfilled by #118."
---

# Orient — starting on CrossLoom

> **CrossLoom is not in your training data.** Read the live source, not memory. This skill
> is the on-ramp; the depth lives in the bundled onboarding Resources it points to.

## The mental model (portable, inline)

- **Everything is an object.** Every object has an immutable **UUID**, universal across all
  instances, stages (DEV/QA/PROD), and applications. CrossLoom is an integration platform +
  moldable app-dev environment (UI builder, script engine, data sync, REST Junctions, a
  universal object store) — all code-in-database, no build step (hot-deploy on next request).
- **MCP is the primary action surface; the `cl` CLI is the backup.** Both reach the same
  instance with the same credentials. Prefer the MCP tools (e.g. `inspect_object`,
  `deploy_trusted_script`); drop to `cl` for anything the tools don't cover.
- **Per-ObjectType conventions** auto-surface via the companion *ObjectType cheat-sheets*
  skill — or pull one directly with `cl howto <type>`.

## Read these to go deeper (pointers, not copies)

Read on demand with `ReadMcpResourceTool` (server `crossloom`):
- `cl://onboarding/claude-quickstart` — the agent quickstart / on-ramp.
- `cl://onboarding/how-a-claude-becomes-useful` — how to become productive here.
- `cl://onboarding/webdev-path` — **the on-ramp for a web developer** (likely your starting path).
- `cl://onboarding/trainee-path` — the structured learning path for building competence.
- `cl://onboarding/glossary` — CrossLoom terminology.
- `cl://reference/known-pitfalls` — the live traps to avoid before your first change.
- `cl://onboarding/crossloom-base` — the canonical base layer **(bundled by task #103; once
  shipped this is the single source of truth — read it first when present).**

> These are the wheel-bundled MCP Resources — the one source. This skill deliberately points
> at them rather than copying their text, so there is no second copy to drift.

## First steps on a fresh install
1. Confirm the prerequisite + connection: `cl --version`, then `cl ping` (see the marketplace
   README for the Python/`cl`-wheel prerequisite). **If `cl ping` fails or you have no
   environment yet, the `crossloom:connect` skill (or the marketplace repo's ENV-SETUP.md at https://github.com/hanuele/crossloom-marketplace/blob/main/docs/ENV-SETUP.md)
   walks first-run setup** (`cl env add` → `cl env use` → `cl ping`).
2. Skim `cl://onboarding/claude-quickstart` + `cl://reference/known-pitfalls`.
3. Working with a specific ObjectType? The ObjectType cheat-sheets skill routes you, or run
   `cl howto <type>`.

> **`cl recall` is sister-only** — it needs the sangha mycelium graph an external install
> doesn't have. Use the Resources above and live `cl`, not `cl recall`.
