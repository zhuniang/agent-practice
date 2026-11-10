from .log import print_messages, print_message
from .prompt import build_prompt, parse_action
from .base import Tool
from .react_loop import react_loop
from .evaluator import evaluate
from .reflector import reflect, trim_reflections
from typing import Callable
import json
# 一条历史记录：{"thought": str, "action": str, "action_input": str, "observation": str}
HISTORY_SCHEMA = dict[str, str]

def reflect_until_success(
    task: str,
    llm: Callable[[str, str], str], 
    tools: dict[str, Tool], 
    max_steps: int = 6,
    max_trials: int = 3, # 最大尝试次数
    max_reflections: int = 5, # 最大反思次数
    verbose: bool = False, # 是否打印详细信息
) -> str:
    """Reflection 主循环：Action → Evaluation → Reflection → Retry。
   
    reflections = []
    repeat until success or max_trials:
        Action: 基于 task + reflections 生成输出
        Evaluation: score, feedback = Evaluator(output)
        if success: return output
        Reflection: reflections.append(Reflector(feedback))
    """
    reflections: list[str] = []
    last_output = ""

    for trial in range(1, max_trials+1):
        last_output = react_loop(
            question=task,  
            tools=tools,
            llm=llm,
            max_steps=max_steps,
            verbose=verbose,
        )

        if verbose:
            print(f"\n--- Evaluation ---")
            print(f"Output: {last_output}")

        result = evaluate(task=task, output=last_output, llm=llm)
        if verbose:
            print(
                f"Success={result.success} Score={result.score}\n"
                f"Feedback: {result.feedback}"
            )

        if result.success:
            if verbose:
                print(f"\n>>> Success on trial {trial}")
            return last_output
        
        reflection = reflect(
            task=task,
            output=last_output,
            feedback=result.feedback,
            score=result.score,
            reflections=reflections,
            llm=llm,
        )
        reflections = trim_reflections(reflections=reflections+[reflection], max_items=max_reflections)

        if verbose:
            print(f"\n--- Reflection appended ---\n{reflection}")

    return last_output or "Failed: max trials exceeded."