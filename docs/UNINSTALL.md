# Uninstall / Reset — returning a machine to a clean state

> Companion to [`ENV-SETUP.md`](ENV-SETUP.md) (the install runbook). This is the **inverse**:
> it removes the registered environment (including its keyring password), the plugin, and the
> marketplace registration — leaving the machine **genuinely fresh**, the state a first-time
> dev starts from. Use it to **repeat the install test** on a machine that has already been
> set up (so the `crossloom:connect` first-run walkthrough can be re-walked end to end), or to
> cleanly remove CrossLoom.

## Why a dedicated reset step exists

`cl env remove` deletes an environment from `environments.yaml` — but it does **NOT** purge the
password from your OS keyring. So a plain `remove` leaves an **orphaned credential** behind, and
the machine is not truly fresh: a re-run of the first-connect walkthrough would find a lingering
keyring entry. **`cl env reset`** closes that gap — it removes the environments, clears the active
selection, **and** purges each removed environment's keyring password in one step.

## The reset, layered (most-targeted first)

Run only as far down as you need. Step 1 alone is enough to re-walk the *first-connect* path
(plugin stays installed, environment gone); add Steps 2–4 to repeat the *whole* install.

### 1. Reset the environment (removes config + keyring password)

```bash
cl env reset            # all environments — asks for confirmation first
```

- Scope to one system on a mixed machine — leaves the others (and their credentials) untouched:
  ```bash
  cl env reset --system claude     # resets only claude:* ; a customer env (e.g. acme:*) is kept
  ```
- Skip the prompt for scripting / CI: add `--yes`.

`cl env reset` removes the matching entries from `environments.yaml`, clears the active env in
`state.yaml` if it pointed at a removed one, and purges each removed env's password from the OS
keyring (service `crossloom`). Confirm it's clean:

```bash
cl env list     # → "No environments configured"  (or only the systems you kept)
cl ping         # → "No active environment" / "No environments configured"
```

> **Customer-env safety.** `cl env reset` purges only the keyring entries for the environments it
> removes — never a blind, service-wide wipe. On a mixed machine, use `--system <name>` so a
> customer environment's credentials are never touched. (Same `acme:*`-is-a-customer-env caution as
> the connect skill and `CONVENTIONS.md`.)

### 2. Remove the plugin

```bash
/plugin uninstall crossloom@crossloom
```

Removes the `crossloom` plugin (its Skills + the bundled MCP server) from this Claude Code install.

### 3. Remove the marketplace registration

```bash
/plugin marketplace remove hanuele/crossloom-marketplace
```

Unregisters the marketplace, so the plugin is no longer offered for (re)install or auto-update.
(If a managed-settings file declared the marketplace — see [`AUTO-UPDATE.md`](AUTO-UPDATE.md) — also
remove that declaration, or it will be re-registered on the next launch.)

> The exact `/plugin` subcommand names can be confirmed with `/plugin` (the in-session manager) if
> a future Claude Code version renames them; these are the inverses of the `add` / `install`
> commands in [`ENV-SETUP.md`](ENV-SETUP.md) and the README.

### 4. (Optional) Uninstall the CLI / MCP wheel

```bash
pip uninstall crossloom-cli
```

Only if you want the `cl` command and the MCP server gone entirely (not needed just to re-walk the
install). After this, `cl --version` will fail until re-installed.

## What each step reverses

| Step | Command | Reverses (from `ENV-SETUP.md` / README) |
|---|---|---|
| 1 | `cl env reset` | `cl env add` + `cl env use` — **and** the keyring password `cl env remove` leaves behind |
| 2 | `/plugin uninstall crossloom@crossloom` | `/plugin install crossloom@crossloom` |
| 3 | `/plugin marketplace remove hanuele/crossloom-marketplace` | `/plugin marketplace add https://github.com/hanuele/crossloom-marketplace.git` (explicit HTTPS `.git` URL — the `owner/repo` shorthand can resolve to an SSH clone and fail without a GitHub SSH key) |
| 4 | `pip uninstall crossloom-cli` | `pip install "crossloom-cli[ai] @ git+…"` |

## Credential safety

`cl env reset` never echoes a password — it deletes the keyring entry without reading it. As in
setup, **never** paste a password into a chat/agent session or a tracked file. After a reset, the
secret is gone from the keyring; re-running `cl env add` will prompt for it again (hidden).

## Re-install

To set the machine back up, follow [`ENV-SETUP.md`](ENV-SETUP.md) from the top (or just Step 1's
`cl env add` / `cl env use` if you only reset the environment).
