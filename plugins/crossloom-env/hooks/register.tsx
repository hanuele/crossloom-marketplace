// crossloom-env — which CrossLoom environment is this session pointed at?
//
// The active environment is a machine-wide `cl env use` setting that nothing in
// the session shows, so a write verb can run against the wrong instance
// unnoticed. This mod reads `cl env show` at start and every minute, draws
// `CrossLoom <system:stage>` in a calm band above the prompt, toasts when it
// changes, and, on an environment listed in the `protectedEnvs` option, asks
// once before a crossloom MCP write verb runs: Cancel denies the call. If the
// question cannot be asked (a -p run, a dismissed dialog) the call goes on:
// this is a confirmation, not a gate.

import { atom, read, update } from 'claude-code'
import type { EngineInterface, Register } from 'claude-code'
import type { BandLine, Tone } from '../types'

const POLL_MS = 60 * 1000
const WRITE_VERB = /^(run_sql|deploy_|patch_|safe_property_update|create_|delete_|revert_|package_preview_then_apply|bootstrap_rollout|inject_|set_|smartui_init|fire_|toggle_|update_|write_|add_to_|changeset_add|restore_|cleanup_)/

const line = atom({ plugin: 'crossloom-env', key: 'line' } as const, null)

type Ctx = { env: string | null; url: string | null; lastShown: string | null; protectedEnvs: Set<string> }

export function parseEnvShow(stdout: string): { env: string | null; url: string | null } {
  const env = /^Environment:\s*(\S+)/m.exec(stdout)?.[1] ?? null
  const url = /^URL:\s*(\S+)/m.exec(stdout)?.[1] ?? null
  return { env, url }
}

/** the crossloom verb name from an MCP tool name, or null for any other tool */
export function crossloomVerb(tool: string): string | null {
  const m = /^mcp__(?:plugin_crossloom_)?crossloom__([a-z_]+)$/.exec(tool)
  return m ? m[1] : null
}

export function parseProtected(value: unknown): Set<string> {
  const s = typeof value === 'string' ? value : ''
  return new Set(s.split(',').map(x => x.trim()).filter(Boolean))
}

function isProtected(ctx: Ctx): boolean {
  return ctx.env !== null && ctx.protectedEnvs.has(ctx.env)
}

async function show($: EngineInterface, text: string, tone: Tone): Promise<void> {
  try { await update($, line, () => ({ text, tone } as BandLine)) } catch { /* no state host (a test): nothing to draw */ }
}

async function refresh($: EngineInterface, ctx: Ctx): Promise<void> {
  try {
    const { exitCode, stdout } = await $.process.run(['cl', 'env', 'show'], { timeoutMs: 15_000 })
    const parsed = exitCode === 0 ? parseEnvShow(stdout) : { env: null, url: null }
    const changed = ctx.lastShown !== null && parsed.env !== ctx.lastShown
    ctx.env = parsed.env
    ctx.url = parsed.url
    if (changed) $.ui.toast(`CrossLoom environment changed: ${ctx.lastShown} -> ${parsed.env ?? 'unknown'}`)
  } catch {
    ctx.env = null
    ctx.url = null
  }
  ctx.lastShown = ctx.env
  if (ctx.env === null) await show($, 'CrossLoom env unknown (cl env show failed)', 'attention')
  else if (isProtected(ctx)) await show($, `CrossLoom ${ctx.env} · PROTECTED`, 'attention')
  else await show($, `CrossLoom ${ctx.env}`, 'ok')
}

export const register: Register = (on, options) => {
  const ctx: Ctx = { env: null, url: null, lastShown: null, protectedEnvs: parseProtected(options.protectedEnvs) }

  on('session.start', async ($, e, next) => {
    await $.command.register({ name: 'cl-env', description: 'Show the active CrossLoom environment this session is pointed at' })
    $.clock.every(POLL_MS, () => { void refresh($, ctx) })
    $.clock.after(3_000, () => { void refresh($, ctx) })
    await show($, 'CrossLoom env: reading...', 'quiet')
    return next(e)
  })

  on('ui.render', { component: 'AbovePrompt' }, async ($, e, next) => {
    const current = await read($, line)
    const rest = await next(e)
    if (current === null) return rest
    const { Box, Text } = $.ui.resolve(e)
    const colour = current.tone === 'attention' ? 'yellow' : current.tone === 'ok' ? 'green' : undefined
    return (
      <Box flexDirection="column">
        {rest}
        <Text color={colour} dimColor={current.tone === 'quiet'}>{current.text}</Text>
      </Box>
    )
  })

  on('command.run', { command: 'cl-env' }, async ($) => {
    await refresh($, ctx)
    const mark = isProtected(ctx) ? 'PROTECTED (write verbs ask first)' : ctx.protectedEnvs.size ? 'not protected' : 'no protected environments configured'
    return { text: `${ctx.env ?? 'unknown'}  ${ctx.url ?? ''}  ${mark}` }
  })

  // confirmation before a crossloom write verb on a protected environment
  on('tool.call', async ($, e, next) => {
    const verb = crossloomVerb(e.tool)
    if (verb === null || !WRITE_VERB.test(verb)) return next(e)
    if (ctx.lastShown === null) await refresh($, ctx)
    if (!isProtected(ctx)) return next(e)
    const answer = await $.ui.ask(
      `crossloom ${verb} would run on ${ctx.env}, a protected environment. Continue?`,
      ['Cancel', `Continue on ${ctx.env}`],
    )
    if (answer === 'Cancel') return { deny: `crossloom-env: ${verb} cancelled on ${ctx.env} (protected).` }
    return next(e)
  }).catch(($, e, next) => next(e))
}
