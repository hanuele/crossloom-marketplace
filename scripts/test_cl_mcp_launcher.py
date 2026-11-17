#!/usr/bin/env python3
"""Behaviour tests for plugins/crossloom/bin/cl-mcp, the macOS/Linux MCP launcher (#601299).

The launcher picks the first interpreter that can import crossloom_cli: python3, then
python, then the interpreter named by the shebang of the `cl` file on PATH (symlinks
followed). These tests run it against stub interpreters in temp dirs, with a PATH that
holds only the stubs and the few tools the launcher needs, so no real Python and no
network install is involved.

A stub interpreter is a small sh script. Asked `-c 'import crossloom_cli'` it exits 0 when
it "has the module" and 1 otherwise; asked anything else it prints `STUB <name> <args>` to
stdout, which is how a test sees which interpreter the launcher exec'd.

Run: python scripts/test_cl_mcp_launcher.py   (stdlib unittest; POSIX only)
"""
from __future__ import annotations

import os
import shutil
import stat
import subprocess
import tempfile
import unittest
from pathlib import Path

LAUNCHER = Path(__file__).resolve().parent.parent / "plugins" / "crossloom" / "bin" / "cl-mcp"
# The launcher needs only sh builtins plus readlink; keep everything else off PATH.
TOOLS = ("readlink",)


def _write_exec(path: Path, text: str) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")
    path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return path


def stub_interpreter(path: Path, *, has_module: bool) -> Path:
    name = path.name
    return _write_exec(path, f"""#!/bin/sh
if [ "$1" = "-c" ]; then
    case $2 in *crossloom_cli*) exit {0 if has_module else 1} ;; esac
    exit 1
fi
echo "STUB {name} $*"
""")


@unittest.skipIf(os.name != "posix", "the sh launcher runs on POSIX only")
class ClMcpLauncherTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="cl-mcp-test-"))
        self.addCleanup(shutil.rmtree, self.tmp, ignore_errors=True)
        self.bin = self.tmp / "bin"  # what PATH sees: stubs + tools
        self.bin.mkdir()
        for tool in TOOLS:
            real = shutil.which(tool)
            self.assertIsNotNone(real, f"{tool} not found on the test host")
            (self.bin / tool).symlink_to(real)

    def run_launcher(self, *args: str) -> subprocess.CompletedProcess:
        env = {"PATH": str(self.bin), "HOME": str(self.tmp)}
        return subprocess.run(["/bin/sh", str(LAUNCHER), *args], env=env, check=False,
                              capture_output=True, text=True, timeout=30)

    def venv_with_cl(self, *, has_module: bool, shebang: str | None = None) -> Path:
        """A fake venv whose bin/cl names its own python; `cl` on PATH is a RELATIVE
        symlink chain into it, the shape pipx / a hand-made venv link leave behind."""
        venv_py = stub_interpreter(self.tmp / "venv" / "bin" / "python", has_module=has_module)
        real_cl = _write_exec(self.tmp / "venv" / "bin" / "cl",
                              f"#!{shebang or venv_py}\nimport sys\n")
        hop = self.tmp / "links" / "cl"
        hop.parent.mkdir()
        hop.symlink_to(os.path.relpath(real_cl, hop.parent))
        (self.bin / "cl").symlink_to(os.path.relpath(hop, self.bin))
        return venv_py

    # (a) a system python that has the module wins, before the fallback is looked at
    def test_a_system_python3_with_module_wins(self) -> None:
        stub_interpreter(self.bin / "python3", has_module=True)
        self.venv_with_cl(has_module=True)
        r = self.run_launcher("--x", "y z")
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "STUB python3 -m crossloom_cli.mcp.server --x y z\n")
        self.assertEqual(r.stderr, "")

    def test_a_python_used_when_python3_lacks_module(self) -> None:
        stub_interpreter(self.bin / "python3", has_module=False)
        stub_interpreter(self.bin / "python", has_module=True)
        self.venv_with_cl(has_module=True)
        r = self.run_launcher()
        self.assertEqual(r.stdout, "STUB python -m crossloom_cli.mcp.server\n")

    # (b) no system module; the venv python behind a symlinked `cl` is used
    def test_b_falls_back_to_interpreter_behind_cl(self) -> None:
        stub_interpreter(self.bin / "python3", has_module=False)
        self.venv_with_cl(has_module=True)
        r = self.run_launcher("--flag")
        self.assertEqual(r.returncode, 0, r.stderr)
        # the stub's name is "python": the venv one, not a PATH stub (python is absent)
        self.assertEqual(r.stdout, "STUB python -m crossloom_cli.mcp.server --flag\n")
        self.assertEqual(r.stderr, "")

    def test_b_env_form_shebang_resolves_on_path(self) -> None:
        stub_interpreter(self.tmp / "envbin" / "py-cl", has_module=True)
        # put the env-named interpreter on PATH via a link in bin
        (self.bin / "py-cl").symlink_to(self.tmp / "envbin" / "py-cl")
        self.venv_with_cl(has_module=False, shebang="/usr/bin/env -S py-cl")
        r = self.run_launcher()
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertEqual(r.stdout, "STUB py-cl -m crossloom_cli.mcp.server\n")

    def test_b_crlf_shebang_is_tolerated(self) -> None:
        venv_py = stub_interpreter(self.tmp / "v2" / "python", has_module=True)
        cl = self.bin / "cl"
        cl.write_bytes(f"#!{venv_py}\r\nimport sys\r\n".encode())
        cl.chmod(0o755)
        r = self.run_launcher()
        self.assertEqual(r.stdout, "STUB python -m crossloom_cli.mcp.server\n")

    # (c) neither: exit 1 with the error, naming the third candidate it tried
    def test_c_neither_exits_1_naming_the_cl_interpreter(self) -> None:
        stub_interpreter(self.bin / "python3", has_module=False)
        venv_py = self.venv_with_cl(has_module=False)
        r = self.run_launcher()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "", "nothing may reach stdout (it belongs to JSON-RPC)")
        self.assertIn("cl-mcp: no interpreter can import crossloom_cli", r.stderr)
        self.assertIn(f"the interpreter behind cl: {venv_py}", r.stderr)
        self.assertNotIn("STUB", r.stderr)

    def test_c_no_cl_on_path(self) -> None:
        r = self.run_launcher()
        self.assertEqual(r.returncode, 1)
        self.assertEqual(r.stdout, "")
        self.assertIn("the interpreter behind cl: none found", r.stderr)

    def test_c_symlink_loop_is_not_taken(self) -> None:
        # `command -v` already skips a looping link, so this does NOT reach the
        # launcher's 40-hop bound (a mutant removing it survives); the bound is
        # defence in depth only.
        (self.bin / "cl").symlink_to("cl2")
        (self.bin / "cl2").symlink_to("cl")
        r = self.run_launcher()
        self.assertEqual(r.returncode, 1)
        self.assertIn("none found", r.stderr)


if __name__ == "__main__":
    unittest.main(verbosity=2)
