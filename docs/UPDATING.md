# Updating CrossLoom — what updates what

> # 🛑 ERRATUM 2026-07-12 — the `url` form in §3 DOES NOT WORK. Do not use it.
>
> **`"source": {"source": "url", "url": "https://github.com/hanuele/crossloom-marketplace.git"}`
> cannot fetch this marketplace, and never could.** Claude Code resolves the `url` form with an
> **unauthenticated HTTP GET** — no git, no credentials. Against a **private** repo that is a
> hard `404`, every time, forever.
>
> Measured on 2026-07-12, same URL shape, unauthenticated:
>
> ```
> 200   https://github.com/anthropics/claude-code.git          (a PUBLIC repo)
> 404   https://github.com/hanuele/crossloom-marketplace.git   (ours — PRIVATE)
> ```
>
> and Claude Code's own `/plugin` → `Errors` tab, on a machine configured this way:
>
> ```
> HTTP 404 error while downloading marketplace from
> https://github.com/hanuele/crossloom-marketplace.git
> ```
>
> **Why this was believed to work — the mistake is worth naming, because it is the second time
> the same one has bitten this plan.** The probe that ratified this form (#249) ran
> **`git clone https://…` by hand**, saw it succeed, and concluded the HTTPS URL was fine. But
> **Claude Code never git-clones the `url` form — it HTTP-downloads it.** The probe verified a
> mechanism the product does not use. *Test the path the product takes, not a path that
> resembles it.*
>
> ### What actually works today
>
> Only the `github` + `repo` form, which git-**clones** — and therefore carries credentials:
>
> ```json
> "crossloom": {
>   "source": { "source": "github", "repo": "hanuele/crossloom-marketplace" },
>   "autoUpdate": true
> }
> ```
>
> **But this clones over SSH, so it needs a GitHub SSH key** — which onboarded developers are
> *not* issued (they get HTTPS credentials). So for a typical external dev, **there is currently
> no working plugin auto-update path at all**, and it fails **silently**: no update arrives,
> nothing says why.
>
> **This is escalated and awaiting a decision** (make the marketplace public, vs. issue SSH keys).
> Until it is resolved, treat everything below about "automatic" delivery as **describing the
> intended design, not the shipping reality.** `cl update` is what moves things today.

> **Read this first if you are about to turn on plugin auto-update, or you are wondering
> why a new cheat-sheet or `cl` command has not reached your machine.**
>
> CrossLoom reaches you over **two independent trains**. They ship different things, they
> come from different repositories, and **they update by different commands.** Turning on
> plugin auto-update updates **one** of them. That is the single most important fact on
> this page, and the one that surprises everybody.
>
> Companion docs: [`AUTO-UPDATE.md`](./AUTO-UPDATE.md) (the *plugin* train in depth — owner
> release flow + managed-settings) and the crossloom-cli `docs/UPDATING.md` (the *wheel*
> train in depth).

---

## 1. The two trains

| | **Train A — the wheel** | **Train B — the plugin** |
|---|---|---|
| **What it is** | the `crossloom-cli` Python package | the `crossloom` Claude Code plugin |
| **Comes from** | `hanuele/crossloom-cli` (**private**) | `hanuele/crossloom-marketplace` (**also private**) |
| **Installed by** | `pip install "crossloom-cli[ai] @ git+…"` | `/plugin install crossloom@crossloom` |
| **Updated by** | **`cl update`** — you run it | **automatic**, silently at launch (if enabled) |
| **Needs credentials?** | **Yes** — GitHub read access (GCM login or a PAT) | **Yes** — same GitHub read access (see the warning below) |

> ### ⚠ Both repos are PRIVATE — auto-update needs GitHub credentials too
>
> **Corrected 2026-07-12.** An earlier revision of these docs stated the marketplace repo was
> *public* and that plugin auto-update *"needs no credentials at all."* **That was wrong.**
> `hanuele/crossloom-marketplace` is **private** — an unauthenticated request returns `404`
> (API) / `401` (git clone endpoint).
>
> **How the error was made, because it is worth not repeating:** the original probe ran
> `git clone https://…` on a machine that already had GitHub credentials cached in Git
> Credential Manager, saw `exit 0` **with no credential prompt**, and concluded "public."
> **The absence of a credential prompt is not evidence of the absence of authentication** — a
> machine with cached creds clones a *private* repo silently too. Ask the repo, not the clone.
>
> **What this means in practice:** the developer needs GitHub read access **before** plugin
> auto-update can fetch anything — the same credentials the wheel needs (the onboarding
> runbook's GitHub-credentials step, which it flags as *"the historically deadliest step"*).
> If those credentials are missing or expired, **auto-update fails quietly**: no plugin update
> arrives and nothing says why.
>
> The HTTPS `.git` form below is still the **right** fix and still strictly better than the
> `github`+`repo` shorthand — devs are issued **HTTPS** credentials during onboarding, and are
> *not* issued SSH keys. Only the *reason* changed: it works because they **have** credentials,
> not because none are needed.

**The one-line mental model:**

> **The plugin ships the _knowledge_. The wheel ships the _capability_.**
> Auto-update keeps what CrossLoom *knows* current. Only `cl update` moves what `cl` can *do*.

Draw the line at "is this text, or is this code?":

- **Text** — the ObjectType cheat-sheets, the conventions, the Skills — rides the **plugin**,
  and therefore auto-updates. A gotcha curated today reaches you at your next session.
- **Code** — the `cl` commands, the MCP tools, the quality package — rides the **wheel**,
  and moves only when you run `cl update`. A *new tool* still needs that.

> **Changed in plugin 0.3.0 (2026-07-12).** Before 0.3.0 the plugin shipped only a *routing
> table* — `SKILL.md` pointed at `cl howto <type>` / `cl://knowledge/<type>`, both served by
> the wheel. So the map auto-updated but the territory did not, and curated knowledge could
> not reach a developer without a manual `cl update`. **The 20 sheets are now vendored into
> the plugin** (`plugins/crossloom/skills/objects/knowledge/*.md`), as a generated mirror of
> the wheel's `crossloom_cli/knowledge/` — one authoring surface, two shipping channels.
> If you read an older version of this document that said knowledge rides only the wheel:
> that was true when it was written, and is no longer true.

---

## 2. What each train carries (exact)

### Train A — the wheel (`cl update`) — **NOT auto-updated**

- The **`cl` CLI** — every command (47 of them: `cl read`, `cl write`, `cl howto`, `cl ping`,
  `cl env`, `cl quality`, …).
- The **MCP server code** — i.e. **every MCP tool the model can actually call** (63 tool
  registrations: `inspect_object`, `code_grep`, `create_changeset`, `search_knowledge`, …).
  The plugin only says *where to start the server*; the wheel **is** the server.
- The **20 ObjectType knowledge sheets** (`crossloom_cli/knowledge/*.md`) — **the authoring
  source.** Since plugin 0.3.0 these are also *mirrored into the plugin*, so a dev gets the
  current text without `cl update`; the wheel's copies remain what `cl howto <type>` and
  `cl://knowledge/<type>` serve, and they are where a curated gotcha is written.
- The **34 playbook / onboarding / reference docs** served as `cl://onboarding/*`,
  `cl://playbook/*`, `cl://reference/*`. **Still wheel-only** — not yet mirrored.
- The **quality package** (47 payload files, via `cl quality extract`).
- The **telemetry** instrumentation.

### Train B — the plugin (auto-update) — **silently updated at launch**

- **The 20 ObjectType knowledge sheets** (`plugins/crossloom/skills/objects/knowledge/*.md`)
  — **new in 0.3.0.** A generated, byte-identical mirror of the wheel's sheets, shipped beside
  the dispatcher Skill and read as `${CLAUDE_SKILL_DIR}/knowledge/<type>.md`. **This is what
  lets a gotcha curated today reach a dev tomorrow with no `cl update`.** It is a *build
  artifact* — nobody hand-edits it; a CI guard here re-hashes every sheet against the shipped
  `.manifest.json` on every push, and crossloom-cli's own test suite fails if the mirror and
  the authored sheets ever diverge.
- **`.mcp.json`** — the MCP server *registration* (`python -m crossloom_cli.mcp.server`).
  This is **wiring, not capability**: it says how to launch the server, not what the server can do.
- **The 3 Skills** — `objects` (the ObjectType dispatcher), `orient` (first-contact), `connect`
  (first-run env setup).
- **`CONVENTIONS.md`** — injected into every session by a SessionStart hook. This *does* carry
  real content (the always-on CrossLoom conventions and cross-cutting gotchas).
- **`compat.json`** — `min_cl_version`, the minimum wheel version this plugin release needs.
- **The hooks** — `emit_conventions.py`, `check_wheel_version.py`.

---

## 3. So: what actually happens when you enable plugin auto-update?

You put this in your settings (managed, user, or project — see
[`AUTO-UPDATE.md`](./AUTO-UPDATE.md) §2):

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

From then on, at every launch, **without you doing anything**:

### ✅ You DO get, silently
- New or reworded **Skills** — including new *routing entries* (e.g. a newly supported
  ObjectType appearing in the dispatcher's table).
- Updated **`CONVENTIONS.md`** — so a new always-on convention or cross-cutting gotcha
  written *there* **does** reach you automatically.
- Updated **hooks** and **MCP registration**.
- A raised **`min_cl_version`** floor — and therefore the nudge in §4.

### ❌ You do NOT get, ever, from plugin auto-update
- **A new or corrected ObjectType cheat-sheet.** `cl howto ttx_Lookups` and
  `cl://knowledge/ttx_Lookups` keep serving **your installed wheel's** copy. If a maintainer
  fixes a wrong gotcha in a sheet today, your sessions keep reading the old, wrong one until
  you run `cl update`.
- **A new MCP tool.** The Skill may now *tell the model to call* `preview_changeset_coverage`;
  if your wheel predates that tool, the call **fails** — the Skill was updated, the server
  behind it was not.
- **A new `cl` command**, a bug-fix in an existing one, or new playbook/reference content.
- **Anything at all in the wheel.** The wheel is not touched by any part of this mechanism.

> **The blunt version:** plugin auto-update can update the *instructions for using a
> capability* without updating *the capability*. That asymmetry is the whole reason §4 exists.

---

## 4. The skew guard — why a session sometimes nags you to run `cl update`

Because the two trains move independently, an auto-updated Skill can point at a `cl`/MCP
capability your wheel does not have. To stop that failing silently, each plugin release
declares the wheel floor it needs in **`compat.json`** (`min_cl_version`), and a SessionStart
hook (`hooks/check_wheel_version.py`) compares it to your installed `cl --version`:

| Your wheel | What you see at session start |
|---|---|
| **≥ floor** | *nothing* — zero added output |
| **< floor** | one line: *"your crossloom-cli wheel is X, but this plugin release needs ≥ Y … Run `cl update`."* |
| **`cl` missing** | one line pointing at the install docs (this is also the silent-dead-MCP-server signal) |

**That nudge is the design admitting the gap.** It is not a bug — it is the honest mitigation
for two trains with no coupling. When you see it, run `cl update`.

### 4b. The staleness check — the *other* watcher, and the one that catches quiet releases

The skew guard above compares your wheel to a **floor**. It has a blind spot, and it is a big
one: **the floor only rises when a maintainer raises it.** A release that ships a corrected
knowledge sheet, a `cl` bugfix, or a security fix — anything needing no *new capability* —
does **not** move `min_cl_version`, so the hook stays **silent** and you sit on a stale wheel
**looking perfectly compliant.**

Two watchers, two different failure modes. You need both:

| Watcher | Compares against | Catches | Reaches |
|---|---|---|---|
| SessionStart hook (§4) | the **floor** (`compat.json`) | **capability skew** — a Skill routes to a tool you lack | plugin users only |
| **MCP staleness check** (in the wheel) | the **latest** published version | **staleness** — your code/content is just old | anyone using the MCP server, **plugin or not** |

The second one lives in the wheel's MCP server, so it also reaches devs who registered the
server **without** the plugin — whom the hook can never reach at all.

**What you'll see** — at most **once a day**, on a tool call:

```
[crossloom] Update available: 0.4.0 -> 0.5.2. Run `cl update` to upgrade the wheel …
```

- **The check is automatic; the upgrade stays human.** The MCP server will *never* run
  `pip install` — reinstalling the wheel would disrupt the very server process the agent is
  talking to. It reports; **you** run `cl update`.
- **It never delays a tool call.** The check runs on a background thread — a real one measures
  **2.6–4.5s** — so it is deliberately off the critical path; the notice rides a later call.
- **Quiet about what you cannot act on — loud about what you can.** Offline, git missing, or a
  timeout → **nothing is shown**; those are transient. But a **credential refusal** stays broken
  until a human fixes it, so the check **says so**, once a day — a lapsed GCM token or rotated
  PAT would otherwise starve you in perfect silence, with your knowledge sheets quietly rotting
  and no update notice ever arriving. **An unknown is never reported as "up to date".**
- **Opt out:** `CROSSLOOM_MCP_UPDATE_CHECK_OFF=1`.

Full detail: the wheel's own `docs/UPDATING.md`.

---

## 5. How to update — both trains

```bash
# Train A — the wheel (the CLI, the MCP tools, the knowledge sheets)
cl update              # check, then upgrade to the newest release tag if stale
cl update --check      # report installed-vs-latest, change nothing
cl update --dry-run    # print the exact pip command without running it
cl update --force      # reinstall from source HEAD (unpinned escape hatch)
```

`cl update` needs **GitHub read access to the private `hanuele/crossloom-cli` repo** (GCM
login or a PAT). If it reports an auth failure, that is the credential prerequisite, not an
outage — see the onboarding runbook's GitHub-credentials step.

```
# Train B — the plugin (Skills, conventions, hooks, MCP wiring)
#   Auto-update ON  -> nothing to do; it arrives at next launch.
#                      A notification says "Plugin updates available";
#                      run /reload-plugins to activate it in-session.
#   Auto-update OFF -> /plugin marketplace update crossloom
#                      /reload-plugins
```

### To be fully current, run **both**

```bash
cl update            # then, in Claude Code:
```
```
/plugin marketplace update crossloom   # (only if auto-update is off)
/reload-plugins
```

## 6. How to check what you are actually on

```bash
cl --version                       # your wheel version  (Train A)
```
```
/plugin                            # Installed tab -> crossloom @ <version>  (Train B)
```

If a Skill or tool is behaving as if a fix never landed, **check both numbers before
reporting a bug.** A mismatched pair is by far the most common cause, and it looks exactly
like a broken feature.

---

## 7. Known limitation — **CLOSED in plugin 0.3.0** (2026-07-12)

**Previously:** curated ObjectType knowledge rode the train that does *not* auto-update. A
gotcha learned and curated today landed in the wheel's `knowledge/<Type>.md`, so it reached a
developer only when they next ran `cl update` — not automatically. That was a seam between two
individually-sound choices (single-source knowledge in the wheel; auto-update on the plugin)
that neither choice owned.

**Now:** the 20 sheets are **vendored into the plugin as a generated mirror**
(`plugins/crossloom/skills/objects/knowledge/`). The wheel remains the only place anyone
*edits* them; the mirror is a build artifact, regenerated by crossloom-cli's
`scripts/sync_plugin_knowledge.py` and guarded on both sides:

- **crossloom-cli CI** opens the mirror PR automatically whenever a sheet changes on `main`,
  and its test suite fails if the mirror ever diverges from the authored sheets;
- **this repo's CI** (`scripts/verify_knowledge_mirror.py`) re-hashes every shipped sheet
  against the `.manifest.json` beside it and fails on any hand-edit, missing sheet, or sheet
  the dispatcher does not route to.

So a curated gotcha now reaches a developer's **next session**, with no `cl update`.

### What still needs `cl update`

Knowledge auto-updates; **capability does not.** You still need `cl update` for:

- a **new or changed `cl` command** or **MCP tool** (the wheel *is* the MCP server);
- the **playbook / onboarding / reference docs** (`cl://playbook/*` etc.) — not yet mirrored;
- the **quality package**;
- any plugin release that raises `min_cl_version` — the session will tell you (§5).
