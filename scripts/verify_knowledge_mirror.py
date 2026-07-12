#!/usr/bin/env python3
"""Verify the vendored ObjectType knowledge mirror against its manifest (#285).

WHAT THIS GUARDS. ``plugins/crossloom/skills/objects/knowledge/`` is a BUILD
ARTIFACT: the 20 sheets are authored in the crossloom-cli wheel
(``src/crossloom_cli/knowledge/*.md``) and copied here by that repo's
``scripts/sync_plugin_knowledge.py`` so they ride this plugin's auto-update train.
The wheel does not auto-update; this plugin does. Vendoring them is what lets a
gotcha curated today reach a dev tomorrow without a manual ``cl update``.

The failure this exists to prevent is someone HAND-EDITING a sheet here. It would
work — until the next sync silently reverted it, and in the meantime the plugin
and the wheel would be teaching two different things. So the sheets are checked,
here, on every push.

WHY IT CHECKS A MANIFEST AND NOT THE WHEEL. crossloom-cli is a PRIVATE repo. This
repo's CI has no credentials for it and should not need any. The sync writes a
``.manifest.json`` beside the sheets carrying a sha256 per sheet; this script
re-hashes what is on disk and compares. That catches any local modification
WITHOUT a cross-repo clone. (The other half of the guard — "does the mirror still
match the WHEEL?" — lives in crossloom-cli's own test suite, which has both trees.
Together they close the loop from both sides.)

EOL. Hashes are computed over CRLF-normalized bytes, matching the sync, so a
Windows checkout does not false-RED on line endings while a real one-byte content
change still fails.

Stdlib only, no dependencies — CI runs it on a bare Python.

Usage::

    python scripts/verify_knowledge_mirror.py     # exit 0 clean, 1 on drift
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
KNOWLEDGE = REPO / "plugins" / "crossloom" / "skills" / "objects" / "knowledge"
SKILL = REPO / "plugins" / "crossloom" / "skills" / "objects" / "SKILL.md"
MANIFEST = KNOWLEDGE / ".manifest.json"


def _hash(path: Path) -> str:
    """sha256 over LF-normalized bytes (see EOL note in the module docstring)."""
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n")).hexdigest()


def main() -> int:
    problems: list[str] = []

    if not KNOWLEDGE.is_dir():
        print(f"FAIL: knowledge mirror missing entirely: {KNOWLEDGE}", file=sys.stderr)
        return 1
    if not MANIFEST.is_file():
        # A missing manifest is a FAILURE, not a skip: without it nothing here is
        # verifiable, and an unverifiable mirror is exactly the state this guards.
        print(f"FAIL: no {MANIFEST.name} beside the sheets — the mirror cannot be "
              "verified. Re-run crossloom-cli's scripts/sync_plugin_knowledge.py.",
              file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    declared: dict[str, str] = manifest["sheets"]
    on_disk = {p.name: p for p in sorted(KNOWLEDGE.glob("*.md"))}

    for name in sorted(set(declared) - set(on_disk)):
        problems.append(f"missing: {name} is in the manifest but not on disk")
    for name in sorted(set(on_disk) - set(declared)):
        problems.append(f"unmanifested: {name} is on disk but not in the manifest")
    for name in sorted(set(declared) & set(on_disk)):
        actual = _hash(on_disk[name])
        if actual != declared[name]:
            problems.append(
                f"modified: {name} does not match its manifest hash "
                f"(expected {declared[name][:12]}…, got {actual[:12]}…)"
            )

    # The routing table must address every shipped sheet. A sheet the dispatcher
    # never names is shipped-but-unreachable — the exact bug that let
    # ttx_SmartUI_History sit in the corpus unroutable until 2026-07-12.
    if SKILL.is_file():
        skill_md = SKILL.read_text(encoding="utf-8")
        for name in sorted(on_disk):
            if f"knowledge/{name}" not in skill_md:
                problems.append(
                    f"unrouted: {name} is shipped but SKILL.md never names it"
                )
    else:
        problems.append(f"missing: the dispatcher {SKILL.name} is absent")

    if problems:
        print("FAIL: the vendored knowledge mirror has drifted:", file=sys.stderr)
        for p in problems:
            print(f"  - {p}", file=sys.stderr)
        print(
            "\nThese sheets are a BUILD ARTIFACT — do not hand-edit them here.\n"
            "Edit src/crossloom_cli/knowledge/<sheet>.md in crossloom-cli, then run\n"
            "  python scripts/sync_plugin_knowledge.py\n"
            "in that repo and commit the regenerated mirror.",
            file=sys.stderr,
        )
        return 1

    print(f"OK: {len(on_disk)} knowledge sheet(s) match the manifest and are routed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
