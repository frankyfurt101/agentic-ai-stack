# agentic-ai-stack

Backup + source of truth for my **`/agentic-ai-stack`** Claude Code skill and its dedicated
`aas-*` subagent team. Private repo so I can rebuild this setup on any machine if `~/.claude`
is ever lost.

## What's in here

```
skills/agentic-ai-stack/    # the skill itself
  SKILL.md                  # entry point: Phase 0 gate, design interview, scaffold, orchestration
  references/
    stack-components.md     # the 8-layer catalog (orchestration, tools, memory, evals, …)
    memory.md               # working vs episodic vs semantic memory; store choice
    agent-team.md           # canonical agent roles + permissions
    scaffold-guide.md       # Phase-2 repo layout + per-component recipes
    htr-orchestration.md    # Hypothesis-Tree Refinement mode (Arbor-derived)
  assets/                   # docker-compose + agent stub templates
  evals/evals.json
agents/                     # the 10 aas-* user-level subagents the skill dispatches
  aas-planner / researcher / coder / reviewer / tester / ops /
  memory-curator / safety-gate / product-ui / orchestrator
```

## The skill in one line

A production agentic app is a **stack of 8 layers** (orchestrator, specialist agents, tools,
memory/RAG, sandbox, evals/tracing, guardrails, deployment), not one magic framework. The
skill runs three phases — **design** the stack, **scaffold** the chosen pieces, **execute**
with the `aas-*` subagent team (main session = Orchestrator; workers are tool-scoped for
least privilege). Two orchestration loop shapes: the default linear loop, and **HTR mode**
for optimization-shaped goals with a measurable held-out metric.

## Restore onto a fresh machine

```bash
# from a clone of this repo
cp -R skills/agentic-ai-stack ~/.claude/skills/
cp agents/aas-*.md            ~/.claude/agents/
# or just run:
./install.sh
```

Then in Claude Code the skill is available as `/agentic-ai-stack` and the agents as
`subagent_type: aas-*`.

## Design lineage

See [`DECISIONS.md`](./DECISIONS.md) for the change history and the rationale behind what's
in the catalog — including what was **deliberately left out** and why, so future-me doesn't
re-add it.

## License

Licensed under the **Apache License, Version 2.0** — see [`LICENSE`](./LICENSE) and
[`NOTICE`](./NOTICE). You may use, modify, and distribute this (including inside a company)
under the terms of that license; it includes an explicit patent grant. Contributions are
accepted under the same license.
