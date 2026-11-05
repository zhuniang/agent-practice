from typing import Callable
from agent import Tool, executor

def _parse_plan(content: str):
    return [line.strip("- ").strip() for line in content.splitlines() if line.strip()]

def _plan(task: str,llm: Callable[[str], str]) -> str:
    prompt = (
        f"将下面的任务分成3-7步，每行只返回一个步骤"
        f"Task:{task}"
    )
    content = llm(prompt)
    return content


def plan_and_executor(task: str,llm: Callable[[str], str], tools: dict[str, Tool], max_replan_step: int = 3, verbose: bool = False,) -> str:
    step_plan = _plan(task, llm)
    steps = _parse_plan(step_plan)
    for _ in range(max_replan_step):
        state = {}
        for i, step in enumerate(steps, 1):
            try:
                if verbose:
                    print(f" --- Planner Step {i} : {step} --- ")
                print(f" ---Executor Step {i}---")
                exec_res = executor(step=step, tools= tools, llm= llm, state=state)
                
                if verbose:
                    print(f" --- Executor Answer : {exec_res} --- ")
                state[f"Step{i}"] = exec_res
            except Exception as e:
                replan_prompt = (
                    "请重新规划task，原来的规划出错"
                    f"报错原因：{e}\n"
                    f"将下面的任务分成3-7步，每行只返回一个步骤"
                    f"Task:{task}"
                )
                replan = _plan(replan_prompt, llm)
                steps = _parse_plan(replan)
                break
        else:
            summary_prompt = f"Summarize final result based on: {state}"
            return llm(summary_prompt)
    return "超出重规划次数"










