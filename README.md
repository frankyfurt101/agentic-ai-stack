# agentic-ai-stack

[![License: Apache 2.0](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](./LICENSE)
[![Claude Code](https://img.shields.io/badge/Claude%20Code-skill-orange.svg)](https://claude.com/claude-code)

A **Claude Code skill** + a dedicated, tool-scoped **`aas-*` subagent team** for designing,
scaffolding, and executing production multi-agent systems — 8-layer stack design, least-privilege
agents, an HTR optimization mode, and superpowers-style execution discipline. Also serves as the
source of truth so the setup can be rebuilt on any machine if `~/.claude` is ever lost.

## Quick start

```bash
git clone https://github.com/frankyfurt101/agentic-ai-stack.git
cd agentic-ai-stack && ./install.sh
```

Installs into `~/.claude/skills` and `~/.claude/agents`. Restart Claude Code, then invoke
`/agentic-ai-stack` (or dispatch the team via `subagent_type: aas-*`). See [Restore onto a
fresh machine](#restore-onto-a-fresh-machine) for the manual steps `install.sh` runs.

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
