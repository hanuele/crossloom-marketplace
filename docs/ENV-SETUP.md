# First-Run Environment Setup — connecting to a CrossLoom instance

> Companion reference to the `crossloom:connect` skill (which auto-surfaces in-session when
> you can't connect). This is the human-readable runbook: prerequisites, the exact commands,
> how credentials are stored, the headless/CI path, and the full troubleshooting tree.

## Why this step exists

A freshly-installed `crossloom` plugin gives you two surfaces — the **`cl` CLI** and the
**MCP server** — but neither can talk to a CrossLoom instance until you register an
**environment**: a `system:stage` pointing at a URL, with a username and a password in your
OS keyring. There is no separate MCP login: the MCP server **reuses the CLI's credential
chain** (`environments.yaml` + the OS keyring), so configuring `cl env` once authenticates
both. Until then, `cl ping` and every MCP tool fail.

## Prerequisites

- The `crossloom-cli` wheel installed (`cl --version` works). See the marketplace README for
  the Python/wheel prerequisite; for the MCP server you need the `[ai]` extra
  (`pip install "crossloom-cli[ai] @ git+…"`).
- The plugin installed (`/plugin install crossloom@crossloom`).
- Access details for a CrossLoom instance: the **base URL** (e.g.
  `<your-instance-url>`), your **username**, and your **password** (your admin
  grants these).

## The three commands

### 1. Register the environment

```bash
cl env add <system> <stage> --url https://<host>/<instance> --user <you>
```

- `<system>` and `<stage>` are your labels (e.g. `claude dev`, `acme prod`). Together they
  form the env key `<system>:<stage>`.
- `--url` and `--user` are flags. **The password is deliberately NOT a flag** — a flag would
  be captured in your shell history and visible in the process list. You'll be prompted for
  it at a **hidden prompt** (`Password: ` — input not echoed), and it goes straight into your
  OS keyring.
- `--no-verify-ssl` — add only if the host uses an internal CA that your machine doesn't
  trust. Never use it against a public host.

### 2. Activate it

```bash
cl env use <system>:<stage>     # e.g. cl env use claude:dev
```

The active environment is **machine-global** (stored in `state.yaml`) — one active env per
machine at a time, shared across all your shells/sessions on that machine. Switch any time
with `cl env use <other>`; `cl env list` shows all and marks the active one.

> **Advanced — project-specific env (per-workspace, opt-in) (#147).** An experienced dev can
> point one shell or workspace at a *different* instance **without** changing the machine-global
> default above:
>
> - **`CROSSLOOM_ENV=<system>:<stage>`** — set it in a shell (or a workspace's MCP launch env)
>   and every `cl` command in that shell resolves that env; `cl env show`/`list` show it and
>   label the source. `state.yaml` is left untouched.
> - **`cl --env <system>:<stage> <command>`** — a one-shot override for a single operational
>   command (`ping`, `read`, …); highest precedence.
> - **MCP server:** it resolves `CROSSLOOM_ENV` from *its own process environment*, so set it in
>   the workspace's MCP launch env (e.g. an `env` block in the project's `.mcp.json`) to give that
>   workspace's server a default; a per-tool-call `env_hint` always overrides. (Whether a given
>   client auto-inherits the launching shell's env into a plugin-spawned server is client-specific
>   — set it explicitly in the launch config to be sure.)
>
> Precedence: **`--env` flag > `CROSSLOOM_ENV` > global `state.yaml`**. Unset = the global
> default, unchanged. So two workspaces can target two instances at once (e.g. one on a dev
> instance, one on a customer instance) by each setting its own `CROSSLOOM_ENV`. The override
> selects an env only — it never touches the keyring.

### 3. Confirm — connected, and to the *right* instance

The closing check is **two** commands read together — because `cl ping` proves the connection
works but NOT *which* instance you're on, and the active env is machine-global:

```bash
cl env show     # WHICH instance + user
cl ping         # WHETHER it connects
```

`cl ping` prints `Connected` + indented status lines on **stdout**; the
`[<system>:<stage>] … (<user>)` env badge prints to **stderr** (the terminal merges them, but the
split matters for scripts). So read *which instance* you're on from `cl env show`'s `Environment:`
line — not from a stdout capture of `cl ping`:
```
[<system>:<stage>] https://<host>/<instance> (<user>)    ← env badge (stderr)
Connected                                                 ← stdout
  status: ok
  method: data-api
  http_status: 200
```

A green `Connected` (exit 0) means both `cl` and the MCP tools can authenticate. Pair it with
`cl env show` showing `Environment: claude:dev` and you have a clean first-connect:
**✓ Connected to your-dev-instance as your user, on the shared dev instance.**

> **⚠ Customer-env guard (canonical — other surfaces cite this block).** Look at the
> **`Environment:`** line from `cl env show`: it MUST be **your onboarding env**. If it is
> anything else, **STOP** — because the active env is machine-global, `cl ping` would report
> `Connected` against the *wrong* instance with no error. Fix: `cl env use <your-env>`, then
> re-run `cl ping` — that sets the machine-global default (the right move for first-connect).
> (One shell on a different env without moving the default → the Advanced note above. For write or
> destructive probes later, the team convention is to pass `--env <your-env>` per-command rather
> than trust the ambient env — see `CONVENTIONS.md`.)

## Worked example (shared dev instance)

```bash
cl env add claude dev --url <your-instance-url> --user yourname
#   Password: ··········          (hidden; → OS keyring)
cl env use claude:dev
cl ping
#   [claude:dev] <your-instance-url> (yourname)
#   Connected
#     status: ok
#     method: data-api
#     http_status: 200
```

## How credentials are stored (and why it's safe)

| What | Where | Notes |
|---|---|---|
| Password (secret) | **OS keyring** — service `crossloom`, key `<system>:<stage>` | Windows Credential Manager / macOS Keychain / Linux Secret Service. Never on disk in plaintext. |
| URL, user, non-secret fields | `environments.yaml` in the CLI config dir | Owner-ACL'd; not in git. |
| Active env + active app | `state.yaml` in the CLI config dir | Machine-global selection. |

**Never** paste your password into a chat/agent session, a command flag, or a tracked file.
The hidden prompt and `CROSSLOOM_PASSWORD` (below) are the only intended paths.

### Headless / CI / scripted

When you can't use an interactive prompt, set the password in the environment before
`cl env add`:

```bash
export CROSSLOOM_PASSWORD='…'      # in your shell/CI secret store — NOT a tracked file
cl env add <system> <stage> --url … --user …   # picks up CROSSLOOM_PASSWORD, no prompt
```

### Migrating an old plaintext config

If you have a legacy `environments.yaml` with a plaintext password, move it into the keyring:

```bash
cl env migrate            # backs up the yaml, stores secrets in the keyring, strips plaintext
```

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| `No active environment. Run: cl env use <system:stage>` | Step 2 skipped | `cl env use <system>:<stage>` |
| `No environments configured` | Step 1 didn't persist | re-run `cl env add …`; check `cl env list` |
| `cl ping` → 401 / auth failure | wrong password / user | re-run `cl env add …` (re-enter password); verify `cl env show`. **If `CROSSLOOM_PASSWORD` is set, `unset` it first** — `cl env add` reads it before the prompt, so a stale value is silently reused. |
| `cl ping` → connection/DNS error | wrong URL | check `cl env show`; fix with `cl env add …` (same key overwrites) |
| TLS / certificate error (internal host) | self-signed / internal CA | `cl env add … --no-verify-ssl` (internal only) |
| Not sure which env is active | — | `cl env show` (active) / `cl env list` (all) |
| `cl` hits an unexpected instance | a `CROSSLOOM_ENV` override is set in this shell (#147) | `cl env show` labels `Source: CROSSLOOM_ENV override`; `unset CROSSLOOM_ENV` to fall back to the global default |
| `cl env show` `Environment:` is not your onboarding env | a different env is the active machine-global env — `cl ping` would connect to the *wrong* instance with no error | `cl env use <your-env>`, then re-run `cl ping`. Never work the dev walkthrough against another instance (see §Customer-env guard). |

## Next step

Once `cl ping` is green, run `/orient` (or the `crossloom:orient` skill) for the on-ramp
into working with CrossLoom.

---
*Authored for L3-01 (#133), crossloom-external-onboarding. Command shapes + keyring service
verified against live `crossloom-cli` source 2026-06-29 (`commands/env.py`, `config.py`).*
