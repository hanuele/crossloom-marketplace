: << 'CMDBLOCK'
@echo off
REM cl-mcp.cmd -- polyglot launcher for the crossloom MCP server (#900389).
REM
REM Windows: cmd.exe runs this batch part. The first line is a label to cmd
REM (":"), so it is neither echoed nor executed. Unix: sh reads the first
REM line as a heredoc that swallows everything up to CMDBLOCK, then runs
REM the shell part at the bottom.
REM
REM Why this file exists: the plugin must not launch cl.exe (Windows locks a
REM running .exe, so pip cannot replace the wheel while a session is open)
REM and must not hard-code an interpreter NAME (macOS has no `python`,
REM Windows `python3` is a 0-byte Store stub). So: try candidates in order
REM and take the first one that can IMPORT crossloom_cli. Validation by
REM import, never by name. Windows order python > py -3 > python3, because
REM `py -3` ignores an active venv.
REM
REM Keep this file LF-only and free of goto/labels: cmd.exe mis-seeks
REM labels in LF-only files, and the polyglot needs LF for sh.

python -c "import crossloom_cli" >nul 2>&1
if not errorlevel 1 (
    python -m crossloom_cli.mcp.server %*
    exit /b
)

py -3 -c "import crossloom_cli" >nul 2>&1
if not errorlevel 1 (
    py -3 -m crossloom_cli.mcp.server %*
    exit /b
)

python3 -c "import crossloom_cli" >nul 2>&1
if not errorlevel 1 (
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
