@echo off
REM cl-mcp.cmd -- Windows half of the crossloom MCP launcher (#900389, split in #900531).
REM
REM .mcp.json names "${CLAUDE_PLUGIN_ROOT}/bin/cl-mcp" with NO extension. On Windows
REM the bare name resolves through PATHEXT to this file; on macOS/Linux the kernel
REM execs the sibling `cl-mcp` (#!/bin/sh) directly. One command name, two
REM platform-specific files (nao's pattern, mycelium
REM cross-project:pattern:extensionless-command-resolves-per-platform, measured
REM 2026-09-08). Plugin 0.5.0 used ONE polyglot file whose line-1 shebang cmd.exe
REM could not run, so the server's stdout began with two non-JSON lines; this file
REM has no shebang, so stdout starts with the first JSON-RPC message.
REM
REM Why this file exists: the plugin must not launch cl.exe (Windows locks a
REM running .exe, so pip cannot replace the wheel while a session is open)
REM and must not hard-code an interpreter NAME (macOS has no `python`,
REM Windows `python3` is a 0-byte Store stub). So: try candidates in order
REM and take the first one that can IMPORT crossloom_cli. Validation by
REM import, never by name. Windows order python > py -3 > python3, because
REM `py -3` ignores an active venv. `equ 0` on purpose: `if not errorlevel 1`
REM also accepts NEGATIVE codes such as a 0xC0000005 crash.
REM
REM Keep this file LF-only (CI asserts it; .gitattributes pins eol=lf) and free
REM of goto/labels: cmd.exe mis-seeks labels in LF-only files.

python -c "import crossloom_cli" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python -m crossloom_cli.mcp.server %*
    exit /b
)

py -3 -c "import crossloom_cli" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    py -3 -m crossloom_cli.mcp.server %*
    exit /b
)

python3 -c "import crossloom_cli" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    python3 -m crossloom_cli.mcp.server %*
    exit /b
)

echo cl-mcp: no interpreter can import crossloom_cli (tried python, py -3, python3). Install the wheel: python -m pip install "crossloom-cli[ai] @ git+https://github.com/hanuele/crossloom-cli.git" >&2
exit /b 1
