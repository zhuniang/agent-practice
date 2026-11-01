from agent import create_llm
from agent import Tool
from typing import Callable
HistoryItem = tuple[str, str, str, str]
from agent import build_prompt,parse_action,_print_tool_messages
def react_loop(
    question: str,
    tools: dict[str,Tool],
    llm : Callable[[str], str],
    max_steps: int = 6
) -> str:
    history: tuple[HistoryItem] = []
    for step in range(1,max_steps+1):
        print(f"\n--- Step {step} ---")
        prompt = build_prompt(question=question,history=history,tools=tools)
        content = llm(prompt)
        if "Final_Answer:" in content:
            for line in content.splitlines():
                if line.startswith("Final_Answer:"):
                    answer = line.split("Final_Answer:")[1].strip()
                    return answer
        action,action_input,thought = parse_action(content)
        observation = tools.get(action).run(action_input)
        _print_tool_messages(action_input=action_input,action=action,observation=observation)
        history.append((thought,action,action_input,observation))
    return f"到达最大轮数"

