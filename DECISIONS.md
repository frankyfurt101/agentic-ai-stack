# Design Decisions & Change Log

Rationale for what's in the skill and — just as important — what's deliberately *not*, so a
future rebuild doesn't re-litigate settled choices or re-add rejected ones.

## 2026-06-19 — Superpowers execution-discipline borrowings

Diffed Phase 3 against `superpowers:subagent-driven-development` + `dispatching-parallel-agents`
(v6.0.3). The skills are complementary, not competing: this skill owns design/safety/permission
scope (Phases 0–2, safety gate, typed least-privilege agents, HTR), superpowers owns execution
mechanics. Ported the four highest-value execution habits into Phase 3 (`SKILL.md` new
"Execution discipline" subsection) + `agents/aas-coder.md`:

1. **File handoffs** — task-brief / report / diff move as files; the Coder writes full detail
   to a report file and returns only status + one-line summary + commit range. Diffs generated
   from the recorded BASE commit, never `HEAD~1` (truncates multi-commit tasks). Keeps the
   controller's context from filling with pasted history.
2. **Durable progress ledger** (`.aas/progress.md`) surviving compaction — never re-dispatch a
   task the ledger marks done; trust ledger + `git log` over recollection.
3. **Per-task model selection** — cheapest model that fits, set explicitly per `Agent` call
   (omitting it inherits the expensive session model).
4. **Structured Coder status protocol** — DONE / DONE_WITH_CONCERNS / NEEDS_CONTEXT / BLOCKED,
   each with a controller handling rule (deterministic control flow). Plus a "don't pre-judge
   the review" rule and a **continuous-vs-gated reconciliation**: run continuously through
   reversible work, stop only at the gates that exist on purpose (safety VETO, Ops human
   approval, unresolvable BLOCKED).

What was *not* borrowed: superpowers' prompt-template scripts (`review-package`, `task-brief`)
are repo-specific bash helpers — the principle was ported, not the scripts.

## 2026-06-19 — Hardening pass (Arbor + Ponytail + r/AI_Agents audit)

Triggered by comparing the skill against four viral artifacts (Ponytail least-code skill, two
"production AI app / RAG" file-trees, the Arbor optimization framework) and a
practitioner thread (r/AI_Agents "Best Agentic Framework for Production"). The skill's core
thesis — *architecture over framework; a stack of layers, not one magic repo* — held up; it
**is** the consensus of that thread. These changes close the real gaps that surfaced.

### Applied — Tier 1 (high value, low cost)

1. **Tool-layer determinism principle** (`references/stack-components.md` §2). Tools are
   typed, tested, deterministic wrappers — the LLM decides *what*, the tool decides *how*.
   Model-generated code that must run goes in the sandbox (layer 4) behind a tool, never
   inlined into the loop. The single biggest gap the Reddit thread exposed.
2. **"Should this be agentic at all?" gate** (`SKILL.md` Phase 1, Step 0). Screen the goal
   *out* of agents if a deterministic workflow/platform (RPA, rules engine, existing SaaS)
   would be more reliable. The process is the durable asset, not the model.
3. **Protected held-out evaluation boundary** (`agents/aas-tester.md`). In HTR/optimization
   mode the Tester is the *only* role that touches the held-out set; the Coder/Executor must
   never see it (else it reward-hacks the metric). Load-bearing guardrail for HTR.
4. **Custom-orchestrator-on-Temporal option** (`stack-components.md` §1). A thin in-house SDK
   over Temporal/Restate is a legitimate layer-1 answer that serious prod teams keep — added
   with a "only if you have the platform muscle" caveat.
5. **Logfire** added to the evals/tracing catalog (`stack-components.md` §5) as the natural
   pairing for PydanticAI.

### Applied — Tier 2 (folded into the same pass)

6. **Reflective memory — "revise, don't replay"** (`references/memory.md`). Long-running
   agents drift when episodic memory only retrieves and never updates; the Memory Curator
   should supersede stale facts, not append contradictions. Letta named as the managed option.
7. **Deep Agents SDK (LangChain)** added to orchestration catalog as the Lang-ecosystem
   counterpart to the Claude Agent SDK for the subagents+skills pattern.
8. **HTR tree storage made size-dependent** (`references/htr-orchestration.md`): a diffable
   `.arbor/tree.json` for multi-session runs, project memory for short in-session searches.

### New in this pass — HTR orchestration mode

`references/htr-orchestration.md` (+ pointer in `SKILL.md` Phase 3, + catalog entry).
**Hypothesis-Tree Refinement**, derived from Arbor (RUC-NLPIR + Microsoft Research). An
*alternative* to the default linear loop for **optimization-shaped** goals with a measurable
held-out metric. Keeps a tree of hypotheses where evidence (incl. failures) compounds.
Six-step cycle: Observe → Ideate → Select → Dispatch → Backpropagate → Decide. Mapped onto
the existing team (main session = Coordinator, `aas-coder` in a worktree = Executor,
`aas-tester` = held-out margin gate, `aas-memory-curator` = insight backprop). Not for
feature/bugfix work and not usable without a metric + held-out set.

### Ponytail least-code preflight

`agents/aas-coder.md` gained a five-check preflight before writing new code (needs-to-exist →
stdlib → native platform → existing dependency → one-liner), with an explicit carve-out:
never trade away security / accessibility / data-loss handling / the test contract to save
lines. Fills the token-economy blind spot; same instinct as the tool-determinism principle.

## Deliberately NOT included (Tier 3 — rejected, do not re-add without new evidence)

- **Agno** — single anecdote of a prod deployment in the Reddit thread (8 agents). Fast-moving
  and unvetted; one data point doesn't justify a catalog row I'd actually recommend. Re-add
  only if multiple credible prod reports appear, and then as "emerging, prototype-validate
  first." *Status: watch, not adopt.*
- **Semantic Kernel** — real Microsoft enterprise option, but irrelevant to my Python/TS-first
  world; it would be a row I never recommend. **Add only if a .NET / Microsoft-enterprise use
  case actually shows up.**
- **Unverified self-promo from the thread** — Kognitos, NYEX, Hindsight, veris, Pipelex, Arvo,
  npcpy, OpenClaw. No independent production signal; roughly a third of that thread was
  bot/promo (a commenter flagged it and was right). **Do not let a viral thread's noise churn
  the catalog.**

## Standing principles (the through-line)

The strongest pattern across Ponytail, Arbor, and the practitioner thread is the **same
instinct**: keep the probabilistic part small and fenced, make the deterministic parts
authoritative.
- Tools = deterministic wrappers (tool layer)
- Least-code preflight = don't let the model generate what doesn't need to exist (coder)
- Held-out gate = don't let the optimizer see its own eval (HTR)
- Human approval gates on irreversible ops (guardrails) — never auto-approved
- Memory partitioned per project, never one global pool
