from typing import Callable
from .prompt import build_reflection_prompt, REFLECTOR_SYSTEM_PROMPT, parse_reflection
MAX_REFLECTION_LEN = 400

def reflector(task: str, 
    llm: Callable[[str, str], str], 
    feedback: str, 
    score: float, 
    output: str, 
    reflections:list[str],
):
    
    prompt = build_reflection_prompt(output=output, score=score, reflections=reflections, feedback=feedback)
    content = llm(prompt, REFLECTOR_SYSTEM_PROMPT)
    reflection = parse_reflection(content)
    if len(reflection) > MAX_REFLECTION_LEN:
        reflection = reflection[:MAX_REFLECTION_LEN]+"..."
    return reflection



def trim_refelctions(reflections: list[str], max_items: int = 5, max_char_per_item: int = 500) -> list[str]:
    trimmed_reflections =[reflection[:max_char_per_item]  for reflection in reflections[-max_items:]]
    seen_set: set[str] = set()
    deduped = []
    for trimmed_reflection in trimmed_reflections.reverse():
        key = trimmed_reflection[:80].lower()
        if key not in seen_set:
            seen_set.add(key)
            deduped.append(trimmed_reflection)
    return deduped.reverse()
        
          


    
    
    