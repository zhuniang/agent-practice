from typing import Callable
from .prompt import build_evaluation, EVALUATOR_SYSTEM_PROMPT, parse_evaluation
from .base import Evaluation
def evaluator(task: str, llm: Callable[[str, str], str], output: str) -> Evaluation:
    success = None
    score = 0
    feedback = None
    prompt = build_evaluation(task=task, output=output)
    content = llm(prompt,EVALUATOR_SYSTEM_PROMPT)
    success, score, feedback = parse_evaluation(content)
    return Evaluation(
        success=success,
        score=score,
        feedback=feedback
    )
