# Memory & Context Architecture

Users ask for "memory" and mean one of three different things. Conflating them is the most
common memory mistake — each has different storage, retrieval, and lifecycle needs. Tease
apart which the user actually needs before recommending a store.

## The three kinds of memory

| Kind | What it is | Lifetime | Typical store |
|---|---|---|---|
| **Working memory** | The current run's state: the task, intermediate results, the message/scratchpad the agents pass around | One run/session | Orchestrator state object (LangGraph state), or Redis for cross-process sharing |
| **Episodic memory** | What happened before: past conversations, decisions, user preferences, prior answers | Across sessions, per user/project | Vector store (pgvector/Qdrant) holding summaries/facts, retrieved by relevance |
| **Semantic memory / knowledge** | A corpus the agent reasons over: docs, code, wiki, tickets | Long-lived, shared | Vector store + ingestion pipeline (chunk → embed → index); this is RAG |

The trap: "it should remember our past chats AND search our internal docs" is **two
systems** — episodic memory (user state) and a semantic knowledge corpus (RAG). They can
share one physical store (e.g. pgvector with separate tables/namespaces) but they have
different write paths, retrieval semantics, and freshness needs. Keep them distinct in the
design even if co-located.

## What to store (and what not to)

Working memory is cheap and ephemeral — keep the full state. Episodic and semantic memory
are where discipline matters, because unbounded growth degrades retrieval quality and
cost:

- **Store summaries and facts, not raw transcripts.** A 50-turn conversation becomes a few
  durable facts ("user prefers TypeScript", "chose Qdrant over pgvector for scale"). Write
  these via the **Memory Curator** agent (scoped writes only — see `agent-team.md`).
- **Attach metadata** (user id, project, timestamp, source) so retrieval can filter, not
  just similarity-match.
- **Don't memorize what's authoritative elsewhere.** If it's in the codebase, the ticket
  system, or the docs corpus, retrieve it at query time rather than copying it into
  episodic memory where it goes stale.

## Retrieval & eviction patterns

- **Partition memory per project (and per user/tenant) — never one global pool.** Episodic
  and semantic memory belong to a specific app and user; a single shared store across
  projects leaks one project's decisions and one user's data into another. Enforce this in
  the store: separate namespaces/collections/tables per project, and a mandatory
  `project_id` (and `user_id` where relevant) on every record. The Memory Curator writes
  only within the current project's namespace.
- **Retrieve by relevance + recency + scope**, not similarity alone. Filter to the current
  project/user *first* (it's a hard boundary, not a ranking signal), then rank by
  similarity within that partition. A pure vector search across all projects/users leaks
  context and is a data-isolation bug, not just a quality issue.
- **Summarize-and-compact** episodic memory periodically: collapse many small entries into
  consolidated facts so the store doesn't bloat. This is a Memory Curator job.
- **Revise, don't just replay.** Long-running agents drift when episodic memory only
  *retrieves* old conclusions and never *updates* them. When new evidence contradicts a stored
  fact, the Memory Curator should supersede it (mark the old entry stale), not append a
  contradiction the agent will keep re-reading alongside the original. Memory that can revise
  its own earlier conclusions is what stops a multi-session agent from compounding an old
  mistake — it's the difference between memory and a transcript. **Letta** is the managed
  option if you'd rather not build this self-editing loop yourself.
- **Cap working memory**: long agent loops blow the context window. Keep a rolling summary
  in state and drop stale intermediate detail.
- **Cite sources** from semantic retrieval so answers are auditable and the Safety Gate can
  screen retrieved (possibly injected) content before it reaches the model.

## Choosing a store

- **pgvector** — default when the app already runs Postgres. One system to operate; semantic
  memory sits next to relational data. Good to a few million vectors.
- **Qdrant** — purpose-built vector DB; reach for it at large scale / high QPS, or when you
  want advanced filtering and payload indexing beyond what pgvector comfortably gives.
- **Redis** — working/session memory and caching; fast, ephemeral. Pairs with a vector
  store, not a replacement for one.
- **Letta** — managed long-term agent memory when persistent, self-editing memory across
  sessions is a first-class product requirement and you'd rather not build the curation
  loop yourself.
- **LlamaIndex / Haystack** — when the *ingestion* side (loaders, parsers, chunking
  strategies over a real document corpus) is the hard part, not just storage.

Rule of thumb: start with **pgvector + Redis** unless an answer to the interview
(scale, latency, managed-memory need) points elsewhere. Don't add a second vector DB you
don't yet need.

## Keeping docs/context fresh

Memory holds what the system has learned; **Context7** (MCP server) covers the other half —
current external library/framework docs. For agents that write code or answer
framework questions, give them Context7 so they pull today's API surface instead of relying
on stale embeddings of old docs. Treat library docs as something to *fetch fresh*, not
something to bake into semantic memory where it silently rots across version bumps.
