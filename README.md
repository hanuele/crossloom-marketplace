# CrossLoom Marketplace

A [Claude Code plugin marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
that distributes the **CrossLoom developer toolkit** to 3TXpert developers working on
the CrossLoom integration platform via Claude Code.

The marketplace bundles, as **one installable plugin**:

- **MCP tools** — actions against a live CrossLoom instance (the `cl`/MCP surface).
- **Auto-firing skills** — CrossLoom knowledge (conventions, per-ObjectType cheat-sheets)
  that the agent surfaces *unprompted*, with no `@`-mention required.
- **A SessionStart conventions hook** — injects the always-on CrossLoom conventions
  (mental model, environment, `cl`-first discipline) into every session.

> **Status:** shipping real content as **v0.2.2** — the CrossLoom MCP server, three auto-firing
> knowledge Skills (ObjectType cheat-sheets, first-contact orientation, and the `connect`
> first-run connection/env setup), and the SessionStart
> conventions hook are all live in the plugin. (Marketplace **auto-update** config is wired in
> **L2-02**; there are no invariant/quality hooks — the portable subset is empty, per L2-05.)

## Before you install — prerequisite (R0): GitHub access + git credentials

This marketplace repo AND the `crossloom-cli` wheel repo are **private**. Installing the
wheel, adding the marketplace, and every later `cl update` / marketplace refresh all ride
your git credentials. Before anything else:

1. **GitHub read access** to `hanuele/crossloom-cli` and `hanuele/crossloom-marketplace`
   — granted by your onboarder / repo admin (no self-service path).
2. **Working git credentials on your machine.** Verify + set up in one command, in an
   **interactive** terminal (Git Credential Manager can only prompt interactively):

   ```
   git ls-remote https://github.com/hanuele/crossloom-cli.git
   ```

   A list of refs = PASS. `fatal: could not read Username for 'https://github.com'` =
   no stored credential and no way to prompt — re-run in an interactive terminal so GCM
   can sign you in. `remote: Repository not found.` = signed in, but the read grant is
   missing (GitHub masks private repos you can't see) — ask your onboarder.

The full walked step (PAT fallback for headless setups included) is Step 0.5 of the
unified install runbook your onboarder works from.

## Before you install — prerequisite (R1): Python + the `cl` wheel

The bundled MCP server is a **stdio Python process**: the plugin ships its *configuration*
(`.mcp.json` runs `python -m crossloom_cli.mcp.server`), **not the runtime**. Two things must
already be on the machine before the plugin can do anything:

1. **Python >= 3.11** on `PATH` as `python` — the interpreter the MCP server runs under
   (pinned by `crossloom-cli`'s `pyproject.toml`: `requires-python = ">=3.11"`).
2. **The `cl` wheel — installed with the `[ai]` extra — into that same Python:**
   `pip install "crossloom-cli[ai] @ git+https://github.com/hanuele/crossloom-cli.git"`
   (or the distributed wheel). **The `[ai]` extra is required** — it pulls the MCP SDK
   (`mcp`, `fastmcp`) the server imports at startup; a plain `crossloom-cli` install gives you
   a working CLI but a **silently dead MCP server** (it exits on the missing import). The
   `git+` form rides your GitHub access + git credentials — if `pip` fails with
   `could not read Username`, a 403, or `Repository not found`, walk the
   [GitHub-access prerequisite (R0) above](#before-you-install--prerequisite-r0-github-access--git-credentials)
   before retrying; there is no public wheel channel (the repo is private by decision).

### Check it in one line — *before* you install the plugin

```
cl --version                      # proves the wheel's console entry point is on PATH
python -c "import crossloom_cli"  # proves the MCP's interpreter can import the package
python -c "import mcp, fastmcp"   # proves the [ai] extra is present — the MCP SDK the server needs
```

All three should succeed — note the second and third commands print **nothing** and exit 0 on
success (no output *is* the pass; an `ImportError` traceback is the failure). The checks matter
because the MCP server runs under **`python`** specifically: if `cl` was installed into a
*different* environment (a venv, pipx, a second Python), `cl --version` can pass while
`python -c "import crossloom_cli"` fails — and the MCP server is dead even though the CLI works.
The **third** check is the one that catches the most common silent failure: `crossloom-cli`
installed **without `[ai]`**, so `import crossloom_cli` passes but `import mcp, fastmcp` fails —
again a dead MCP server behind a working CLI.

### Failure symptom — what a missing prerequisite looks like

The plugin installs fine and the `crossloom` MCP server *appears* in your config, **but its
tools error or are absent** and the agent can't call any CrossLoom action. Under the hood
`python -m crossloom_cli.mcp.server` exited immediately — no `python` on `PATH`, Python below
3.11, or `crossloom_cli` not importable by that interpreter. If CrossLoom tools are silently
missing after install, re-run the two checks above; this prerequisite is the usual cause.
(On Windows, beware the Microsoft Store `python` shim — it can satisfy `python --version`
yet not run the server; the `import crossloom_cli` check above catches that case.)

The **SessionStart conventions hook also shells `python`** (`hooks/emit_conventions.py`), so an
unmet prerequisite *also* silently drops the always-on CrossLoom conventions — not just the MCP
tools. Both surfaces share the same Python requirement; the two checks above cover both.

> **Cache-copy note (R1):** the manifest invokes the server by **module**
> (`python -m crossloom_cli.mcp.server`), resolved from the installed package on `sys.path` —
> *not* by a relative (`../`) file path. So the reference stays valid when Claude Code copies
> the plugin into its cache; there is no relative path to break.

## For an external developer — install in three steps

In any Claude Code session:

```
/plugin marketplace add https://github.com/hanuele/crossloom-marketplace.git
/plugin install crossloom@crossloom
/reload-plugins
```

- **`/plugin marketplace add https://github.com/hanuele/crossloom-marketplace.git`** —
  registers this marketplace (Git-hosted; refresh later with `/plugin marketplace update`).
  **Use this explicit HTTPS `.git` URL, not the `owner/repo` shorthand** — the shorthand can
  resolve to an SSH clone and fail with `No ED25519 host key is known for github.com` on a
  machine without a GitHub SSH key. The HTTPS URL rides the same private-git credentials as
  the wheel install (see R0) — a failure here means the R0 prerequisite above isn't met. (The
  `.git` suffix matters: a `…/marketplace.json` URL would break the plugin's relative sources.)
- **`/plugin install crossloom@crossloom`** — installs the `crossloom` plugin from the
  `crossloom` marketplace.
- **`/reload-plugins`** — activates it in the current session.

> **Prerequisite:** these three commands assume **Python >= 3.11 and the `cl` wheel are
> already installed** — see [the prerequisite section above](#before-you-install--prerequisite-r1-python--the-cl-wheel) and run its one-line check first. Without it the MCP server installs but its tools are silently dead.

## Updating — the two trains

CrossLoom reaches you over **two independent trains**, and **plugin auto-update only moves one
of them**:

| | ships | updated by |
|---|---|---|
| **Wheel** (`crossloom-cli`) | the `cl` CLI, the MCP **tools**, the **ObjectType knowledge sheets** | **`cl update`** — you run it |
| **Plugin** (`crossloom@crossloom`) | the Skills, `CONVENTIONS.md`, hooks, MCP *wiring* | **automatic** at launch (if enabled) |

> **The plugin ships the map; the wheel ships the territory.** Turning on auto-update refreshes
> the map — it does **not** move the territory. A corrected cheat-sheet does **not** reach you
> until you run `cl update`; a session-start nudge tells you when you are behind the floor.

**→ Read [`docs/UPDATING.md`](docs/UPDATING.md)** for exactly what each train carries, what
auto-update does and does not deliver, and how to check which versions you are on.

## Versioning & pinning

Each plugin entry in [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)
carries a `version` field. Plugin sources additionally support Git `ref` (branch/tag) and
`sha` (exact commit) pinning. **The version controls the update flow:** Claude Code resolves a
plugin's version as `plugin.json` → marketplace entry → git SHA (first present wins), and
auto-update pulls a new version only when that string is **bumped** — so we keep the pin and
bump it for controlled releases. Silent auto-update is enabled per-machine via managed settings
(`extraKnownMarketplaces.<name>.autoUpdate: true`), **not** a `marketplace.json` field. Full
owner + dev flow: [`docs/AUTO-UPDATE.md`](docs/AUTO-UPDATE.md) (**plugin train only** — see
`docs/UPDATING.md` for both).

## Layout

```
crossloom-marketplace/
  .claude-plugin/
    marketplace.json     # marketplace manifest (name, owner, plugins[])
  plugins/
    crossloom/           # the one plugin (MCP + Skills + conventions hook; v0.2.2)
  README.md
```

## Portability

Hosted under `hanuele` to start. The manifest uses **relative** plugin sources
(`./plugins/crossloom`), which resolve only when the marketplace is added **via Git**
(not via a raw URL to `marketplace.json`). Moving to a 3TXpert org later is a remote
change (new origin), not a rebuild — keep the repo name and internal structure stable.

---

*Part of the [CrossLoom External-Dev Onboarding](https://github.com/hanuele) plan
(one-plugin distribution).*
