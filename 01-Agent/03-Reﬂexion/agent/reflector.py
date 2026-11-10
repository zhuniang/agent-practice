from typing import Callable
from .prompt import build_reflector_prompt, REFLECTOR_SYSTEM_PROMPT, parse_reflection
MAX_REFLECTION_LEN = 400



def reflect(
    task: str,
    output: str,
    feedback: str,
    score: float,
    reflections: list[str],
    llm: Callable[[str, str], str]
) -> str:
    """Reflection：根据评估反馈生成可复用的改进策略文本。"""
    prompt = build_reflector_prompt(task=task, output=output, score=score, reflections=reflections, feedback=feedback)
    raw = llm(prompt, REFLECTOR_SYSTEM_PROMPT)
    text = parse_reflection(raw)
    if len(text) > MAX_REFLECTION_LEN:
        text = text[:MAX_REFLECTION_LEN] + "..."
    return text

def trim_reflections(
    reflections: list[str],
    max_items: int = 5,
    max_chars_per_item: int = 400,
) -> list[str]:
    """限制条数与长度，只保留最近的高信息密度条目。"""
    trimmed = [r[:max_chars_per_item] for r in reflections[-max_items:]]
    seen: set[str] = set()
    deduped: list[str] = []
    for r in reversed(trimmed):
        key = r[:80].lower()
        if key in seen:
            continue
        seen.add(key)
        deduped.append(r)
    deduped.reverse()
    return deduped
