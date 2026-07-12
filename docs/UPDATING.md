# Updating CrossLoom — what updates what

> **Read this if you are setting up auto-update, or wondering why a new cheat-sheet or `cl`
> command has not reached your machine.**
>
> CrossLoom reaches you over **two independent trains**. They ship different things, they come
> from different repositories, and **they update by different commands.** That is the single
> most important fact on this page, and the one that surprises everybody.

---

## 1. The two trains

| | **Train A — the plugin** | **Train B — the wheel** |
|---|---|---|
| **What it is** | the `crossloom` Claude Code plugin | the `crossloom-cli` Python package |
| **Comes from** | `hanuele/crossloom-marketplace` — **public** | `hanuele/crossloom-cli` — **private** |
| **Installed by** | `/plugin install crossloom@crossloom` | `python -m pip install "crossloom-cli[ai] @ git+…"` |
| **Updated by** | **automatic**, at launch (with `autoUpdate`) | **manual** — when a new floor is announced |
| **Needs credentials?** | **No** — none at all | **Yes** — GitHub read access (GCM login or a PAT) |

The marketplace is public *on purpose*. Auto-update runs silently in the background, and a
silent channel that needs credentials is a channel that silently stops working for whoever
lacks them. The wheel repo stays private; that is the one step that asks you to log in.

**The one-line mental model:**

> **The plugin ships the _knowledge_. The wheel ships the _capability_.**
> Auto-update keeps what CrossLoom *knows* current. Only a wheel upgrade moves what `cl` can *do*.

Draw the line at *"is this text, or is this code?"*:

- **Text** — the ObjectType cheat-sheets, the conventions, the Skills — rides the **plugin**
  and auto-updates. A gotcha curated today reaches you at your next session.
- **Code** — the `cl` commands, the MCP tools, the quality package — rides the **wheel**, and
  moves only when you upgrade it. A *new tool* still needs that.

---

## 2. What each train carries (exact)

### Train A — the plugin — **silently updated at launch**

- **The 20 ObjectType knowledge sheets** (`plugins/crossloom/skills/objects/knowledge/*.md`).
  A generated, byte-identical mirror of the wheel's sheets, shipped beside the dispatcher Skill
  and read as `${CLAUDE_SKILL_DIR}/knowledge/<type>.md`. **This is what lets a gotcha curated
  today reach you tomorrow with no wheel upgrade.** It is a *build artifact* — nobody
  hand-edits it; CI re-hashes every sheet against the shipped `.manifest.json` on every push.
- **The 3 Skills** — `objects` (the ObjectType dispatcher), `orient` (first contact),
  `connect` (first-run env setup).
- **`CONVENTIONS.md`** — injected into every session by a SessionStart hook.
- **`.mcp.json`** — the MCP server *registration* (`cl mcp serve`). This is **wiring, not
  capability**: it says how to launch the server, not what the server can do.
- **`compat.json`** — `min_cl_version`, the minimum wheel version this plugin release needs.
- **The hooks** — `emit_conventions.py`, `check_wheel_version.py`.

### Train B — the wheel — **NOT auto-updated**

- The **`cl` CLI** — every command (`cl read`, `cl write`, `cl howto`, `cl ping`, `cl env`,
  `cl quality`, …).
- The **MCP server code** — i.e. **every MCP tool the model can actually call**. The plugin
  only says *where to start the server*; the wheel **is** the server.
- The **20 knowledge sheets** — as the **authoring source**. The plugin's copies are a mirror
  of these; this is where a curated gotcha is written.
- The **playbook / onboarding / reference docs** (`cl://playbook/*`, `cl://reference/*`) —
  still wheel-only, not yet mirrored.
- The **quality package** and the telemetry instrumentation.

---

## 3. Turning plugin auto-update on

Put this in your settings (`~/.claude/settings.json`, or managed settings — see
[`AUTO-UPDATE.md`](./AUTO-UPDATE.md)):

```json
{
  "extraKnownMarketplaces": {
    "crossloom": {
      "source": { "source": "github", "repo": "hanuele/crossloom-marketplace" },
      "autoUpdate": true
    }
  },
  "enabledPlugins": { "crossloom@crossloom": true }
}
```

**`"autoUpdate": true` is not the default and `marketplace add` does not write it.** Without
it the plugin installs once and then never moves again — while continuing to report itself as
perfectly healthy. That silence is the failure mode; the flag is the fix.

> **Why `source: "github"` and not a `url`.** The `github` form makes Claude Code **git-clone**
> the repo, which is what lets the manifest's relative plugin source (`./plugins/crossloom`)
> resolve. The `url` form downloads **only `marketplace.json`** and nothing else, so the
> relative source can never resolve — it cannot work here, for any repo, ever.
>
> And `github` needs no SSH key: Claude Code probes whether SSH is configured, and on a machine
> without a key it clones over **plain HTTPS** — which, against a public repo, needs no
> credentials. (Set `CLAUDE_CODE_PLUGIN_PREFER_HTTPS=1` to force that branch.)

From then on, at every launch, **without you doing anything**, you get: new or corrected
**knowledge sheets**, new or reworded **Skills**, an updated **`CONVENTIONS.md`**, updated
**hooks** and **MCP registration**, and a raised **`min_cl_version`** floor (with the nudge in
§4).

What you still **do not** get from plugin auto-update — because it never touches the wheel:

- **A new MCP tool.** A Skill may now tell the model to call a tool your wheel does not have;
  the call fails. The Skill was updated, the server behind it was not. This is what §4 guards.
- **A new `cl` command**, a bug-fix in an existing one, or new playbook/reference content.

---

## 4. The skew guard — why a session sometimes nags you

Because the two trains move independently, an auto-updated Skill can point at a capability
your wheel lacks. Each plugin release declares the floor it needs in **`compat.json`**
(`min_cl_version`), and a SessionStart hook compares it to your installed `cl --version`:

| Your wheel | What you see at session start |
|---|---|
| **≥ floor** | *nothing* — zero added output |
| **< floor** | one line naming the floor and how to upgrade |
| **`cl` missing** | one line pointing at the install docs (also the silent-dead-MCP-server signal) |

**That nudge is the design admitting the gap.** It is not a bug — it is the honest mitigation
for two trains with no coupling.

### 4b. The staleness check — the other watcher

The skew guard compares your wheel to a **floor**, and the floor only rises when a maintainer
raises it. So a release that ships a corrected sheet or a bugfix — anything needing no *new*
capability — leaves the floor untouched, the hook silent, and you on a stale wheel **looking
perfectly compliant.**

Two watchers, two failure modes. You need both:

| Watcher | Compares against | Catches | Reaches |
|---|---|---|---|
| SessionStart hook (§4) | the **floor** (`compat.json`) | **capability skew** — a Skill routes to a tool you lack | plugin users only |
| **MCP staleness check** (in the wheel) | the **latest** published version | **staleness** — your code is just old | anyone using the MCP server, **plugin or not** |

The second lives in the wheel's MCP server, so it also reaches devs who registered the server
**without** the plugin — whom the hook can never reach.

- **The check is automatic; the upgrade stays human.** The MCP server will never run
  `pip install` — reinstalling the wheel would disrupt the very server process the agent is
  talking to.
- **It never delays a tool call** — it runs on a background thread.
- **Quiet about what you cannot act on, loud about what you can.** Offline, git missing, a
  timeout → nothing is shown. But a **credential refusal** stays broken until a human fixes it,
  so the check **says so** — a lapsed token would otherwise starve you in perfect silence.
  **An unknown is never reported as "up to date".**
- **Opt out:** `CROSSLOOM_MCP_UPDATE_CHECK_OFF=1`.

---

## 5. How to update — both trains

### Train A — the plugin

```
# Auto-update ON  -> nothing to do; it arrives at next launch.
#                    Restart Claude Code, then /reload-plugins to activate it.
# Auto-update OFF -> /plugin marketplace update crossloom
#                    /reload-plugins
```

`/plugin marketplace update crossloom` also **repairs** a marketplace clone that can no longer
be fetched (you will see `Found stale directory, cleaning up and re-cloning…`). If your plugin
seems frozen at an old version, run it.

### Train B — the wheel

> ### ⚠ Do not run `cl update` on Windows — it will destroy your installation
>
> `cl update` **is** `cl.exe`. It asks pip to overwrite the very executable that is running,
> and Windows will not allow that — so pip uninstalls the old version, fails to install the
> new one, and leaves you with **no `cl` at all** *and no way to retry, because the command you
> would retry with is the one that just deleted itself.* Reproduced; a fix is in progress.
>
> **If a session-start message tells you to run `cl update`, ignore it for now.**

Upgrade from a **normal terminal** instead — not from inside `cl`:

```bash
python -m pip install --upgrade "crossloom-cli[ai] @ git+https://github.com/hanuele/crossloom-cli.git@v0.5.3"
```

The **`[ai]` extra is not optional** — it pulls `mcp` and `fastmcp`, which the MCP server
imports at startup. Without it you get a working CLI and a silently dead server.

This step **will** ask for GitHub credentials — the wheel repo is private. That is the only
step that should.

**Already bricked** (ran `cl update` before reading this)? The same command repairs it. If you
also see a `~rossloom_cli-*.dist-info` folder in `site-packages`, delete it — it is debris from
the torn uninstall.

---

## 6. How to check what you are actually on

```bash
cl --version                       # your wheel version  (Train B)
```
```
/plugin                            # Installed tab -> crossloom @ <version>  (Train A)
```

If a Skill or tool behaves as if a fix never landed, **check both numbers before reporting a
bug.** A mismatched pair is by far the most common cause, and it looks exactly like a broken
feature.

---

## 7. The seam this closed

Until plugin 0.3.0, curated ObjectType knowledge rode the train that does *not* auto-update: a
gotcha learned today landed in the wheel's `knowledge/<Type>.md` and reached a developer only
when they next upgraded the wheel — which, being manual, might be never. The plugin shipped a
*routing table* pointing back at text it did not carry, and auto-updated it faithfully.

That was a seam between two individually-sound choices — single-source the knowledge in the
wheel; auto-update the plugin — which **neither choice owned**. The sheets are now vendored
into the plugin as a generated mirror. The wheel is still the only place anyone *edits* them;
the mirror is a build artifact, guarded from both sides:

- **crossloom-cli's CI** opens the mirror PR automatically whenever a sheet changes on `main`,
  and its test suite fails if the mirror ever diverges from the authored sheets;
- **this repo's CI** (`scripts/verify_knowledge_mirror.py`) re-hashes every shipped sheet
  against the `.manifest.json` beside it and fails on any hand-edit, missing sheet, or sheet
  the dispatcher does not route to.

A curated gotcha now reaches a developer's **next session**, with no wheel upgrade.
