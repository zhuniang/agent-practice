from .log import  print_messages, print_message
from .prompt import build_prompt, parse_action, REACT_SYSTEM_PROMPT
from .base import Tool
from typing import Callable
import json
# 一条历史记录：{"thought": str, "action": str, "action_input": str, "observation": str}
HISTORY_SCHEMA = dict[str, str]

def react_loop(question: str, llm: Callable[[str, str], str], tools: dict[str, Tool], max_steps: int = 6) -> str:

    history: list[HISTORY_SCHEMA] = []

    for i in range(1,max_steps+1):
        print(f" --- Step {i} --- ")
        prompt = build_prompt(question=question, tools=tools, history=history)
        content = llm(prompt, REACT_SYSTEM_PROMPT)

        for line in content.splitlines():
            if line.startswith("Final Answer:"):
                return line.split("Final Answer:")[1].strip()
        thought, action, action_input = parse_action(content)
        if action is None:
            observation = "没有解析到 Action，请严格按 Thought/Action/Action Input 输出。"
        else :
            tool = tools.get(action)
            if tool is None:
                observation = f"ERROR: 工具 {action!r} 不存在，可用工具：{list(tools)}"
            else:
                try:
                    observation = str(tool.run(action_input))
                except Exception as e:
                    observation = f"ERROR: 工具执行失败: {e}"
        print("="*88)
        _print_action(thought=thought, action_input= action_input, action= action, observation=observation)
        print("="*88)
        history.append({
            "Thought": thought,
            "Action": action,
            "Action Input": action_input,
            "Observation": observation,
        })
    return "ERROR:到达最大步数"


def _print_action(thought: str, action:str, action_input:str, observation: str) -> str:
    print(json.dumps(
        {
            "Thought": thought,
            "Action": action,
            "Action Input": action_input,
            "Obserbation": observation
        },
        indent=2,
        ensure_ascii=False
    ))
