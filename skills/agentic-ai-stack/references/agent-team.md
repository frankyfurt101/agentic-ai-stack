# The Initial Agent Team

A multi-agent app usually starts with a recognizable team of roles. Below is the
canonical starting team, each role's job, and its permission boundary. **Least privilege
is the rule**: give each agent only what its job requires, and require human approval for
anything irreversible.

Not every app needs all ten. Scope the team to the user's domain — a research assistant
might be Orchestrator + Planner + Researcher + Memory Curator + Safety Gate, while a
coding platform uses nearly all of them.

| Agent | Job | Permissions |
|---|---|---|
| **Orchestrator** | Breaks tasks down, routes work, merges results | No direct destructive actions |
| **Planner** | Creates step-by-step execution plans | Read-only |
| **Researcher** | Pulls docs, citations, web/internal knowledge | Read-only |
| **Coder** | Writes implementation patches | Branch-only edits |
| **Reviewer** | Reviews diff, catches bugs/security issues | Read-only |
| **Tester** | Runs tests, reports failures | Test execution only |
| **Ops Agent** | Docker, deploys, migrations, rollback plans | Approval required |
| **Memory Curator** | Stores decisions, user preferences, project state | Scoped memory writes |
| **Safety Gate** | Blocks risky commands, PII leaks, prompt injection | Can veto |
| **Product/UI Agent** | Turns user needs into UI/UX acceptance criteria | Read/write design docs |

## Reading the permission column

The permission boundaries aren't decoration — they're the contract you enforce in code
(via tool scoping, separate credentials, and approval gates):

- **No direct destructive actions** (Orchestrator) — it coordinates and delegates, but
  never deletes/deploys itself. It must route risky work through the Ops Agent + Safety
  Gate. This keeps the "brain" from also being the "hands."
- **Read-only** (Planner, Researcher, Reviewer) — these reason and report. They get
  retrieval/search tools but no write or execute tools at all.
- **Branch-only edits** (Coder) — writes to a feature branch, never to `main`/`prod`
  directly. Its changes are gated behind Reviewer + Tester before merge.
- **Test execution only** (Tester) — can run the test suite in the sandbox, but not edit
  source or touch deploy targets.
- **Approval required** (Ops Agent) — the only agent that touches infra (deploys,
  migrations, rollbacks). Every action it proposes pauses for a human gate.
- **Scoped memory writes** (Memory Curator) — writes only to the memory store, only the
  namespaces it owns. It can't reach into code or infra.
- **Can veto** (Safety Gate) — sits in the path of risky operations and can block them
  (dangerous commands, PII leaks, prompt-injection attempts). It's a checkpoint, not a
  worker; it doesn't produce output, it approves/denies.
- **Read/write design docs** (Product/UI Agent) — owns acceptance criteria and design
  artifacts; no code or infra access.

## How they interact (typical flow)

1. **Orchestrator** receives the goal, asks **Planner** for a plan.
2. **Researcher** gathers any needed context/docs.
3. **Coder** implements on a branch; **Reviewer** and **Tester** check it.
4. **Safety Gate** screens any risky action; **Ops Agent** deploys *after human approval*.
5. **Memory Curator** records decisions and state so the next run has context.
6. **Product/UI Agent** keeps work tied to acceptance criteria.

When proposing a team to the user, give each agent a one-sentence responsibility, its
tool list, and its approval needs — mirroring this table but specialized to their app.

## Mapping to real Claude Code subagents (execution mode)

These roles are installed as dispatchable user-level subagents, so the skill can *execute*,
not just advise. The main session is the Orchestrator and dispatches the rest via the Agent
tool (subagents can't spawn subagents). Each agent's permission row above is enforced by the
`tools:` field in its definition, not just by prompt.

| Role | `subagent_type` |
|---|---|
| Orchestrator | main session (or `aas-orchestrator` for a dispatch plan) |
| Planner | `aas-planner` |
| Researcher | `aas-researcher` |
| Coder | `aas-coder` |
| Reviewer | `aas-reviewer` |
| Tester | `aas-tester` |
| Ops Agent | `aas-ops` |
| Memory Curator | `aas-memory-curator` |
| Safety Gate | `aas-safety-gate` |
| Product/UI Agent | `aas-product-ui` |

See Phase 3 in `SKILL.md` for the orchestration loop (plan → research → code → review+test
→ gate → ops-with-approval → persist).
