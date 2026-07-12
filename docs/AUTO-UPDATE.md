# Auto-update — owner release flow + dev managed-settings

> # 🛑 ERRATUM 2026-07-12 — §2's managed-settings block DOES NOT WORK. Do not ship it.
>
> The `"source": {"source": "url", "url": "…/crossloom-marketplace.git"}` block below **cannot
> fetch this marketplace, and never could.** Claude Code resolves the `url` form with an
> **unauthenticated HTTP GET** — no git, no credentials. Against a **private** repo that is a
> hard `404`.
>
> Measured 2026-07-12, same URL shape, unauthenticated — and reproduced in Claude Code's own
> `/plugin` → `Errors` tab on a machine configured exactly as §2 says:
>
> ```
> 200   https://github.com/anthropics/claude-code.git          (a PUBLIC repo)
> 404   https://github.com/hanuele/crossloom-marketplace.git   (ours — PRIVATE)
>
> HTTP 404 error while downloading marketplace from
> https://github.com/hanuele/crossloom-marketplace.git
> ```
>
> **How this shipped, named so it stops happening.** The probe that ratified this form (#249)
> ran **`git clone https://…` by hand**, saw `exit 0`, and concluded the HTTPS URL was sound.
> But **Claude Code never git-clones the `url` form — it HTTP-downloads it.** The probe verified
> a mechanism the product does not use. That is the same error as the erratum below (*"a machine
> with cached credentials clones a private repo silently too"*) wearing a different coat:
> **both times, a hand-run command stood in for the product's real code path.**
> *Test the path the product takes, not one that resembles it.*
>
> ### The state of play
>
> | Form | What Claude Code does | Against our PRIVATE repo |
> |---|---|---|
> | `source: "url"` | unauthenticated **HTTP GET** | ❌ `404`, always |
> | `source: "github"` + `repo` | **git clone over SSH** | ✅ *only with a GitHub SSH key* |
>
> Onboarded developers are issued **HTTPS** credentials and are **not** issued SSH keys. So for
> a typical external dev **there is currently no working auto-update path**, and it fails
> **silently** — no update arrives, nothing says why. (Observed live: an install with
> `autoUpdate: true` that had not fetched since 29 June and never reported it.)
>
> **Escalated, awaiting a decision:** make the marketplace **public** (then the `url` form works
> with zero credentials, for everyone), or **issue SSH keys** to the dev cohort. Until that is
> settled, do not hand §2's block to a developer — it will 404. Read the rest of this page as
> the **intended design, not the shipping reality.**

> ## ⚠ SCOPE — this page covers the **plugin** only
>
> Everything below describes auto-update of the **`crossloom` plugin** (Skills, `CONVENTIONS.md`,
> hooks, MCP *wiring*). It does **NOT** cover the **`crossloom-cli` wheel** — the `cl` CLI, the
> MCP **tools** themselves, and the **ObjectType knowledge sheets**. The wheel is a **separate
> train with no auto-update**: it moves only when the developer runs **`cl update`**.
>
> A reader who takes this page as the whole update story will conclude that a corrected
> cheat-sheet reaches every dev automatically. **It does not.**
>
> **→ For what-updates-what across BOTH trains, read [`UPDATING.md`](./UPDATING.md) first.**

> **What this is.** How a CrossLoom-toolkit maintainer ships an update through the
> `hanuele/crossloom-marketplace` git marketplace, and how it reaches an external 3TXpert
> dev's machine **automatically at next launch** — no manual reinstall. This is the
> distribution leg of the onboarding flywheel (plan L2-02).
>
> **Believe-the-source note.** The mechanism below was confirmed against the live Claude Code
> docs on **2026-06-26** (`code.claude.com/docs` — "Discover and install prebuilt plugins" §
> _Configure auto-updates_; "Create and distribute a plugin marketplace" § _Version resolution
> and release channels_). This surface is young and moving — re-confirm before relying on a
> field name. One thing the original ticket got wrong: **auto-update is NOT a `marketplace.json`
> field** — it is a *client* managed-setting (see §2).

---

## The two facts that shape everything

1. **Self-hosted marketplaces have auto-update OFF by default.** (Only Anthropic's official
   marketplaces default to on.) To get silent updates you must turn it on per-marketplace via
   **managed settings** (§2).
2. **A pinned `version` only moves when you bump the string.** Claude Code resolves a plugin's
   version as **`plugin.json` version → marketplace entry version → git commit SHA** (first
   present wins). Auto-update pulls a new version only when that resolved string changes. So:
   - **Keep `version` and bump it** → controlled releases (what we do).
   - **Omit `version`** → every git commit is a new version (too noisy for an external cohort).

---

## 1. Owner-side: cut a release

You change plugin content, then publish by bumping the version in **both** places that carry it
(plugin.json wins the resolution order, so it MUST move):

1. `plugins/crossloom/.claude-plugin/plugin.json` → bump `"version"` (e.g. `0.2.0` → `0.2.1`).
2. `.claude-plugin/marketplace.json` → bump the matching `plugins[].version`.
3. **Review `plugins/crossloom/compat.json` → `min_cl_version`** — the minimum crossloom-cli
   **wheel** version this plugin release needs. If this release's Skills or MCP wiring depend on
   a `cl`/MCP capability newer than the current floor, **raise it**; otherwise leave it. The
   SessionStart `check_wheel_version.py` hook nudges any dev whose installed `cl` is below this
   floor (`cl update` fixes it). Name the floor in the CHANGELOG entry so the release record
   states which wheel it needs (#180).
4. Add a `plugins/crossloom/CHANGELOG.md` entry naming what changed (and the wheel floor).
5. Commit + push to the marketplace repo's **default branch** (`main`). Auto-update reads the
   default branch, so a feature branch publishes nothing until merged.

That's the whole publish step. The next launch on every auto-update-enabled machine pulls it.

### The knowledge mirror is NOT a manual release step (#285)

`plugins/crossloom/skills/objects/knowledge/*.md` — the 20 ObjectType sheets — is a **generated
mirror** of crossloom-cli's `src/crossloom_cli/knowledge/`. **Do not hand-edit it, and do not
"remember to sync it" before a release.** Neither is needed, and both are how it would rot:

- crossloom-cli's `sync-plugin-knowledge` workflow opens the mirror PR **automatically** when a
  sheet changes on its `main`. Your job is to review and merge that PR (then cut a release as
  above so it ships).
- this repo's CI (`scripts/verify_knowledge_mirror.py`) fails on any sheet that does not match
  the `.manifest.json` shipped beside it, is not routed by the dispatcher Skill, or was added by
  hand. A hand-edit cannot reach `main`.

To edit a sheet: change it in **crossloom-cli**, merge there, and the PR appears here. That is
the whole loop, and it is the loop that lets a gotcha curated today reach a developer tomorrow
without them running `cl update`.

## 2. Enable auto-update — same block, three scopes

`extraKnownMarketplaces` (with `autoUpdate: true`) works at **any settings scope** — managed,
user, or project (confirmed against the live docs 2026-06-26). Same JSON block everywhere; the
scope decides who it applies to and whether admin is needed.

**For the developer cohort — enforced, admin-pushed (the D-5=Yes path):** the **managed**
settings file.
- **Windows (v2.1.75+):** `C:\Program Files\ClaudeCode\managed-settings.json` — the admin must
  **create** the directory and file; it is **not** auto-created (the legacy
  `C:\ProgramData\ClaudeCode\...` path is deprecated as of v2.1.75).
- Merge the `extraKnownMarketplaces` key; don't overwrite other managed settings.

**For a single dev / no admin (simplest):** put the same block in the **user** settings file
`~/.claude/settings.json` (Windows: `C:\Users\<user>\.claude\settings.json`) — no admin, no
system path. **Or no file at all:** `/plugin` → **Marketplaces** tab → select the marketplace →
**Enable auto-update** (an interactive toggle that persists).

The block (see [`managed-settings.example.json`](./managed-settings.example.json)):

```json
{
  "extraKnownMarketplaces": {
    "crossloom": {
      "source": { "source": "url", "url": "https://github.com/hanuele/crossloom-marketplace.git" },
      "autoUpdate": true
    }
  }
}
```

This both **declares** the marketplace (so the dev doesn't run `/plugin marketplace add`) and
turns on **silent startup auto-update** for it.

> **Use the explicit `url` `.git` form — NOT `github`+`repo` (verified 2026-07-07, task #249).**
> The `{ "source": "github", "repo": "hanuele/crossloom-marketplace" }` shorthand does **not**
> reliably clone over HTTPS: the transport is machine-dependent, and on a fresh Windows machine
> with HTTPS/GCM credentials but **no GitHub SSH key** it resolved to an **SSH** clone
> (`git@github.com:…`) and failed with `No ED25519 host key is known for github.com … Host key
> verification failed` — the same blocker an external dev hit on the interactive path. The
> explicit `url` `https://…​.git` form clones over **HTTPS** (no SSH key needed) and — because it
> is a `.git` clone URL, not a raw `marketplace.json` URL — still resolves the marketplace's
> relative plugin source (`./plugins/crossloom`). Evidence:
> `vault/docs/plans/crossloom-external-onboarding/L2-249-transport-evidence-2026-07-07.md`.
>
> **ERRATUM (2026-07-12) — this repo is PRIVATE, and auto-update needs credentials.**
> An earlier revision of this paragraph said the HTTPS form works because *"the repo is public,
> so it needs no credentials at all."* **That was false.** `hanuele/crossloom-marketplace` is
> **private**: unauthenticated it returns `404` (API) / `401` (git clone endpoint). The original
> probe cloned successfully on a machine that already held cached GCM credentials and read the
> **absence of a credential prompt** as proof the repo was public — it is not; a machine with
> cached creds clones a private repo silently too. **Ask the repo, not the clone.**
>
> The fix itself is unchanged and still correct — HTTPS is right precisely because onboarded devs
> **are** issued GitHub HTTPS credentials and are **not** issued SSH keys. But note the real
> dependency: **plugin auto-update cannot fetch until the dev has GitHub read access** (the
> runbook's GitHub-credentials step), and if those credentials are absent or expired it fails
> **silently** — no update arrives and nothing says why. Order the onboarding accordingly:
> credentials **before** the managed-settings marketplace declaration. See
> [`UPDATING.md`](./UPDATING.md) for the full two-train picture.
> Note (Claude Code does NOT normalize URL identity): the `url` form is a *different*
> marketplace identity than the old `github`+`repo` one, so on a machine that already carried
> the shorthand both may coexist — irrelevant for a fresh dev-cohort onboarding, where only this form
> is declared.

## 3. What the dev sees when an update ships

1. They relaunch Claude Code. At startup it fetches `marketplace.json`, sees the bumped version,
   and pulls it silently.
2. A notification appears: **"Plugin updates available — run `/reload-plugins`."**
3. They run **`/reload-plugins`** → it activates the new version in-session (no restart).
   - **Caveat:** if the plugin's MCP server is loaded and tool-search isn't deferring tools,
     `/reload-plugins` warns it will invalidate the prompt cache and needs `--force`.

> **Tested live (2026-06-26 → 27).** Cross-machine *propagation* is proven — a machine sitting
> at `0.2.1` with auto-update enabled, after `0.2.2` was published, resolved the new version with
> no reinstall. But *silent-at-startup* is **inconclusive / pending a clean fully-rebooted
> second-machine test**: the *very first* relaunch immediately after a publish may still render
> the OLD version (a fetch/cache settle lag — a fresh launch showed `0.2.0` while the update
> check already resolved `0.2.1`); a normal subsequent launch applies it. So set the dev's
> expectation as *"updates arrive on their own at launch,"* not *"instantly the second the owner
> publishes."* (Verdict consistent with the CHANGELOG 0.2.2 entry + #127.)

## 4. Fallback — non-managed machines

A future *non-managed* dev (no pushed managed-settings) does not get silent updates. Their path:

```
/plugin marketplace update crossloom   # pull the latest marketplace state
/reload-plugins                        # activate it
```

Document this as the fallback only — it is **not** the dev-cohort path.

---

## 5. Retract — pulling back a bad version

When a bad version has shipped, two levers exist. **Prefer the forward-bump** (it also reaches
auto-update-*off* machines and needs no per-machine action); the pull/pin is a validated backstop.

**Primary — emergency forward-bump.** Fix the content, bump to a *higher* version in both
`plugin.json` + `marketplace.json`, push to `main`. The fix rides the same silent auto-update
path to every enabled dev at next launch.

**Secondary — pull the entry / pin to last-good.** Remove the bad version from `marketplace.json`
(or pin managed settings to the last-good version).

> **Does this downgrade a machine *already* on the bad version? YES (tested #182, 2026-07-03).**
> When the marketplace offers a version **lower** than the one installed, Claude Code's
> update/resolution moves the installed plugin **down** to the offered version — it is **not**
> forward-only. Observed directly: `Plugin "…" updated from 0.0.2 to 0.0.1`, and
> `installed_plugins.json` then read `0.0.1`. So the pull/pin lever is an **active rollback**, not
> merely stop-the-spread.
>
> **Scope of the proof:** demonstrated for the update mechanism (manual `/plugin update
> <plugin>@<marketplace>`). The **silent-startup** arm (`autoUpdate:true`, downgrade at next
> launch) uses the same resolution and is expected to behave identically, but was inferred rather
> than directly observed (a headless `claude -p` does not trigger startup auto-update sync — a
> full interactive relaunch does). **Restart applies the change** (the state file downgrades
> immediately; the running plugin loads the older version on restart).

---

## Verification — the live second-machine test (AC3, non-negotiable)

A plugin that installs but silently fails to auto-update defeats the whole plan, so this is
proven on a **real second machine**, not asserted:

1. **Baseline (machine 2):** managed-settings from §2 in place; `/plugin install crossloom@crossloom`;
   confirm the Installed tab shows **crossloom @ `<current>`** (e.g. 0.2.0).
2. **Publish (owner machine):** bump to the next version (§1) + push to `main`.
3. **Verify (machine 2):** relaunch Claude Code → the update notification fires at startup →
   `/reload-plugins` → confirm the Installed tab now shows **crossloom @ `<bumped>`** (e.g. 0.2.1).
4. **Capture** both machines' before/after version in the L2-02 closure.

> Use a *real* second machine (a clean profile on another box, or a second physical machine) —
> a local re-clone cannot exercise the startup auto-update path.
