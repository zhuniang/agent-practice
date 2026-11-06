from typing import Callable
from agent import Tool, executor, ORDINARY_SYSTEM_PROMPT, PLANNER_SYSTEM_PROMPT

def _parse_plan(content: str):
    return [line.strip("- ").strip() for line in content.splitlines() if line.strip()]

def _plan(task: str,llm: Callable[[str, str], str]) -> str:
    prompt = (
        f"将下面的任务分成3-7步，每行只返回一个步骤"
        f"Task:{task}"
    )
    content = llm(prompt, PLANNER_SYSTEM_PROMPT)
    return content


def plan_and_executor(task: str,llm: Callable[[str, str], str], tools: dict[str, Tool], max_replan_step: int = 3, verbose: bool = False,) -> str:
    step_plan = _plan(task, llm)
    steps = _parse_plan(step_plan)
    state = {}

    for attempt in range(max_replan_step+1):
        for i, step in enumerate(steps, 1):
            try:
                if verbose:
                    print(f" --- Planner Step {i} : {step} --- ")
                print(f" ---Executor Step {i}---")
                exec_res = executor(step=step, tools= tools, llm= llm, state=state)
                
                if verbose:
                    print(f" --- Executor Answer : {exec_res} --- ")
                state[f"attempt{attempt}_step{i}"] = exec_res
            except Exception as e:
                if attempt == max_replan_step:
                    return "超出重规划次数"

                replan_prompt =(
                    f"任务：{task}\n"
                    f"失败步骤：{step}\n"
                    f"之前执行状态{state}\n"
                    f"ERROR: {e}\n"
                    "请重新规划计划。"
                )
                replan = _plan(replan_prompt, llm)
                steps = _parse_plan(replan)
                break
        else:
            summary_prompt = f"Summarize final result based on: {state}"
            return llm(summary_prompt, ORDINARY_SYSTEM_PROMPT)
    return "超出重规划次数"










