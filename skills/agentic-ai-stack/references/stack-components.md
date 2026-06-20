# Stack Components Catalog

Options per layer, with strengths and when to reach for them. Synthesize 2-3 picks that
fit the user's answers (language, scale, risk, existing infra) — don't paste the whole
catalog at them.

## 1. Orchestration

- **LangGraph** — stateful orchestration, planning, routing, long-running workflows.
  Strong default for graph-shaped agent flows with branching and loops. Python + JS.
- **OpenAI Agents SDK** — agents, handoffs, structured outputs, built-in guardrails.
  Clean for handoff-style multi-agent and structured tool use.
- **PydanticAI** — typed outputs, production Python workflows. Pick when type safety and
  validation of agent outputs matter and you're Python-first.
- **Mastra** — TypeScript-first agent framework with workflows, RAG, and observability
  built in. The strongest single choice for a TS/Node shop that wants batteries included.
- **Claude Agent SDK / Claude Code** — coding agents, repo understanding, subagents,
  hooks, skills. Best for software-engineering agents that work over a real codebase.
- **Deep Agents SDK (LangChain)** — the LangChain-ecosystem counterpart to the Claude Agent
  SDK for the subagents-plus-skills pattern (planner/sub-agent decomposition, file tools).
  Reach for it when you want that shape without leaving Lang tooling. For simpler agents,
  LangGraph directly is usually enough — Deep Agents and Claude Agent SDK earn their keep
  only when you specifically want managed subagents + skills.
- **OpenHands** — autonomous software-engineering agents and coding workflows. Use when
  you want an existing autonomous-coding platform rather than building one.
- **Arbor (HTR)** — *not* a general orchestrator; a hypothesis-tree search loop for
  **optimization-shaped** goals with a measurable target and a held-out eval (model tuning,
  perf/harness engineering, eval-score climbing). Attempts compound via a tree of hypotheses
  instead of linear retry. Reach for it as an *alternative loop* alongside the default, not a
  replacement. See `references/htr-orchestration.md` for the mode mapped onto the `aas-*`
  team; the upstream `RUC-NLPIR/Arbor` CLI is the heavier standalone option.
- **Custom orchestrator on a durable engine** — a thin in-house SDK over **Temporal** (or
  Restate) instead of any named agent framework. Several serious production teams run exactly
  this and would keep it: full control of the agent loop, no fighting a framework's
  abstractions. Choose it **only** if you have the platform-engineering muscle to own retries,
  state, isolation, and observability yourself — otherwise a framework gets you there faster.

## 2. Tool layer

- **MCP (Model Context Protocol)** — the emerging standard for giving agents tools.
  Servers exist for GitHub, filesystems, databases, APIs, and you can write custom ones.
  Default to MCP so tools are reusable across agents and frameworks.
- **A2A Protocol** — agent-to-agent communication for multi-service collaboration. Reach
  for it when independent agent services need to talk, not just call tools.
- **Context7 (MCP server)** — fetches current, version-accurate library/framework docs.
  Worth giving to agents (especially the Coder and Researcher) so they write code against
  today's APIs instead of stale training data. Also use it yourself when advising on or
  scaffolding any of the fast-moving frameworks in this catalog.

**Principle: tools should be deterministic, not model-generated.** The LLM decides *what* to
do; the tool decides *how*. A tool is a typed, tested wrapper around a real operation (query
this DB, call this API, run this command) — not a place to let the model emit freeform code
that runs unsandboxed. Push every operation that *can* be deterministic into a tool and keep
the probabilistic surface as small as possible. This is the highest-leverage production habit
at the tool layer: it makes failures debuggable (a tool call either ran or it didn't) instead
of emergent. Model-generated code that genuinely must run belongs in the sandbox (layer 4),
behind a typed tool — not inlined into the agent loop. (The Coder's least-code preflight and
HTR's held-out gate are the same instinct applied elsewhere: shrink and fence the
probabilistic part.)

> Memory has its own dedicated reference: see `references/memory.md` for how to choose and
> combine the layer-3 options below.

## 3. Memory / RAG

- **pgvector** — vector search inside Postgres. Best when you already run Postgres and
  want one fewer system to operate; semantic memory + relational data together.
- **Qdrant** — dedicated vector database. Pick for large-scale or high-throughput
  semantic retrieval where a purpose-built store pays off.
- **Redis** — fast ephemeral/session memory and caching; pairs with a vector store.
- **Letta** — long-term agent memory as a managed concern. Use when persistent,
  evolving memory across sessions is a first-class product requirement.
- **LlamaIndex / Haystack** — RAG, knowledge retrieval, document ingestion pipelines.
  Use when ingesting and querying a real document corpus is central.

## 4. Sandboxed execution

- **E2B** — secure cloud execution sandboxes for code/commands agents generate. Default
  for running untrusted agent-generated code safely.
- **Docker sandboxes** — self-hosted isolation when you want to run execution on your own
  infra or air-gapped.

## 5. Evals & tracing

- **Langfuse** — tracing, evaluation, and cost visibility. Strong open default; wire it
  in from day one so you can see every agent step and what it cost.
- **Phoenix (Arize)** — tracing and evaluation with a strong analysis UI. Comparable
  choice; pick based on team familiarity and hosting preference.
- **Logfire (Pydantic)** — tracing/observability from the Pydantic team; the natural pairing
  if you chose PydanticAI at layer 1, since the instrumentation is built in. Pick it when
  you're already in the Pydantic ecosystem rather than standing up Langfuse/Phoenix
  separately.

## 6. Guardrails / safety

- **NeMo Guardrails** — programmable rails for dialogue and action safety.
- **Guardrails AI** — output validation and structured safety checks.
- Plus **human approval gates** for irreversible actions — the cheapest, most reliable
  guardrail. No framework replaces a human in the loop on destructive ops.

## 7. Workflow engine (durability)

- **Temporal** — durable execution for long-running, resumable workflows that survive
  crashes and retries. Use when agent jobs run for minutes-to-hours and must not lose
  state midway.

## 8. Deployment

- **Frontend** — Next.js, SwiftUI, or React Native depending on platform.
- **Backend** — FastAPI (Python) or Node.js (TS), matching the agent-core language.

## Not recommended as the foundation

- **AutoGen** — in maintenance mode; don't build a new load-bearing core on it.
- **CrewAI** — good for quick prototypes, but not ideal as the primary production
  architecture. Fine to prototype with, then graduate to LangGraph/Agents SDK.

These can still appear in a prototype — just don't let them become the core the whole
system depends on.

## The recommended foundation, in one line

> LangGraph + (OpenAI Agents SDK *or* PydanticAI) + MCP + Temporal +
> (pgvector *or* Qdrant) + Langfuse + E2B + Claude Agent SDK

Each agent in the resulting system should have: a clear responsibility, defined
permissions, access only to required tools, and human approval for risky actions.
