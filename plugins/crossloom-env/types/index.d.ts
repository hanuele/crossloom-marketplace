export type Tone = 'quiet' | 'ok' | 'attention'
export type BandLine = { text: string; tone: Tone }

declare module 'claude-code' {
  interface PluginState {
    'crossloom-env': { line: BandLine | null }
  }
}
