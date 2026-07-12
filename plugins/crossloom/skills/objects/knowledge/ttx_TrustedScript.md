# ttx_TrustedScript — Cheat Sheet

> Quick-reference for creating and editing CrossLoom TrustedScripts. This sheet
> is the *index*, not the manual — depth lives in
> `cl://playbook/trustedscript-conventions` and
> `cl://playbook/runtime-architecture`. Read those before writing C#.

## Checklist (before you call it done)
- [ ] Created under the correct Trusted Code folder — not at the application root.
- [ ] Description is set (an empty Description makes the script hard to find later).
- [ ] ScriptCode deployed from a file: `cl write <uuid> -p ScriptCode --file script.cs` (verb verified).
- [ ] Dependencies declared as `ttx_Dependency_Script` entries (see Required relations).
- [ ] Linted: `cl validate-script <uuid>` (checks the four JIT invariants).

## Required relations
- **`ttx_Dependency_Script`** — every library or sibling script this TrustedScript
  references needs a dependency entry. These are **not** created by `cl create`;
  add them explicitly, or the script fails to resolve its references at runtime.

## Parenting rules
- A TrustedScript belongs under its Trusted Code folder — a `ttx_Menu_CrossLoom`
  node, the only valid parent type (live appmodel) — not the app
  root. An object created with a zero-GUID parent is orphaned and **invisible in
  the Admin UI**. Inspect valid parents with `cl appmodel ttx_TrustedScript`, then
  create inside the folder: `cl objects` → `cl down <N>` → `cl create`.

## Gotchas
- **No build step.** The saved script is canonical; the next request loads it.
- **JIT invariants.** The Roslyn/JIT path has four invariants (confirmed via
  `cl validate-script --help`: outer class name, parameter
  injection, C# ≤5 syntax, one public class) that each cost ~90 minutes of
  trial-and-error if violated. Read `cl://playbook/trustedscript-conventions`
  first.
- **Large ScriptCode.** `cl write -v` can't take 32KB of source inline — use
  `cl write <uuid> -p ScriptCode --file <path>` (or `-f -` to pipe from stdin).

## See also
- `cl validate-script <uuid>` — lint against the four JIT invariants
- `cl howto` — list all available cheat sheets
- `cl://playbook/trustedscript-conventions` — the four invariants, in depth
- `cl://playbook/runtime-architecture` — scripting engines, handlers, DB model
