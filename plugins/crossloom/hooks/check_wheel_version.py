#!/usr/bin/env python3
"""SessionStart hook — nudge when the installed crossloom-cli wheel is older than
the floor this plugin release needs (#180).

The plugin (Skills + MCP wiring + conventions) auto-updates SILENTLY at launch;
the crossloom-cli wheel (the `cl` CLI, the MCP server code, the knowledge payload)
updates only when the dev runs `cl update`. Nothing links the two versions, so a
silently-updated Skill can route to a `cl`/MCP capability the dev's wheel lacks.
This hook closes that skew: it reads the machine-readable floor from the sibling
`compat.json` and compares it to the installed `cl --version`.

Three states:
  - wheel >= floor            -> emit NOTHING (zero added session output)
  - wheel <  floor            -> ONE line: installed vs required + `cl update`
  - `cl` missing / unreadable -> ONE line pointing at the install docs (also the
                                 silent-dead-MCP-server signal, surfaced at start)

SELF-CONTAINED BY DESIGN: it MUST NOT import crossloom_cli — the wheel it checks
may be the very thing that is absent. It shells `cl --version` via a PATH-resolved
path (`shutil.which`, so a PATH miss is a clean None) with a hard timeout, and
parses the version string inline.

Typed-channel discipline (like emit_conventions.py): stdout carries ONLY the JSON
envelope, and on ANY error we emit nothing — a session must never break because
the version check failed.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

_TIMEOUT_S = 5
_INSTALL_HINT = "see the crossloom-marketplace README (Installation)"
_CACHE = Path(tempfile.gettempdir()) / "crossloom_cl_version_cache.json"

# CrossLoom-context gate (#1000113): the wheel nag is emitted ONLY in a
# CrossLoom project context, so cross-project sessions get no nag (and don't pay
# the `cl --version` subprocess). Same rule as emit_conventions.py — kept inline
# (not a shared import) so this hook stays self-contained and can never break a
# session on a missing sibling module.
# Project-root markers. NOT `.crossloom` — that is the user-global `cl` config
# dir (`~/.crossloom`), which an ancestor walk would hit for EVERY home-descended
# session, opening the gate globally (#1000113 falsifier caught exactly this).
_MARKERS = (".crossloom-session.json", "cl.toml")


def _session_cwd() -> str:
    """The session cwd from the SessionStart hook payload (stdin JSON), falling
    back to os.getcwd(). Never raises; never blocks on a missing stdin."""
    try:
        if not sys.stdin.isatty():
            raw = sys.stdin.read()
            if raw.strip():
                data = json.loads(raw)
                cwd = data.get("cwd") if isinstance(data, dict) else None
                if isinstance(cwd, str) and cwd.strip():
                    return cwd
    except Exception:
        pass
    try:
        return os.getcwd()
    except Exception:
        return ""


def _is_crossloom_context() -> bool:
    """True when this session is a CrossLoom project context (see gate above)."""
    cwd = _session_cwd()
    if not cwd:
        return False
    if "crossloom" in cwd.lower():
        return True
    try:
        p = Path(cwd).resolve()
        home = Path.home().resolve()
    except Exception:
        return False
    # Exclude the home dir + everything at/above it, and filesystem roots: a
    # user-global marker there must NOT open the gate for every session.
    skip = {home, *home.parents}
    for d in (p, *p.parents):
        if d in skip or d.parent == d:
            continue
        for m in _MARKERS:
            try:
                if (d / m).exists():
                    return True
            except OSError:
                continue
    return False


def _floor() -> str | None:
    """The min wheel version from the sibling compat.json, or None if unreadable."""
    compat = Path(__file__).resolve().parent.parent / "compat.json"
    try:
        data = json.loads(compat.read_text(encoding="utf-8"))
    except Exception:
        return None
    version = data.get("min_cl_version") if isinstance(data, dict) else None
    return version if isinstance(version, str) and version.strip() else None


def _parse(version: str) -> tuple[int, int, int] | None:
    """(major, minor, patch) from a version string; leading ``v`` and any
    -pre / +build suffix dropped. None when not three numeric components."""
    core = version.strip().lstrip("v").split("+", 1)[0].split("-", 1)[0]
    parts = core.split(".")
    if len(parts) != 3:
        return None
    try:
        return (int(parts[0]), int(parts[1]), int(parts[2]))
    except ValueError:
        return None


def _read_cl_version(cl_path: str) -> str | None:
    """The semver from ``cl --version`` (click prints ``crossloom-cli, version
    X.Y.Z``), or None when the subprocess fails, times out, or has no version."""
    try:
        proc = subprocess.run(
            [cl_path, "--version"],
            capture_output=True,
            text=True,
            timeout=_TIMEOUT_S,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if proc.returncode != 0:
        return None
    # Version prints to stdout today; also scan stderr so a future `cl` that moved
    # --version there isn't misread as "broken" (returncode==0 already gates this,
    # so stderr is empty on the success path).
    match = re.search(r"version\s+(\S+)", proc.stdout + "\n" + proc.stderr)
    return match.group(1) if match else None


def _cl_version_cached(cl_path: str) -> str | None:
    """The installed cl version, cached by (cl_path, mtime) in a temp file so the
    ~700ms `cl --version` subprocess runs only when cl.exe actually changes (e.g.
    after `cl update`) — steady-state cost drops to a small file read. A stale
    wheel keeps failing the check because its mtime is unchanged, so caching never
    hides skew. Fail-open: ANY cache/stat error falls back to a live read, so the
    cache can never break a session or return a wrong answer on error."""
    try:
        mtime = os.path.getmtime(cl_path)
    except OSError:
        return _read_cl_version(cl_path)  # can't stat -> just read live
    try:
        data = json.loads(_CACHE.read_text(encoding="utf-8"))
        if (
            data.get("cl_path") == cl_path
            and data.get("cl_mtime") == mtime
            and isinstance(data.get("version"), str)
        ):
            return data["version"]  # fast path: unchanged cl.exe
    except Exception:
        pass  # miss / unreadable / malformed -> fall through to a live read
    version = _read_cl_version(cl_path)
    if version is not None:  # only cache a real read, never a transient failure
        try:
            _CACHE.write_text(
                json.dumps(
                    {"cl_path": cl_path, "cl_mtime": mtime, "version": version}
                ),
                encoding="utf-8",
            )
        except Exception:
            pass  # best-effort write; a cache miss next time is harmless
    return version


def _emit(context: str) -> None:
    """Emit ``context`` as the SessionStart additionalContext envelope (the only
    thing that may ever reach stdout)."""
    envelope = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(envelope))


def main() -> None:
    if not _is_crossloom_context():
        return  # off-project: no wheel nag, no `cl --version` subprocess (#1000113)
    floor = _floor()
    if floor is None:
        return  # no floor declared -> nothing to check; never nag
    floor_t = _parse(floor)
    if floor_t is None:
        return  # malformed floor -> stay silent rather than nag falsely

    cl_path = shutil.which("cl")
    if cl_path is None:
        _emit(
            "CrossLoom: `cl` was not found on PATH — the CrossLoom MCP server and "
            "CLI are unavailable this session (tools will be silently absent). "
            f"Install the crossloom-cli wheel: {_INSTALL_HINT}."
        )
        return

    installed = _cl_version_cached(cl_path)
    if installed is None:
        _emit(
            "CrossLoom: `cl` is on PATH but its version could not be read — the "
            "wheel may be broken or the MCP server dead. Reinstall: "
            f"{_INSTALL_HINT}."
        )
        return

    installed_t = _parse(installed)
    if installed_t is None:
        return  # present but unparseable version -> don't nag on an odd string
    if installed_t < floor_t:
        _emit(
            f"CrossLoom: your crossloom-cli wheel is {installed}, but this plugin "
            f"release needs >= {floor}. Some Skills or MCP tools may route to "
            f"capability your wheel lacks. Run `cl update` to upgrade."
        )
    # compliant (installed >= floor) -> emit nothing


if __name__ == "__main__":
    try:
        main()
    except Exception:
        # Fail-open BY CONSTRUCTION: SessionStart must stay silent even on an
        # unforeseen error (e.g. a locale-undecodable byte from the subprocess) —
        # this hook must never break or noise a dev's session start.
        pass
