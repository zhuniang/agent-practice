import json
from typing import Callable
from .react_loop import react_loop
from .tools import Tool
from .evaluator import evaluator
from .reflector import reflector, trim_refelctions
from .prompt import parse_evaluation
def reflection_loop(
    task: str,
    llm: Callable[[str, str], str],
    tools: dict[str, Tool],
    max_react_trials: int = 4,
    max_reflection_trials: int = 4,
    max_reflections_len: int = 5,
    verbose: bool = True,

):
    reflections = []
    for trial in range(max_reflection_trials+1):

        output = react_loop(llm=llm, tools=tools, max_steps=max_react_trials,question=task, reflections=reflections)
        if verbose:
            print(f"React Output>> {output}")
        evaluator_res = evaluator(task=task, llm=llm, output=output)

        success = evaluator_res.success
        score = evaluator_res.score
        feedback = evaluator_res.feedback

        if verbose:
            evaluator_show = json.dumps({
                "success": success,
                "score": score,
                "feedback": feedback
                ,
            },indent=2,ensure_ascii=False)
            print(f"Evaluator Output>> {evaluator_show}")
        if success:
            return output
        reflection = reflector(llm=llm, task=task, feedback=feedback, output=output, reflections=reflections, score=score)
        reflections = trim_refelctions(reflections+[reflection],max_items=max_reflections_len)
        if verbose:
            print(f"This Reflection Output>> {reflection}")
        

    return "Failed: max trials exceeded."
    