"""提示词生成和解析"""
from .tools.base import Tool
def build_prompt(question: str, history: list, tools: dict[str,Tool]) -> str:
    tools_name = "["+", ".join(tools.keys())+"]"
    tools_description = "\n".join(f"{t.name}: {t.description}" for t in tools.values())
    lines = [
        "你借助工具完成任务，每一轮严格使用此格式：",
        "Thought: ...",
        f"Action: 为{tools_name}中的一个工具",
        "Action_Input: ...",
        "在你能回答时结束",
        "Final_Answer: ...",
        "",
        "重要提示：每次回复仅输出一轮内容。在收到工具返回的观测结果前，不要给出最终答案。",
        f"可用的工具{tools_name}",
        "工具介绍：",
        tools_description,
        "",
        f"问题：{question}",
        ""
    ]
    for thought, action, action_input, observation in history:
        lines += [
            f"Thought: {thought}",
            f"Action: {action}",
            f"Action_Input: {action_input}",
            f"Observation: {observation}",
            "",
        ]
    return "\n".join(lines)

def parse_action(text: str) -> tuple[str|None,str|None,str|None]:
    """只解析第一轮的thought和action"""
    action = None
    action_input = None
    thought = None
    seen_thought = False
    lines = text.splitlines()
    for line in lines:
        if line.startswith("Thought:"):
            if not seen_thought:
                thought = line.split("Thought:")[1].strip()
                seen_thought = True
            else :
                break
        if line.startswith("Action:"):
            action = line.split("Action:")[1].strip()
        if line.startswith("Action_Input:"):
            action_input = line.split("Action_Input:")[1].strip()
    return action,action_input,thought
    



