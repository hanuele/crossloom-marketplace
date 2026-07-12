---
description: First-run connection setup for a CrossLoom instance — registers an environment (URL + user + keyring password) so `cl` and the MCP server can authenticate. Use when the user can't connect, sees auth/login/credential failures, "no active environment" / "no environments configured", `cl ping` fails, the MCP `crossloom` server shows failed/unauthenticated, or they just installed the plugin and need to point it at a CrossLoom instance.
last_verified: 2026-07-02
verified_against: "crossloom-cli live source read 2026-06-29 (binta, #133): src/crossloom_cli/commands/env.py (cl env add/use/show shapes; password NOT a flag) + src/crossloom_cli/config.py (KEYRING_SERVICE='crossloom', secret key f'{system}:{stage}', environments.yaml + state.yaml). Clean-profile cl-ping walk + no-leak grep at ticket close; full fresh-machine walk = L3 gate. First-connect verification + customer-env guard added 2026-06-30 (prasert, #135): cl ping / cl env show live-verified against claude:dev at cl 0.3.0 — cl ping env-badge confirmed on STDERR, Connected+status on STDOUT; stage+user read from cl env show Environment/User fields."
---

# Connect — first-run environment setup for CrossLoom

> **The day-one wall.** A freshly-installed plugin has the `cl` CLI + the MCP server, but
> **no environment registered** — no `environments.yaml`, no keyring password. So `cl ping`
> and every MCP tool fail to authenticate until you register one. This skill walks that
> one-time setup. (The MCP server has no login of its own — it **reuses the CLI's
> credential chain**, so configuring `cl env` once connects both surfaces.)

## The one-time setup (three commands)

```bash
# 1. Register the environment. URL + user are flags; the PASSWORD is NOT a flag
#    (a flag leaks into your shell history + the process list). You'll be asked
#    for it at a hidden prompt.
cl env add <system> <stage> --url https://<host>/<instance> --user <you>
#    Password: ··········   ← hidden prompt; stored in your OS keyring, not on disk

# 2. Make it the active environment (machine-global — one active env per machine).
cl env use <system>:<stage>

# 3. Confirm you're connected.
cl ping        # → a green "Connected" then indented status lines (see below)
```

A successful `cl ping` prints the env badge, then `Connected`, then indented `key: value` lines:
```
[<system>:<stage>] https://<host>/<instance> (<user>)    ← env badge — on STDERR
Connected                                                 ← on STDOUT
  status: ok
  method: data-api
  http_status: 200
```
(The terminal merges the two streams, but the split matters for scripts: the `Connected` +
status lines are **stdout**; the `[…] (<user>)` env badge is **stderr**. To read *which instance*
you're on, use `cl env show` — see *First-connect verification* below — not a stdout grep of `cl ping`.)

Example for the shared dev instance:
```bash
cl env add claude dev --url <your-instance-url> --user <you>
cl env use claude:dev
cl ping
```

> **Advanced — one workspace on a different instance (#147).** The active env above is
> machine-global. To point a single shell/workspace at another instance *without* changing that
> global default, set `CROSSLOOM_ENV=<system>:<stage>` in that shell (or `cl --env <system>:<stage>
> <command>` for one command); `cl env show` labels the source. Precedence: `--env` >
> `CROSSLOOM_ENV` > global default. Full detail: ENV-SETUP.md (https://github.com/hanuele/crossloom-marketplace/blob/main/docs/ENV-SETUP.md) → "Advanced: project-specific
> env".

## First-connect verification — connected, and to the *right* instance?

`cl ping` tells you the connection works — but **not which instance you're pointed at**. The
active env is **machine-global**, so if a non-onboarding env happens to be active,
`cl ping` will cheerfully report `Connected` against the *wrong* system, with no error. So the
closing check reads two commands together:

```bash
cl env show     # WHICH instance + user (the active, machine-global env)
cl ping         # WHETHER it connects
```

A clean first-connect to the shared dev instance:

```
$ cl env show
Environment: claude:dev
URL:         <your-instance-url>
User:        claude
$ cl ping
Connected
  status: ok
  method: data-api
  http_status: 200
```

Read that as a **pass**: ✓ *Connected to your-dev-instance as `claude`, active env `claude:dev`.*

> **⚠ Customer-env guard — the failure that hides itself.** Look at the **`Environment:`** line
> from `cl env show`: it MUST be **your onboarding env**. If it is anything else, **STOP** —
> because the active env is machine-global, you'd be working against the wrong instance with no
> error to warn you. Fix: `cl env use <your-env>`, then re-run `cl ping`. (That sets the
> machine-global default — the right move for first-connect. Need a *different* env in just one
> shell without moving the default? Use the Advanced note above — `CROSSLOOM_ENV` / `cl --env`.
> For write or destructive probes later, the team convention is to pass `--env <your-env>`
> per-command rather than trust the ambient env — see `CONVENTIONS.md`.) Canonical guard:
> ENV-SETUP.md §Customer-env guard (https://github.com/hanuele/crossloom-marketplace/blob/main/docs/ENV-SETUP.md).

**If `cl ping` does NOT print `Connected` (or exits non-zero)** — that's a **fail**. Map the
message to the fix, then see *When it still won't connect* below:

| What you see | Fix (setup step) |
|---|---|
| `No active environment` | `cl env use <system>:<stage>` (step 2 was skipped) |
| `No environments configured` | re-run `cl env add …` (step 1 didn't land); check `cl env list` |
| `401` / auth error | wrong password/user — re-run `cl env add …`; `unset CROSSLOOM_PASSWORD` first if it's set |
| connection / DNS / TLS error | wrong URL or internal-CA cert — check `cl env show` |

## Credential safety — non-negotiable

- **Never type or paste your password into this chat**, and never put it in a file or a
  command flag. The only safe paths are the **hidden prompt** above, or — for
  headless/CI — the `CROSSLOOM_PASSWORD` environment variable (set it in your shell, not
  in a tracked file).
- The password is stored in your **OS keyring** (Windows Credential Manager / macOS
  Keychain / Linux Secret Service) under service `crossloom`, key `<system>:<stage>` —
  never in `environments.yaml` (which holds only URL + user + non-secret fields and is
  owner-ACL'd, not in git).
- If you ever have an older config with a plaintext password in `environments.yaml`, move
  it into the keyring with `cl env migrate` (writes a backup, then strips the plaintext).

## When it still won't connect

- **`No active environment`** → you skipped step 2: run `cl env use <system>:<stage>`.
- **`No environments configured`** → step 1 didn't land: re-run `cl env add …` and check
  `cl env list`.
- **`cl ping` 401 / auth error** → wrong password (re-run `cl env add …` to re-enter it),
  wrong user, or wrong URL. Verify with `cl env show`. **If you set `CROSSLOOM_PASSWORD`
  earlier, `unset` it first** — `cl env add` reads that env var before the prompt, so a stale
  value is silently reused and the 401 won't clear.
- **TLS / certificate error against an internal host** → add `--no-verify-ssl` to
  `cl env add` (internal CA only; never for public hosts).
- **Which env am I on?** `cl env show` (active env + URL + user); `cl env list` (all).

## Full walkthrough

The step-by-step first-run runbook — prerequisites, the headless/CI path, and the full
troubleshooting tree — lives in the marketplace repo's ENV-SETUP.md (https://github.com/hanuele/crossloom-marketplace/blob/main/docs/ENV-SETUP.md). This skill is the
in-session guide; the runbook is the reference.

> **`cl env` is the proven mechanism** the dev cohort already use — this skill just makes it
> discoverable at the moment you're stuck. Once `cl ping` is green, run `/orient` (or the
> `crossloom:orient` skill) for the on-ramp into actually using CrossLoom.
