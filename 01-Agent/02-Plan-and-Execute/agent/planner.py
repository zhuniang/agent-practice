from typing import Any, Callable
from .tools.base import Tool
from .llm import create_llm
from agent import execute_step

def _parse_steps(text: str) -> list[str]:
    return [s.strip("- ").strip() for s in text.splitlines() if s.strip()]

def plan(task: str, llm: Callable[[str], str]) -> list[str]:
    prompt = f"""
将task任务分成3-7步。每行只返回一个步骤。
task任务：{task}
"""
    text = llm(prompt)
    steps = _parse_steps(text)
    return steps


def plan_and_execute(
    task: str,
    llm: Callable[[str], str],
    tools: dict[str, Tool],
    max_replans: int = 2,
    verbose: bool = False,
) -> str:
    steps = plan(task, llm)
    state: dict[str, Any] = {}
    for attempt in range(1,max_replans+1):
        for i, st in enumerate(steps,1):
            if verbose:
                print(f"--- Executing step {i} 步: {st} ---")
            try:
                out = execute_step(step=st,tools=tools,llm=llm,verbose=verbose,state=state)
                state[f"step_{i}"] = out
                if verbose:
                    print(f"Result: {out}\n")
            except Exception as e:
                if verbose:
                    print(f"Step failed: {e}. Replanning...\n")

                replen_prompt =(
                    f"任务：{task}\n"
                    f"失败步骤：{st}\n"
                    f"之前执行状态{state}\n"
                    f"ERROR: {e}\n"
                    "请重新规划计划。"
                )
                replan = llm(replen_prompt)
                steps = _parse_steps(replan)
                if verbose:
                    print(f"\n --- Replanned ---")
                    for j, new_plan in enumerate(steps, 1):
                        print(f" --- Step_{j} : {new_plan} --- ")
                    print()
                break
        else:
            summary_prompt = f"Summarize final result based on: {state}"
            return llm(summary_prompt)
    return "Failed after replanning."
    
# if __name__ == "__main__":


#     print(plan("计算233*2333，并输出当前时间和结果字符串的长度", create_llm()))