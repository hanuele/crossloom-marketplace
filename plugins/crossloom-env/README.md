# crossloom-env

Shows which CrossLoom environment your Claude Code session is pointed at, and asks before a write runs on an environment you have marked as protected.

The active environment is a machine-wide `cl env use` setting. Nothing in a session shows it, so a `run_sql` or a deploy can land on the wrong instance without anyone noticing. This plugin puts the answer under the prompt.

## What it does

- Reads `cl env show` three seconds after the session starts and once a minute after that, and pins `CrossLoom <system:stage>` under the prompt. On a protected environment the line reads `· PROTECTED`.
- Toasts when the environment changes while the session runs.
- Before a crossloom MCP write verb (`run_sql`, `deploy_*`, `patch_*`, `create_*`, `delete_*`, `revert_*`, property updates, package apply, bootstrap rollout, translations, SmartUI, scheduler triggers, knowledge writes, changesets, cleanup) runs on a protected environment, asks once: Cancel denies the call, Continue lets it through. Read verbs never ask.
- `/cl-env` prints the environment, its URL and whether it is protected.

If the question cannot be asked (a `claude -p` run, a dismissed dialog) the call goes on. This is a confirmation for a person at the prompt, not a security gate.

## Install

```
/plugin install crossloom-env --marketplace hanuele/crossloom-marketplace
```

Needs the `cl` CLI on PATH (the crossloom-cli wheel) and a Claude Code build that loads plugin hooks modules (2.1.291 or later; earlier builds ignore the plugin).

## Configure

In `/config`, under the plugin, set **Protected environments** to a comma-separated list of `system:stage` names, for example `mwm:dev,wiam-3T:prod`. Empty (the default) never asks; the status line still shows the environment.

The same value lives in `~/.claude/settings.json`:

```json
"pluginConfigs": { "crossloom-env@crossloom": { "options": { "protectedEnvs": "mwm:dev" } } }
```

## Develop

```
claude plugin validate plugins/crossloom-env
claude plugin test plugins/crossloom-env
```

The tests run against the engine with a mocked `cl env show` and a mocked dialog; they need no CrossLoom instance.
