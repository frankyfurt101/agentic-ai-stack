# HTR Orchestration Mode (Hypothesis-Tree Refinement)

An **alternative to the default Phase-3 loop** for *optimization-shaped* goals. The default
loop (`plan → code → review/test → loop-until-clean`) is linear: each retry largely discards
the last attempt. HTR keeps a **tree of hypotheses** where evidence and lessons from every
branch — including failed ones — compound, so later attempts start smarter. Adapted from
Arbor (RUC-NLPIR + Microsoft Research), which reported ~2.5× the held-out gains of a
single-agent coding loop on the same budget.

## When to use HTR vs. the default loop

Use HTR **only** when the goal has a **measurable target and a held-out evaluation**:

- ✅ "Make this faster / more accurate / cheaper" — model/algorithm tuning, harness/perf
  engineering, data-synthesis quality, retrieval@k, eval-score climbing.
- ✅ Long-horizon, many-attempt search where attempts should learn from each other.
- ❌ A specific feature or bugfix with a known correct answer → use the **default linear
  loop**. There's nothing to search; a hypothesis tree is overhead.
- ❌ No measurable metric / no held-out set → you can't run HTR's merge gate, so don't.

If you can't name the metric and the held-out set before starting, you're not ready for HTR.

## Role mapping (reuse the existing team)

HTR introduces no new agents — it re-wires the ones you have:

| HTR role | Maps to | Notes |
|---|---|---|
| **Coordinator** | **You (main session)** | Holds the tree, picks the frontier, decides merge/prune. Same "routes, not hands" rule as default mode. |
| **Executor** | `aas-coder` with `isolation: "worktree"` | One hypothesis = one worktree = one branch. Never share a worktree across hypotheses. |
| **Margin gate** | `aas-tester` | Scores the candidate on the **held-out** eval; reports the metric, not a pass/fail. |
| **Insight backprop** | `aas-memory-curator` | Abstracts *why* a branch won/lost into the node + project memory, so later ideas start smarter. |
| **Hypothesis source** | `aas-researcher` / `aas-planner` | Proposes 1–3 new hypotheses *grounded in accumulated insights*, not blank-slate. |
| **Safety / Ops gates** | `aas-safety-gate`, `aas-ops` | Unchanged. A merge that touches anything irreversible still goes through the gate; deploys stay human-approved. |

## The idea tree

Maintain it as a lightweight artifact the Coordinator owns. **Pick storage by run size:** for
a real multi-day / multi-session optimization run, use a diffable file in the repo
(`.arbor/tree.json`) so it survives restarts and you can inspect it; for a short in-session
search, hold it in project memory via `aas-memory-curator` rather than introducing a new file
convention. Either way it has three depths:

- **Depth 0 — Root:** the objective, the metric, the held-out eval definition, and global
  insights accumulated so far.
- **Depth 1 — Directions:** high-level research directions ("quantize the model", "rewrite
  the hot loop", "rerank retrieval").
- **Depth 2+ — Methods:** concrete, implemented-and-tested changes under a direction.

Each node tracks: `hypothesis`, `status` (`pending` | `running` | `done` | `merged` |
`pruned`), `metric` (held-out score), and `insight` (the abstracted lesson). Children
**refine, correct, or extend** what the tree already learned.

## The six-step cycle

Repeat until a stop condition fires:

1. **Observe** — Re-ground yourself: read the active frontier, the ancestor insights, the
   recent evidence, and the current best artifact. (This is the whole point — you read the
   *tree*, not just the last attempt.)
2. **Ideate** — Dispatch `aas-researcher`/`aas-planner` to propose **1–3** hypotheses
   conditioned on the tree's insights. Each must be a concrete, testable change with an
   expected metric move. Add them as `pending` nodes.
3. **Select** — Pick the single highest-priority `pending` node. **Balance exploit vs.
   explore**: extend the current best direction *unless* an unresolved alternative is
   cheaper to falsify or higher-upside. This judgment is yours as Coordinator.
4. **Dispatch** — Dispatch one `aas-coder` with `isolation: "worktree"` to implement *only*
   that hypothesis in its own worktree. Give it a tight, self-contained prompt: the
   hypothesis, the files, the metric, and that it must not touch the held-out eval.
5. **Backpropagate** — Dispatch `aas-tester` to score the candidate on the **held-out** set.
   Then dispatch `aas-memory-curator` to abstract the lesson (*why* the number moved) and
   write it back to the node **and to ancestor nodes / project memory** so later ideas
   inherit it.
6. **Decide** — **Merge only if the candidate clears a configurable margin** over the current
   best on held-out data (guards against noise and overfitting). Otherwise **prune** the
   worktree. Then: continue (next cycle), or **stop**.

```
Observe ──> Ideate ──> Select ──> Dispatch ──> Backpropagate ──> Decide ──┐
   ^                                                                       │
   └───────────────────────────────────────────────────────────────────  ┘
```

## Discipline specific to HTR

- **Held-out integrity is the load-bearing guardrail.** The Executor must never see or be
  able to run the held-out eval — otherwise the agent optimizes the metric, not the goal
  (reward hacking). Keep the held-out set out of the worktree; only `aas-tester` touches it.
- **One hypothesis per worktree.** Mixing two changes in a branch makes the evidence
  uninterpretable — you can't backpropagate a clean lesson. `isolation: "worktree"` exists
  for exactly this; failed branches are discarded by dropping the worktree.
- **Merge needs a margin, not just a win.** A +0.1% bump inside eval noise is not a win.
  Set the margin from the eval's variance before you start.
- **Backprop is mandatory, not optional.** If you skip step 5's insight write-back, HTR
  degrades into the linear loop with extra ceremony — the compounding is the entire benefit.
- **Cap the breadth and depth.** 1–3 hypotheses per Observe; a max frontier width and tree
  depth. Unbounded ideation burns the budget on tangents.
- **Trace it.** Log each node's hypothesis, cost, and held-out delta to your tracing layer
  (Langfuse/Phoenix) so the search itself is auditable and you can see cost-per-gain.

## Stop conditions

Stop when **any** holds: budget exhausted; **N consecutive cycles** fail to clear the margin
(plateau); the target metric is reached; or the frontier is empty and no new hypotheses
survive triage. Report the best artifact, its held-out metric, and the surviving insight
trail.

## Integration note

Arbor ships both a native CLI runtime (`RUC-NLPIR/Arbor`, with dashboard/checkpoints/
protected eval) and a loadable skill suite (`/arbor-research-agent`) for Codex/Claude Code.
This doc reimplements the *pattern* on the `aas-*` team so it composes with the rest of the
stack (tracing, safety gate, memory). For a heavy, standalone optimization run with protected
evaluation, the upstream CLI is more complete — "if you can run the CLI, use the CLI." Use
this mode when the optimization is one phase of a larger build the rest of the team owns.
