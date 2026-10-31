import json
from typing import Callable
from .tools import Tool
from .prompt import build_prompt,parse_action
# history 每条为 (thought, action, action_input, observation)
HistoryItem = tuple[str, str, str, str]

def _print_tool_execution(action: str, action_input: str, observation: str):
    print("\n=======>>> Tool execution ======\n")
    print(
        json.dumps(
            {
                "action" : action,
                "action_input": action_input,
                "observation": observation
            },
            indent=2,
            ensure_ascii=False
        )
    )

def react_loop(
    question: str,
    tools: dict[str, Tool],
    llm : Callable[[str], str],
    max_steps: int = 6
) -> str:
    history: list[HistoryItem] = []
    for step in range(1,max_steps+1):
        print(f"\n--- Step {step} ---")
        prompt = build_prompt(question=question,history=history,tools=tools)
        content = llm(prompt)
        action, action_inputs = parse_action(content)
        
        # 有合法工具可执行时，先执行工具；忽略同条回复里的 Final Answer
        if action and action in tools:
            thought = ""
            for line in content.splitlines():
                if line.startswith("Thought:"):
                    thought = line.split("Thought:")[1].strip()
                    break
            observation = tools[action].run(action_inputs or "")
            _print_tool_execution(action=action,action_input=action_inputs,observation=observation)
            history.append((thought,action,action_inputs or "",observation))
            continue
        if "Final Answer:" in content:
            answer = content.split("Final Answer:", 1)[1].strip()
            print(f"\n=====> Model>\t {answer}\n")
            return answer
        obs = f"ERROR: invalid Action. Must be one of {list(tools.keys())}."
        _print_tool_execution(action or "", action_inputs or "", obs)
        history.append(("", action or "", action_inputs or "", obs))
    
    return "Failed: max steps exceeded."
