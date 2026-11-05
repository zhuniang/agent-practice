from agent import react_loop, Tool
from typing import Any, Callable
def executor(step: str, llm: Callable[[str], str], tools: list[str, Tool], state: dict[str, Any]) -> str:
    try: 
        content = "\n".join(f"- {k}: {v}" for k, v in state.items())
        question = (
            f"只完成以下步骤：\n{step}\n\n"
            f"先前的执行结果：\n{content}\n\n"
            "当需要时使用工具，回答最终结果简洁明了"
        )
        step_res = react_loop(question=question, llm=llm, tools=tools)
        return step_res
    except Exception as e:
        return f"步骤{step}执行失败{e}"

    

