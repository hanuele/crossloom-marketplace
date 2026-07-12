# CrossLoom — Always-On Conventions

> Injected into every session by the `crossloom` plugin (SessionStart hook).
> **Conventions only** — the *mental model*, the *environment*, the *discipline*,
> and *where the knowledge lives*. The actual per-ObjectType knowledge is in the
> plugin's auto-firing Skills and the `cl` tool — not here. Keep this lean.
>
> _Last verified: 2026-07-02._

## CrossLoom is not in the model's training data

Do **not** answer CrossLoom-specific questions from memory — you will confabulate.
Read the live source: the `cl` tool, the auto-firing Skills, and the running
instance. When unsure, verify against the instance before asserting.

## The non-negotiable mental model

- **Everything is an object with an immutable UUID.** The UUID is universal across
  every instance, stage (DEV/QA/PROD), and application. A UUID given without app
  context is intentional and sufficient (default app = Admin
  `18027c26-f8c8-4ff3-8875-119e480336e6`).
- **No build step — scripts and UIs are hot-deployed.** The deployed object *is*
  the source of truth ("browser scripts are canonical"). The next request loads
  the saved version.
- **`save` preserves the UUID; `create` mints a new one.** Edit an existing object
  with `save`/`cl write`; only `create` for a genuinely new object. (`cl save` does
  not exist — the verb is `cl write`.)
- **HTTP 200 ≠ persisted.** For typed objects (a base row + a typed-table row), the
  data API can return 200 while the typed INSERT silently no-ops — e.g. creating
  under the zero-GUID root, or a create that doesn't map structural FK columns.
  **Always verify a create/edit by reading the object back** (`cl read` /
  `inspect_object`). Re-reading is the portable, always-true check.

## The environment — which instance you are on

- Your CrossLoom dev instance and env are whatever your active `cl env` reports
  (`cl env show`) — the live env is the source of truth, not a hardcoded host. All
  tool development and live probes happen against your onboarding env.
- Set it once: **`cl env use <your-env>`**, then `cl ping` to confirm.
- The active env is **machine-global** — switching affects everyone on the box. For
  any write/destructive probe, pass an explicit `--env <your-env>` rather than
  trusting the ambient env.
- ⚠️ **Customer-env guard:** if `cl env show` is not your onboarding env, **STOP** and
  switch back first — never build, probe, or test against another instance. Canonical
  guard: `docs/ENV-SETUP.md` §Customer-env guard.

## `cl`-first discipline

`cl` is your read/write/verify surface to the instance. Reach for it before raw SQL
or guesswork.

- **Run `cl --help` first** — it self-documents the full command surface and saves
  time. (`cl --version` proves the wheel is installed and on PATH.)
- **`cl whatis <uuid>`** is the FIRST call for any unknown UUID — Title, Type,
  TableName, and App in one shot.
- **The fix is usually in the error message.** When a `cl` call fails, read the
  error body before retrying — it lists the available (type-specific,
  case-sensitive) property names or names the bad SQL column. The per-type sheets
  carry the exact property names; don't guess them.
- **Discover the schema before you SELECT** (`cl schema columns <TABLE>`) and
  resolve a type's UUID from a *live* object of that type — UUIDs copied from notes
  go stale.

## TrustedScripts (server-side C#) — pointer, not the rules

C# TrustedScripts JIT-compile as a single self-contained `public class
CL_TrustedCode`. There are four JIT invariants that, if skipped, cost ~90 minutes
of trial-and-error each time. **Before writing or editing any C# TrustedScript**,
read the TrustedScript type sheet (below) and lint with **`cl validate-script
<uuid>`**. MSBuild-green ≠ JIT-green — always validate, then smoke-run.

## Where the knowledge lives (not in this file)

This file is conventions only. For actual CrossLoom knowledge, the plugin gives you
three auto-firing Skills plus the `cl` corpus:

- The **`crossloom:objects`** Skill — per-ObjectType cheat-sheets (the dispatcher
  routes you to the exact sheet for the type you're working on).
- The **`crossloom:orient`** Skill — fires when you're new to CrossLoom or need the
  mental model + onboarding map.
- The **`crossloom:connect`** Skill — fires when you can't connect (auth/env failures,
  `cl ping` fails); walks first-run environment setup.
- **`cl howto <type>`** — the per-type sheet on the CLI. `cl howto` (no arg) lists
  the living set.
- **MCP Resource** `cl://knowledge/<type>` — the same sheets via `ReadMcpResourceTool`.

Ask about a CrossLoom ObjectType and the Skills surface unprompted — you do not need
to `@`-mention anything.

## What you do NOT have (don't chase it)

This install is a standalone CrossLoom toolkit, not the maintainer's full
environment. **There is no mycelium graph and no `cl recall`** (those query a
knowledge graph this install lacks), and **no inter-instance bus**. If guidance ever
points you to `cl recall`, `query-mycelium`, or a "sangha" surface, that is
maintainer-only — use `cl howto`, the Skills, and the live instance instead.
