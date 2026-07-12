#!/usr/bin/env python3
"""SessionStart hook — inject the CrossLoom always-on conventions.

The plugin cannot ship an auto-loading CLAUDE.md and cannot contribute
`.claude/rules/` (both are user/project-scoped, per the Claude Code docs). The
documented always-on surface for a plugin is a SessionStart hook that emits
`additionalContext`. This script reads the sibling CONVENTIONS.md (the reviewable
artifact) and emits it as that context.

Context gate (#1000113): the full CONVENTIONS.md block (~1.3k tokens of
CrossLoom-specific rules) is emitted ONLY in a CrossLoom project context — a
session whose cwd is inside a CrossLoom project. Every OTHER session (the common
cross-project case) pays no rent: it gets a single pointer line instead. The
gate rule is pre-decided: cwd (lowercased) contains `crossloom`, OR a CrossLoom
project marker (`.crossloom-session.json`, `cl.toml`, `.crossloom`) exists in the
cwd or an ancestor. The auto-firing crossloom Skills stay registered regardless
— this changes SessionStart context only, not skill availability.

Typed-channel discipline: stdout carries ONLY the JSON envelope. On any error we
emit nothing (a session must never break because the conventions could not load).
"""
import json
import os
import sys
from pathlib import Path

# Off-project pointer — one line, so a cross-project session knows the plugin is
# present and how to pull the full conventions on demand, without paying for them.
_POINTER = ('CrossLoom plugin present — say "crossloom" or run cl to load '
            'conventions (crossloom:orient).')

# Project-root markers. NOT `.crossloom` — that is the user-global `cl` config
# dir (`~/.crossloom`), which an ancestor walk would hit for EVERY home-descended
# session, opening the gate globally (#1000113 falsifier caught exactly this).
_MARKERS = (".crossloom-session.json", "cl.toml")


def _session_cwd() -> str:
    """The session cwd from the SessionStart hook payload (stdin JSON), falling
    back to os.getcwd(). Never raises; never blocks on a missing stdin (a hung
    SessionStart hook would stall session start)."""
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
    """True when this session is a CrossLoom project context (see module gate)."""
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


def _emit(context: str) -> None:
    envelope = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": context,
        }
    }
    sys.stdout.write(json.dumps(envelope))


def main() -> None:
    if not _is_crossloom_context():
        # Off-project: one-line pointer, not the full block.
        _emit(_POINTER)
        return
    conventions = Path(__file__).resolve().parent.parent / "CONVENTIONS.md"
    try:
        text = conventions.read_text(encoding="utf-8")
    except Exception:
        # any failure (missing/unreadable/decode) -> no context; never crash a session
        return
    if not text.strip():
        return
    _emit(text)


if __name__ == "__main__":
    main()
