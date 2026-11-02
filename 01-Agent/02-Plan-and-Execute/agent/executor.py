from agent import Tool,build_tool_registry,react_loop
from typing import Callable


def execute_step(
    step: str,
    state: dict[str, any],
    tools: dict[str, Tool],
    llm: Callable[[str], str],
    verbose: bool = False
) -> str:
    """以 ReAct 作为单步执行器，结合已有 state 完成当前步骤。"""
    content = "\n".join(f"- {k}: {v}" for k, v in state.items())
    question = (
        f"只完成以下步骤：\n{step}\n\n"
        f"先前的执行结果：\n{content}\n\n"
        "当需要时使用工具，回答最终结果简洁明了"
    )
    return react_loop(tools=tools, llm=llm, question=question)

        