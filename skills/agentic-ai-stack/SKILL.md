---
name: agentic-ai-stack
description: >-
  Use when the user wants to design or build a multi-agent / agentic AI system —
  not a single chatbot, but a stack of cooperating agents (orchestrator + specialists,
  tools, memory, sandboxed execution, evals, guardrails, deployment). Trigger on phrases
  like "stack of agents", "full agent stack", "multi-agent system", "agent orchestration",
  "build an agentic app", "which agent framework should I use", "LangGraph vs CrewAI",
  "agent architecture", or any request to wire together orchestration + tools + memory +
  observability for autonomous agents. Use this even when the user only names a piece
  (e.g. "I need agent memory" or "how do I orchestrate agents") — it covers the whole
  stack and how the pieces fit. Also use it when the user wants to actually EXECUTE work
  with a team of agents — "use the agent team to build X", "continue building with the
  agents", "dispatch the subagents" — in which case it orchestrates the dedicated aas-*
  Claude Code subagents (planner, researcher, coder, reviewer, tester, ops, memory-curator,
  safety-gate, product-ui). Do NOT use for a single prompt/completion, a basic
  RAG-only chatbot, or generic LLM API questions with no orchestration.
---

# Agentic AI Full Stack

Help the user architect and (optionally) scaffold a real multi-agent system. This skill
runs in two phases: **design the stack**, then **scaffold the chosen pieces into code**.
You don't always do both — many users just want the architecture. Read the user.

## The core principle

There is no single "magic" agent repository. A production agentic app is a *stack* of
cooperating layers, each with a clear job. Steer the user away from hunting for one
framework that does everything, and toward composing the right tool per layer. Every
serious agent system has these eight layers:

1. **Orchestrator** — routes work, holds state, runs long workflows
2. **Specialist agents** — focused roles (planner, coder, researcher, …)
3. **Tool layer** — how agents act on the world (MCP is the emerging standard)
4. **Memory / RAG** — semantic + episodic memory, retrieval over knowledge
5. **Sandboxed execution** — safe place to run code/commands agents generate
6. **Evals & tracing** — see what agents did, measure quality, track cost
7. **Guardrails** — validation, safety, human-approval gates on risky actions
8. **Deployment** — frontend, backend, workflow engine, hosting

A system is only as trustworthy as its weakest layer. A great orchestrator with no
tracing or guardrails is a liability, not a product.

## Phase 1 — Design the stack

### Step 0: Should this be agentic at all?

Before designing a stack, screen the goal *out* of agents if it doesn't need them. Ask: **is
the process deterministic and well-specified enough that a plain workflow, a state machine, or
an existing platform (RPA, a business-rules engine, a SaaS that already does this) would be
more reliable than a probabilistic agent?** For structured business processes — AP/AR,
contract review, order management, compliance checklists — the answer is often yes, and the
honest recommendation is *don't build agents*: the business process is the durable asset, not
the model or the prompt. Only reach for an agentic stack when the work genuinely needs
open-ended reasoning, tool use over an unbounded space, or adaptation you can't enumerate up
front. If it doesn't, say so and stop here.

### Step 1: Interview before recommending

Don't dump a stack on the user. Their constraints change every choice. Ask (adapt to
what they've already told you — skip what's known):

- **Language / ecosystem?** Python vs TypeScript drives the whole framework choice.
- **What do the agents actually do?** Coding? Research? Customer ops? Data pipelines?
- **Scale & latency** — interactive (sub-second) or long-running background workflows?
- **Autonomy & risk** — can agents take irreversible actions, or is it advisory? This
  decides how much guardrail/approval machinery you need.
- **Existing infra** — already on Postgres? Have a vector DB? On a cloud already?
- **Team maturity** — prototyping fast, or building something to run in production?

### Step 2: Recommend a foundation, then justify each layer

A strong, opinionated default foundation (state the reasoning, don't just list names):

> **LangGraph** (orchestration) + **OpenAI Agents SDK** *or* **PydanticAI** (agent
> definitions) + **MCP** (tools) + **Temporal** (durable workflows) +
> **pgvector or Qdrant** (memory) + **Langfuse or Phoenix** (tracing/evals) +
> **E2B** (sandboxed execution) + **Claude Agent SDK** (for coding/repo agents).

Then map each of the eight layers to a concrete pick **for this user**, and explain the
tradeoff. The full catalog of options per layer — with strengths, when-to-use, and what
to avoid — lives in `references/stack-components.md`. Read it before recommending so your
advice reflects current tradeoffs (e.g. why AutoGen and CrewAI are *not* recommended as
the primary architecture). Don't paste the whole catalog at the user; synthesize the
2-3 choices that fit their answers.

These frameworks move fast and their APIs change between versions. Before stating
specific API surface, version numbers, or config for any of them (LangGraph, Mastra,
OpenAI Agents SDK, PydanticAI, MCP, Langfuse, Temporal, E2B, …), **consult Context7 for
current docs** rather than relying on training memory — `resolve-library-id` then
`query-docs`. Use it for the recommendation here and again in Phase 2 before generating
code. Note also that Context7 itself is a useful MCP server to include in the user's
tool layer for the same reason: it lets *their* agents fetch up-to-date library docs.

The memory layer is the one users most often underspecify — they ask for "memory" but mean
three different things. Before recommending a memory setup, read `references/memory.md`: it
covers working vs episodic vs semantic memory, what belongs in each, retrieval/eviction
patterns, and how to pick between pgvector, Qdrant, Redis, and Letta. Memory shape should
follow the user's app, not a default.

### Step 3: Lay out the agent team

Most multi-agent apps start with a recognizable team of roles. The canonical starting
team and each role's responsibility, the tools it should get, and where it needs human
approval is in `references/agent-team.md`. Propose a team scoped to the user's domain —
not all ten roles are needed for every app. For each agent you propose, specify:

- **One clear responsibility** (if you can't state it in a sentence, split or cut it)
- **Defined permissions** — what it may read/write/execute
- **Only the tools it needs** — least privilege; don't hand every agent every tool
- **Human approval gates** for risky/irreversible actions

This per-agent discipline is the single most important design habit. Surface it
explicitly; it's what separates a demo from something safe to deploy.

### Step 4: Produce the design artifact

Summarize the design as a short architecture doc: the eight layers with the chosen tool
for each, the agent team with responsibilities/permissions, and the recommended build
sequence (usually: orchestrator + one specialist + tracing first, then expand). Confirm
with the user before scaffolding.

### Step 5: Persist the agreed design to PROJECT memory

Once the user signs off on the stack, save it as a durable memory so future sessions don't
re-litigate settled choices. **Scope it to this project, never globally.** A stack design
is true for one app; writing it to user-global memory would wrongly leak these choices
(LangGraph, Qdrant, etc.) into every unrelated project the user works on later. Be precise
about where it lands:

- Prefer a **project-local** memory location — inside the project (e.g. a project
  `.claude/`-scoped or project-namespaced memory directory), so it travels with the repo
  and only loads when working on this project.
- If your environment's memory is keyed by project (e.g. a per-project memory directory),
  that is correct — use it. Do **not** write to a shared/global user memory file that is
  loaded across all projects.
- If only a global memory mechanism exists, scope the content explicitly: title and tag it
  with the project name/path so it's unambiguous which app it describes, and never phrase
  it as a general user preference.

Record the chosen stack per layer, the agent team, and the constraints the user gave
(language, scale, risk tolerance, existing infra) — the decisions and their rationale, not
things the eventual repo will already record. This is what lets a later session pick up at
"extend the stack" instead of "what stack?". Skip only if no persistent memory mechanism
exists.

## Phase 2 — Scaffold the chosen pieces

Only after the user agrees on a design. The goal is a runnable skeleton they can grow
into — not a finished product. Full repo layout, per-component generation instructions,
and ready-to-adapt file templates are in `references/scaffold-guide.md` and the
`assets/` directory.

Workflow:

1. **Confirm scope** — which layers to scaffold now. Don't generate code for tools they
   haven't chosen. It's fine to scaffold just the orchestrator + one agent + tracing and
   leave hooks (clearly marked `TODO`) for the rest.
2. **Read `references/scaffold-guide.md`** for the repo layout and the per-component
   recipes (orchestrator graph, agent stubs, MCP wiring, memory/docker-compose, tracing
   init, eval harness, guardrail gate).
   **Before writing code that calls a framework's API, fetch its current docs via
   Context7** (`resolve-library-id` → `query-docs`). The templates in `assets/` are
   intentionally minimal; the real import paths, initialization, and config for
   LangGraph, the chosen agent SDK, Langfuse, E2B, etc. shift between versions, and
   scaffolding from stale memory produces code that doesn't run.
3. **Generate the skeleton**, using the templates in `assets/` as starting points. Match
   the user's chosen language. Wire in tracing and at least one guardrail/approval gate
   from the start — retrofitting these later is painful and the whole point of the skill
   is that they're not optional.
4. **Leave a `README` and a runnable entrypoint** so the user can `docker compose up` /
   run the orchestrator and see one agent loop execute end to end.

## Phase 3 — Execute with the subagent team (orchestration mode)

Use this when the user wants the skill to **do the work**, not just design or scaffold —
e.g. "use the agent team to build X", "continue building with the agents", or any request
to actually implement against their repo. Here the team isn't a diagram; it maps onto real
**Claude Code subagents** that you dispatch.

**You (the main session) are the Orchestrator.** Claude Code subagents cannot spawn other
subagents, so the orchestration loop lives here, in the main thread. The worker roles are
installed as user-level agents (dispatch them with the Agent tool via `subagent_type`):

| Role | subagent_type | Permission boundary (enforced by its tools) |
|---|---|---|
| Planner | `aas-planner` | read-only |
| Researcher | `aas-researcher` | read-only + web + Context7 docs |
| Coder | `aas-coder` | edit/write/bash, **branch-only** |
| Reviewer | `aas-reviewer` | read-only |
| Tester | `aas-tester` | bash for tests only |
| Ops | `aas-ops` | **human approval required** on every mutation |
| Memory Curator | `aas-memory-curator` | scoped writes to project memory only |
| Safety Gate | `aas-safety-gate` | read-only; returns APPROVE/VETO |
| Product/UI | `aas-product-ui` | design docs only |
| Orchestrator | `aas-orchestrator` | optional planning aid that drafts a dispatch plan |

If a request is missing (the `aas-*` agents aren't installed), fall back to dispatching
`general-purpose` subagents with the role's responsibility and permission constraints stated
in the prompt — but prefer the dedicated agents, since their tool scoping enforces least
privilege rather than just asking for it.

### The orchestration loop

1. **Plan.** Dispatch `aas-planner` (or `aas-orchestrator` for a full dispatch plan) to turn
   the goal into ordered steps with role assignments and flagged risky actions. Confirm the
   plan with the user if the work is large or irreversible.
2. **Gather context in parallel.** Dispatch `aas-researcher` (one or several in parallel) for
   anything the plan needs — repo facts, current library APIs via Context7. Independent
   research fans out; see `superpowers:dispatching-parallel-agents` for the pattern.
3. **Implement.** Dispatch `aas-coder` for each implementation step. It works on a feature
   branch only.
4. **Verify in parallel.** After the coder reports, dispatch `aas-reviewer` and `aas-tester`
   together — review and tests are independent. Route their findings back to `aas-coder` and
   loop until clean or a retry cap is hit.
5. **Gate risky actions.** Before anything irreversible (deploy, migration, destructive
   command), dispatch `aas-safety-gate` to screen it. A VETO stops the action.
6. **Ops behind a human gate.** Dispatch `aas-ops` only for infra/deploy work, and surface
   its proposed commands to the **human for explicit approval** before it runs them. Never
   auto-approve on the user's behalf.
7. **Persist.** Dispatch `aas-memory-curator` to record durable decisions to **project**
   memory (not global) so the next session has continuity.

### Optimization-shaped goals: HTR mode

The loop above is **linear** — `plan → code → review/test → loop-until-clean` — and is right
for feature/bugfix work with a known correct answer. When the goal is instead to **optimize a
measurable target against a held-out eval** (make it faster/cheaper/more accurate, tune a
model or pipeline, climb an eval score), switch to **Hypothesis-Tree Refinement (HTR) mode**:
keep a tree of hypotheses where every branch's evidence — including failures — compounds, so
later attempts start smarter than blank-slate retries. It reuses the same `aas-*` team (you =
Coordinator, `aas-coder` in a worktree = Executor, `aas-tester` = held-out margin gate,
`aas-memory-curator` = insight backprop). Read `references/htr-orchestration.md` before
running it. Don't use HTR when there's no metric or no held-out set — fall back to the linear
loop.

### Orchestration discipline

- **You hold state and route; you are not the hands.** Keep your own direct edits minimal —
  delegate implementation to the Coder so roles and permissions stay clean.
- **Respect least privilege.** Don't work around a role's boundary by doing its
  forbidden action yourself in the main thread (e.g. deploying because Ops would need
  approval). The gates exist on purpose.
- **Parallelize the independent, serialize the dependent.** Research and verification fan
  out; plan→code→review is a chain.
- **Give each subagent a tight, self-contained prompt** — it doesn't see this conversation.
  State the goal, the inputs (files, branch, prior findings), and exactly what to return.
- Track the stages with TodoWrite so the user can see the loop's progress.

## Anti-patterns to call out

If you see the user heading toward these, say so:

- **Framework maximalism** — adopting five overlapping frameworks. Pick one per layer.
- **Skipping tracing/evals** until "later" — you'll fly blind on cost and quality.
- **God-agent** — one agent with all tools and no role boundaries. Split it.
- **No human gate on irreversible actions** — destructive ops need approval.
- **CrewAI/AutoGen as the load-bearing core** — fine for prototypes, not the foundation
  (see `references/stack-components.md` for why).
