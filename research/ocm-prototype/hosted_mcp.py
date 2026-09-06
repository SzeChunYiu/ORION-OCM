"""ADAPT the maintained official MCP SDK; only the fixed public tools are registered."""
from mcp.server.fastmcp import FastMCP
from hosted_tools import PublicTools

api = PublicTools()
server = FastMCP("ORION public native reference tools")


@server.tool()
def public_task(item_id: str) -> dict:
    """Read one released public task. Contains no gold, expected program or scores."""
    return api.invoke("public_task", item_id=item_id)


@server.tool()
def syntax_predict(tokens: list[str]) -> dict:
    """Run the identical fixed UDPipe model. Read full words through proposal_read if useful."""
    return api.invoke("syntax_predict", tokens=tokens)


@server.tool()
def syntax_check(tokens: list[str], words: list[dict] | None = None, proposal_ref: str | None = None) -> dict:
    """Check only tree structure/token binding, never gold correctness."""
    return api.invoke("syntax_check", tokens=tokens, words=words, proposal_ref=proposal_ref)


@server.tool()
def clia_synthesize(task: dict, timeout_ms: int = 5000, deadline_s: float = 15) -> dict:
    """Run cvc5 with the same full public specification and checked accepted grammar."""
    return api.invoke("clia_synthesize", task=task, timeout_ms=timeout_ms, deadline_s=deadline_s)


@server.tool()
def clia_check(task: dict, proposal: dict | None = None, proposal_ref: str | None = None,
               timeout_ms: int = 5000, deadline_s: float = 10) -> dict:
    """Validate exact grammar then independently check the public specification with Z3."""
    return api.invoke("clia_check", task=task, proposal=proposal, proposal_ref=proposal_ref,
                      timeout_ms=timeout_ms, deadline_s=deadline_s)


@server.tool()
def proposal_read(proposal_ref: str) -> dict:
    """Read a complete native result by opaque reference; no general path access."""
    return api.invoke("proposal_read", proposal_ref=proposal_ref)


@server.tool()
def memory_read() -> dict:
    """Read the actor's bounded persistent public notes."""
    return api.invoke("memory_read")


@server.tool()
def memory_write(text: str) -> dict:
    """Replace public notes, retaining them across fresh processes; maximum 1 MiB."""
    return api.invoke("memory_write", text=text)


@server.tool()
def final_submit(item_id: str, proposal_ref: str | None = None, custom_answer: dict | None = None) -> dict:
    """Commit one final output per item, by native reference OR a custom answer; no gold grading."""
    return api.invoke("final_submit", item_id=item_id, proposal_ref=proposal_ref, custom_answer=custom_answer)


if __name__ == "__main__":
    server.run(transport="stdio")
