# Scaffold Guide

How to generate a runnable skeleton once the user has agreed on a design. Goal: a
skeleton they can run end-to-end (one agent loop executing, with tracing on), not a
finished product. Match the user's chosen language — recipes below default to Python
(LangGraph + FastAPI); the TypeScript path uses Mastra.

## Recommended repo layout (Python foundation)

```
my-agent-app/
├── docker-compose.yml          # postgres+pgvector, qdrant, redis, langfuse
├── .env.example                # API keys, DB URLs, LANGFUSE_*  (never commit real keys)
├── pyproject.toml              # deps: langgraph, pydantic-ai/openai-agents, langfuse, ...
├── README.md                   # how to run it
├── src/
│   ├── orchestrator/
│   │   └── graph.py            # LangGraph graph: nodes = agents, edges = routing
│   ├── agents/
│   │   ├── base.py             # shared agent factory (model, tools, tracing wrapper)
│   │   ├── planner.py          # read-only
│   │   ├── researcher.py       # read-only
│   │   ├── coder.py            # branch-only edits
│   │   ├── reviewer.py         # read-only
│   │   └── ...                 # one file per chosen role
│   ├── tools/
│   │   └── mcp_client.py       # connects to MCP servers; exposes scoped tools per agent
│   ├── memory/
│   │   ├── vector_store.py     # pgvector or qdrant client
│   │   └── curator.py          # scoped memory writes (Memory Curator)
│   ├── sandbox/
│   │   └── executor.py         # E2B or docker sandbox wrapper for running code
│   ├── guardrails/
│   │   └── safety_gate.py      # veto layer + human-approval gate
│   ├── observability/
│   │   └── tracing.py          # Langfuse init; wrap every agent/tool call
│   └── main.py                 # FastAPI entrypoint; POST /run drives the orchestrator
├── evals/
│   ├── dataset.jsonl           # task -> expected outcome
│   └── run_evals.py            # scores agent outputs, logs to Langfuse
└── workflows/
    └── temporal_worker.py      # (optional) durable long-running workflows
```

For TypeScript, collapse to a Mastra project: `src/mastra/{agents,workflows,tools}`,
`src/index.ts`, same docker-compose for infra, Mastra's built-in observability for tracing.

## Per-component recipes

Generate only the layers the user chose. For each, leave clear `TODO:` markers where the
user must add domain logic or credentials.

- **Orchestrator (`graph.py`)** — define a LangGraph `StateGraph` whose nodes are the
  chosen agents and whose edges encode routing (planner → coder → reviewer → tester,
  with the Safety Gate on edges to risky nodes). Start with a linear flow; note where
  conditional edges go.
- **Agent stubs (`agents/*.py`)** — use the `assets/agent_stub.py` template. Each agent
  gets a system prompt stating its single responsibility, a **scoped** tool list (only
  what its permission row allows), and the tracing wrapper. Read-only agents get no
  write/execute tools — enforce it here, not just in the prompt.
- **Tool layer (`tools/mcp_client.py`)** — connect to MCP servers; expose a function that
  returns the *subset* of tools a given agent is allowed. Least privilege lives here.
- **Memory (`memory/`, docker-compose)** — bring up pgvector or Qdrant + Redis via
  compose; `vector_store.py` does embed/upsert/query; `curator.py` restricts writes to
  owned namespaces.
- **Sandbox (`sandbox/executor.py`)** — wrap E2B (or docker) so the Coder/Tester run
  generated code in isolation, never on the host.
- **Tracing (`observability/tracing.py`)** — initialize Langfuse and provide a decorator
  used to wrap every agent and tool call. Wire this in from the first commit.
- **Guardrails (`guardrails/safety_gate.py`)** — a veto function screening for dangerous
  commands / PII / injection, plus a `require_approval()` that pauses irreversible actions
  for a human. The Ops Agent's actions route through this.
- **Evals (`evals/`)** — a small dataset + a runner that scores outputs and logs to the
  tracing tool, so quality is measurable from day one.

## Non-negotiables when scaffolding

Even a minimal skeleton wires in **tracing** and at least one **guardrail/approval gate**.
These are the layers users are most tempted to defer and most expensive to retrofit —
generating them up front is the whole point of building from a stack rather than a demo.

Always finish with a `README.md` and a runnable entrypoint so the user can
`docker compose up` and run one agent loop end to end.
