from typing import Callable
from .base import EvaluationResult
from .prompt import build_evaluator_prompt, EVALUATOR_SYSTEM_PROMPT, parse_evaluation
import re

def _rule_check(task: str, output: str) -> EvaluationResult | None:
    """
    可验证任务的规则评估（示例：21+21 且统计答案字符串字符数）。
    命中规则时返回确定结果，否则返回 None 交给模型评估。
    Args:
        task (str): _description_
        output (str): _description_

    Returns:
        EvaluationResult | None: _description_
    """
    if "21+21" not in task .replace(" ", "") and "21 + 21" not in task:
        return None
    has_sum = "42" in output
    char_ok = bool(
        re.search(r"字符数\s*[:：]\s*2\b", output)
        or re.search(r"\b2\s*个字符", output)
        or re.search(r"字符数.{0,20}2", output)
    )
    if has_sum and char_ok:
        return EvaluationResult(
            success=True,
            score=1.0,
            feedback="规则校验通过：包含 42 且明确给出答案字符串字符个数为2。",
        )
    missing = []
    if not has_sum:
        missing.append("未给出正确计算结果 42")
    if not char_ok:
        missing.append("未用 word_count 统计答案字符串「42」的字符数（应为 2）")
    return EvaluationResult(
        success=False,
        score=0.3 if has_sum else 0.0,
        feedback="规则校验未通过：" + ";".join(missing),
    )

def evaluate(
    task: str,
    output: str,
    llm: Callable[[str, str], str],
    use_rules: bool = False,

) -> EvaluationResult:
    """Evaluation：规则优先，否则由 LLM 给出成功标志、分数与批评。"""
    if use_rules:
        ruled = _rule_check(task, output)
        if ruled is not None:
            return ruled
    prompt = build_evaluator_prompt(task, output)
    raw = llm(prompt, EVALUATOR_SYSTEM_PROMPT)
    success, score, feedback = parse_evaluation(raw)
    if success and score < 0.5:
        score = 1.0
    return EvaluationResult(success=success, score=score, feedback=feedback)
