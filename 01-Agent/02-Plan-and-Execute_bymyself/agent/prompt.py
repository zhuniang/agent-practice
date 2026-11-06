from agent import Tool
REACT_SYSTEM_PROMPT = (
    "你是一个ReAct智能体，帮助用户解决问题"
    "每次回复仅输出一轮内容，(Thought+Action+Action Input 或 Thought+Final Answer)"
    "需要时调用工具，用自然语言回答，语言和问题一致。"
)
PLANNER_SYSTEM_PROMPT = (
    "你是规划助手，根据用户的问题规划合理的计划"
    "用自然语言回答，语言和问题一致。"
)
ORDINARY_SYSTEM_PROMPT = (
    "你是一个乐于助人的助手"
    "用自然语言回答，语言和问题一致。"
)
def build_prompt(question: str, tools: dict[str, Tool], history: list) -> str:
    tools_name = '['+ ", ".join(tools.keys()) +']'
    tools_description = {t.name: t.description  for t in tools.values()}
    lines = [
        "在需要时调用以下工具，严格按照以下格式回答",
        f"工具列表: {tools_name}",
        f"工具描述: {tools_description}",
        "",
        "格式如下：",
        "Thought: ...",
        f"Action: {tools_name}为其中的一个工具",
        "Action Input: ...",
        "",
        "当觉得可以回答时，返回：",
        "Final Answer: ...",
        "",
        f"问题：{question}",
        "",
        f"上下文：",
        ""
    ]
    for step in history:
        lines += [
            f"Thought: {step['Thought']}",
            f"Action: {step['Action']}",
            f"Action Input: {step['Action Input']}",
            f"Observation: {step['Observation']}",
            "",
        ]
    return "\n".join(lines)

def parse_action(content: str) -> tuple[str | None, str | None, str | None]:
    thought = action = action_input = None

    lines = content.splitlines()
    seen_thought = False
    for line in lines:
        if line.startswith("Thought:"):
            if not seen_thought:
                thought = line.split("Thought:")[1].strip()
                seen_thought = True
            else :
                break
        if line.startswith("Action:"):
            action = line.split("Action:")[1].strip()
        if line.startswith("Action Input:"):
            action_input = line.split("Action Input:")[1].strip()
    return thought, action, action_input
