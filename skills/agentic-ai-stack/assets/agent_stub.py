"""Agent stub template.

Copy per role into src/agents/<role>.py. Each agent has:
- ONE clear responsibility (stated in the system prompt)
- a SCOPED tool list (only what its permission row in agent-team.md allows)
- the tracing wrapper applied to every call

Read-only roles (Planner, Researcher, Reviewer) must be given NO write/execute tools.
Enforce least privilege here, not just in the prompt text.
"""

from observability.tracing import traced
from tools.mcp_client import tools_for

# TODO: swap for your chosen agent SDK (PydanticAI / OpenAI Agents SDK / Claude Agent SDK)
from your_agent_sdk import Agent

ROLE = "planner"  # TODO: set the role name

SYSTEM_PROMPT = """\
You are the {role} agent.

Responsibility: <ONE sentence — if you need two, split this into another agent>.

You may ONLY use the tools provided. You do not have write or execute access.
Stay within your role; hand anything outside it back to the orchestrator.
""".format(role=ROLE)


def build_agent() -> Agent:
    return Agent(
        model="claude-opus-4-8",  # TODO: pick model per role; cheaper models for simple roles
        system_prompt=SYSTEM_PROMPT,
        tools=tools_for(ROLE),  # scoped: returns only this role's allowed tools
    )


@traced(name=f"agent.{ROLE}")
def run(state: dict) -> dict:
    """Invoked as a node by the orchestrator graph. Returns updated state."""
    agent = build_agent()
    # TODO: pull this role's input from state, call the agent, write result back
    result = agent.run(state["task"])
    return {**state, f"{ROLE}_output": result}
