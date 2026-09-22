#!/bin/sh
: << 'CMDBLOCK'
@echo off
REM cl-mcp.cmd -- polyglot launcher for the crossloom MCP server (#900389).
REM
REM Line 1 is a real shebang so macOS/Linux exec this file directly (Node's
REM posix_spawn does NOT fall back to /bin/sh on ENOEXEC, so a shebang-less
REM script would silently never start there). cmd.exe cannot run line 1: it
REM echoes it to stdout once and reports it on stderr, then continues -- the
REM MCP client tolerates that one stray line (measured with `claude mcp list`
REM on Windows, 2026-09-22: Connected). Line 2 is a label to cmd.exe (not
REM echoed, not executed) and a heredoc to sh that swallows this batch half.
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
REM Keep this file LF-only and free of goto/labels: cmd.exe mis-seeks
REM labels in LF-only files, and the polyglot needs LF for sh.

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
CMDBLOCK

# Unix (macOS / Linux). macOS ships no `python`, so python3 goes first;
# both are validated by import, never taken on name alone.
for py in python3 python; do
    if command -v "$py" >/dev/null 2>&1 && "$py" -c 'import crossloom_cli' >/dev/null 2>&1; then
        exec "$py" -m crossloom_cli.mcp.server "$@"
    fi
done
echo 'cl-mcp: no interpreter can import crossloom_cli (tried python3, python). Install the wheel: python3 -m pip install "crossloom-cli[ai] @ git+https://github.com/hanuele/crossloom-cli.git"' >&2
exit 1
