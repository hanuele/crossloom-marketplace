import { test, expect, mock } from 'claude-code/testing'

const SHOW = (env: string) => `Environment: ${env}\nURL:         https://example/${env}\nUser:        tester\n`
const PROTECTED = { options: { protectedEnvs: 'mwm:dev, wiam-3T:prod' } }

test('the command reports the active environment and marks a protected one', PROTECTED, async ($, on) => {
  mock.clock(on)
  on('process.run', () => ({ value: { exitCode: 0, stdout: SHOW('mwm:dev'), stderr: '' } }))
  on('ui.status', () => ({ value: undefined }))
  const out = await $.command.run({ command: 'cl-env', args: '' })
  expect(out.text).toContain('mwm:dev')
  expect(out.text).toContain('PROTECTED')
})

test('with no protected environments configured, nothing asks and the command says so', async ($, on) => {
  mock.clock(on)
  on('process.run', () => ({ value: { exitCode: 0, stdout: SHOW('mwm:dev'), stderr: '' } }))
  on('ui.status', () => ({ value: undefined }))
  on('tool.call', () => ({ result: 'ran' }))
  const w = await $.tool.call({ tool: 'mcp__crossloom__run_sql', sql: 'select 1' })
  expect(w.deny).toBe(undefined)
  const out = await $.command.run({ command: 'cl-env', args: '' })
  expect(out.text).toContain('no protected environments configured')
})

test('a write verb on a protected env asks, and Cancel denies the call', PROTECTED, async ($, on) => {
  mock.clock(on)
  on('process.run', () => ({ value: { exitCode: 0, stdout: SHOW('mwm:dev'), stderr: '' } }))
  on('ui.status', () => ({ value: undefined }))
  on('tool.call', { tool: 'AskUserQuestion' }, (_$, e) => {
    const q = (e as { questions: { question: string }[] }).questions[0].question
    return { result: { answers: { [q]: 'Cancel' } } }
  })
  on('tool.call', () => ({ result: 'ran' }))
  const ran = await $.tool.call({ tool: 'mcp__crossloom__run_sql', sql: 'select 1' })
  expect(ran.deny).toContain('cancelled on mwm:dev')
})

test('a read verb on a protected env never asks', PROTECTED, async ($, on) => {
  mock.clock(on)
  on('process.run', () => ({ value: { exitCode: 0, stdout: SHOW('mwm:dev'), stderr: '' } }))
  on('ui.status', () => ({ value: undefined }))
  let asked = 0
  on('tool.call', { tool: 'AskUserQuestion' }, () => { asked += 1; return { result: { answers: {} } } })
  on('tool.call', () => ({ result: 'ran' }))
  const r = await $.tool.call({ tool: 'mcp__crossloom__inspect_object', id: 'x' })
  expect(r.deny).toBe(undefined)
  expect(asked).toBe(0)
})
