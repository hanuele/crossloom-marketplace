# CrossLoom Marketplace

A [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
that distributes the **CrossLoom developer toolkit** to 3TXpert developers working on
the CrossLoom integration platform via Claude Code.

The marketplace bundles, as **one installable plugin**:

- **MCP tools** — actions against a live CrossLoom instance (the `cl`/MCP surface).
- **Auto-firing skills** — CrossLoom knowledge (conventions, per-ObjectType cheat-sheets)
  that the agent surfaces *unprompted*, with no `@`-mention required.
- **The 20 ObjectType knowledge sheets**, shipped *inside* the plugin — so a corrected
  cheat-sheet reaches you at your next session with nothing to run.
- **A SessionStart conventions hook** — injects the always-on CrossLoom conventions
  (mental model, environment, `cl`-first discipline) into every session.

> **Status:** plugin **v0.4.0**. Needs the `crossloom-cli` wheel at **≥ 0.5.3** — but install
> **v0.6.1**: it is the first release whose `cl update` cannot brick a Windows install.
> (0.5.3 and 0.6.0 *claimed* to fix that. They only fixed it inside a virtualenv.)

## This repo is public. The wheel repo is not.

**This marketplace is a public repo**, so Claude Code fetches it with **no credentials at
all** — no SSH key, no token, no login. That is deliberate: the marketplace auto-updates
silently in the background, and a channel that needs credentials is a channel that
silently stops working for whoever lacks them.

**`hanuele/crossloom-cli` (the wheel) is still private**, and installing it *does* need
your GitHub credentials. So exactly one step in this README will ask you to log in: the
`pip install`. If any *other* step asks for credentials, something is wrong — say so.

Nothing sensitive lives here: no hostnames, no customer names, no credentials. Keep it
that way. Before you push anything to this repo, ask whether you would be comfortable with
a stranger reading it, because they can.

## Prerequisite — Python + the `cl` wheel

The bundled MCP server is a **stdio Python process**: the plugin ships its *configuration*,
**not the runtime**. Two things must be on the machine before the plugin can do anything:

1. **Python ≥ 3.11** (pinned by `crossloom-cli`'s `pyproject.toml`).
2. **The `cl` wheel — installed with the `[ai]` extra:**

   ```
   python -m pip install --upgrade "crossloom-cli[ai] @ git+https://github.com/hanuele/crossloom-cli.git@v0.6.1"
   ```

   **The `[ai]` extra is required** — it pulls the MCP SDK (`mcp`, `fastmcp`) that the
   server imports at startup. A plain `crossloom-cli` install gives you a working CLI and a
   **silently dead MCP server** (it exits on the missing import).

   This is the step that rides your GitHub credentials. If `pip` fails with
   `could not read Username`, a 403, or `Repository not found`, you either have no stored
   credential or no read grant on the wheel repo — ask your onboarder. There is no public
   wheel channel.

> **⚠ If your wheel is older than 0.6.1, do not run `cl update` on Windows — use the pip
> command above to get to 0.6.1 first.**
>
> In wheels **before 0.6.1**, `cl update` bricked the install on Windows: `cl update` *is*
> `cl.exe`, and Windows will not let a running executable be overwritten — so pip uninstalled
> the old wheel, failed to install the new one, and left you with **no `cl` and no way to
> retry**. **Fixed in 0.6.1** (`cl` now exits first and hands off to a worker that waits for
> the lock to clear). But the fix only helps you *once you are on it* — and the only way to
> get there from an older wheel is the pip command above.
>
> **Why 0.6.1 and not 0.5.3, which announced this same fix?** Because 0.5.3's guard looked
> for `cl.exe` next to `python.exe` — true in a virtualenv, false on a normal Windows Python,
> where the scripts live one directory down. It found nothing, reported *nothing is locked*,
> and ran pip anyway. It bricked a real machine that way, on the build that was supposed to
> protect it. 0.6.1 asks pip's own record of installed files instead of guessing, and
> **refuses** rather than proceed when it cannot tell.
>
> **Already bricked?** The same pip command repairs it. If you also see a
> `~rossloom_cli-*.dist-info` folder in `site-packages`, delete it — it is debris from the
> torn uninstall.

### Check it in three lines — *before* you install the plugin

```
cl --version                      # the wheel's console entry point is on PATH (want >= 0.6.1)
python -c "import crossloom_cli"  # the package is importable
python -c "import mcp, fastmcp"   # the [ai] extra is present — the MCP SDK the server needs
```

All three should succeed. The second and third print **nothing** and exit 0 on success — no
output *is* the pass; an `ImportError` traceback is the failure. The third is the one that
catches the most common silent failure: `crossloom-cli` installed **without `[ai]`**, so the
CLI works while the MCP server is dead.

> **Why the plugin no longer names an interpreter.** `.mcp.json` spawns **`cl mcp serve`**,
> not `python -m …`. `cl` is a pip-baked console script, so it always runs the Python that
> actually has the wheel — which is correct by construction, on every platform and on
> machines with several Pythons. (Naming `python` broke macOS entirely, where no such
> binary exists; naming `python3` breaks Windows, where it resolves to a 0-byte Store stub.
> There is no interpreter name that is right on both, so the plugin names none.)

## Install — three steps

In any Claude Code session:

```
/plugin marketplace add hanuele/crossloom-marketplace
/plugin install crossloom@crossloom
/reload-plugins
```

**Both of these are success**, and which one you get depends only on whether *you* happen to
have a GitHub SSH key:

```
SSH not configured, cloning via HTTPS: https://github.com/...   ← no key (most developers)
Cloning via SSH: git@github.com:...                             ← you have a key
```

Claude Code probes whether SSH authenticates and picks accordingly — and falls back to the
other transport if the first fails. The repo is public, so **neither path asks you for
credentials.** A credential *prompt* is the thing to report; the transport name is not.

Then **restart Claude Code and run `/reload-plugins`** — a restart alone has proven not to be
enough.

Already have it installed, from before this repo went public?

```
/plugin marketplace update crossloom
```

You will see `Found stale directory, cleaning up and re-cloning…`. That is expected: the
repo was republished, so an old clone cannot be fast-forwarded and Claude Code replaces it.

## Turn auto-update on — it is not on by default

Add `"autoUpdate": true` to your Claude Code settings (`~/.claude/settings.json`):

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

**Adding the marketplace does not set this**, and third-party marketplaces do not
auto-update without it. Omit it and the plugin installs once, freezes forever, and goes on
reporting itself as perfectly healthy.

## Updating — the two trains

CrossLoom reaches you over **two independent trains**:

| | ships | updated by |
|---|---|---|
| **Plugin** (`crossloom@crossloom`) | the Skills, **the 20 ObjectType knowledge sheets**, `CONVENTIONS.md`, hooks, MCP *wiring* | **automatic** at launch (with `autoUpdate`) |
| **Wheel** (`crossloom-cli`) | the `cl` CLI, the MCP **tools** — the runtime | **manual** — only when a new floor is announced |

**The knowledge sheets moved from the wheel to the plugin.** That is the point of the
0.4.0 release: they used to ride the train that only moves when a human remembers to move
it, so a gotcha we learned on a Tuesday could sit undelivered for months. Now it is in your
next session.

**→ [`docs/UPDATING.md`](docs/UPDATING.md)** — what each train carries and how to check
which versions you are on. **→ [`docs/AUTO-UPDATE.md`](docs/AUTO-UPDATE.md)** — the owner's
release flow.

## Versioning & pinning

Each plugin entry in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
carries a `version`. **Auto-update fires only when that string is bumped**, and Claude Code
reads it from the **marketplace entry** — so `plugin.json` and `marketplace.json` must agree
or a release silently never ships. CI enforces that they agree.

## The knowledge sheets are a build artifact — do not edit them here

`plugins/crossloom/skills/objects/knowledge/` is a **generated mirror** of
`src/crossloom_cli/knowledge/` in the wheel repo. Edit a sheet **there**; a bot opens the
mirror PR here automatically. A hand-edit here would work right up until the next sync
silently reverted it — and in the meantime the plugin and the wheel would teach two
different things. CI re-hashes every sheet against the shipped `.manifest.json` and fails on
any local modification.

## Layout

```
crossloom-marketplace/
  .claude-plugin/
    marketplace.json     # marketplace manifest (name, owner, plugins[])
  plugins/
    crossloom/           # the one plugin (MCP + Skills + sheets + conventions hook)
  scripts/
    verify_knowledge_mirror.py
  docs/
  README.md
```

## Portability

The manifest uses **relative** plugin sources (`./plugins/crossloom`), which resolve only
when the marketplace is added **as a git repo** — not via a raw URL to `marketplace.json`,
which downloads that one file and nothing else. Moving to a 3TXpert org later is a remote
change, not a rebuild — keep the repo name and internal structure stable.

---

*Part of the CrossLoom External-Dev Onboarding plan (one-plugin distribution).*
