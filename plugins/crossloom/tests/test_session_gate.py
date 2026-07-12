"""Tests for the CrossLoom SessionStart context gate (#1000113).

The two SessionStart hooks (emit_conventions.py, check_wheel_version.py) must
emit their full payload ONLY in a CrossLoom project context, and a one-line
pointer / nothing otherwise. Covers the falsifier AC plus the regression the
live falsifier caught: the user-global `~/.crossloom` config dir must NOT open
the gate for every home-descended session.

Run: pytest plugins/crossloom/tests/test_session_gate.py -v
"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

HOOKS = Path(__file__).resolve().parent.parent / "hooks"
EMIT = HOOKS / "emit_conventions.py"
WHEEL = HOOKS / "check_wheel_version.py"

OFF_CWD = "C:/Users/PeterLinder(3Txpert)"        # home — must be off-project
ON_CWD = "D:/VersionControl/crossloom"           # path-substring — on-project
POINTER_MARK = "CrossLoom plugin present"


def _run(hook: Path, cwd: str) -> str:
    """Drive a hook the way Claude Code does: SessionStart payload on stdin."""
    payload = json.dumps({"cwd": cwd, "hook_event_name": "SessionStart"})
    out = subprocess.run([sys.executable, str(hook)], input=payload,
                         capture_output=True, text=True, timeout=30)
    return out.stdout.strip()


def _context(out: str) -> str:
    if not out:
        return ""
    return json.loads(out)["hookSpecificOutput"]["additionalContext"]


# --- integration: the four falsifier cases -----------------------------------

def test_emit_off_project_is_pointer_only():
    ctx = _context(_run(EMIT, OFF_CWD))
    assert ctx.startswith(POINTER_MARK)
    assert "Always-On Conventions" not in ctx   # NOT the full block


def test_emit_on_project_is_full_block():
    ctx = _context(_run(EMIT, ON_CWD))
    assert "Always-On Conventions" in ctx
    assert len(ctx) > 1000


def test_wheel_off_project_is_silent():
    assert _run(WHEEL, OFF_CWD) == ""            # no nag, no output


def test_wheel_on_project_emits_something():
    # On-project the wheel check runs; it emits a nag OR a cl-missing line
    # depending on the installed wheel — either way, non-empty. (Off-project it
    # is unconditionally silent; that asymmetry IS the gate.)
    assert _run(WHEEL, ON_CWD) != ""


# --- unit: the gate predicate, incl. the home-global-marker regression --------

def _load(hook: Path):
    spec = importlib.util.spec_from_file_location(hook.stem, hook)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_substring_and_subdir_open_gate(monkeypatch):
    mod = _load(EMIT)
    for cwd in ("D:/VersionControl/crossloom", "D:/VersionControl/crossloom-cli/src",
                "c:/work/CrossLoom/x"):
        monkeypatch.setattr(mod, "_session_cwd", lambda c=cwd: c)
        assert mod._is_crossloom_context() is True, cwd


def test_plain_off_project_closes_gate(tmp_path, monkeypatch):
    mod = _load(EMIT)
    plain = tmp_path / "some-other-project"
    plain.mkdir()
    monkeypatch.setattr(mod, "_session_cwd", lambda: str(plain))
    assert mod._is_crossloom_context() is False


def test_project_marker_opens_gate(tmp_path, monkeypatch):
    mod = _load(EMIT)
    proj = tmp_path / "app"
    proj.mkdir()
    (proj / ".crossloom-session.json").write_text("{}", encoding="utf-8")
    monkeypatch.setattr(mod, "_session_cwd", lambda: str(proj))
    assert mod._is_crossloom_context() is True


def test_home_global_marker_does_not_open_gate(tmp_path, monkeypatch):
    """REGRESSION (#1000113 falsifier): a marker in the HOME dir must NOT open
    the gate for a home-descended session. This is the exact bug the live probe
    caught — ~/.crossloom (config dir) + ancestor-walk opened the gate globally.
    Here we put a REAL marker (.crossloom-session.json) in a fake home and a
    plain subdir cwd under it: the home-exclusion must keep the gate closed."""
    mod = _load(EMIT)
    fake_home = tmp_path / "home"
    fake_home.mkdir()
    (fake_home / ".crossloom-session.json").write_text("{}", encoding="utf-8")
    sub = fake_home / "notes"          # not a crossloom project
    sub.mkdir()
    monkeypatch.setattr(mod, "_session_cwd", lambda: str(sub))
    monkeypatch.setattr(mod.Path, "home", staticmethod(lambda: fake_home))
    assert mod._is_crossloom_context() is False


def test_config_dir_marker_is_not_used(tmp_path, monkeypatch):
    """`.crossloom` (the cl config DIR) is intentionally NOT a project marker.

    (Test name deliberately avoids the literal substring the gate keys on — else
    pytest's tmp_path, named after the test, would itself match the path rule.)"""
    mod = _load(EMIT)
    proj = tmp_path / "app"
    proj.mkdir()
    (proj / ".crossloom").mkdir()      # config dir, not a project signal
    monkeypatch.setattr(mod, "_session_cwd", lambda: str(proj))
    monkeypatch.setattr(mod.Path, "home", staticmethod(lambda: tmp_path / "elsewhere"))
    assert mod._is_crossloom_context() is False
