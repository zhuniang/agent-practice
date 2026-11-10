from .base import Tool
REACT_SYSTEM_PROMPT = (
    "你是一个ReAct智能体，帮助用户解决问题"
    "每次回复仅输出一轮内容，(Thought+Action+Action Input 或 Thought+Final Answer)"
    "需要时调用工具，用自然语言回答，语言和问题一致。"
)
EVALUATOR_SYSTEM_PROMPT = (
    "你是一名评估员。判断智能体的输出是否完全满足任务要求。"
    "用自然语言回答，语言和问题一致。"
    "严格按照以下格式回复（不要额外增加内容）：\n"
    "Success: yes | no"
    "Score: <0.0到1.0之间的浮点数>"
    "Feedback: <简洁评价；说明存在的问题或缺漏>"
)
REFLECTOR_SYSTEM_PROMPT = (
    "你是反思者。根据评估反馈，写出一条简短的改进策略，供智能体在下一次尝试时使用（最多120词）。"
    "重点关注：工具选择、格式、约束条件、缺失步骤。不要重复答案。"
    "以单行形式回复："
    "Reflection: <你的策略文字>"
)
ORDINARY_SYSTEM_PROMPT = (
    "你是一个乐于助人的助手"
    "用自然语言回答，语言和问题一致。"
)
def build_prompt(question: str, tools: dict[str, Tool], history: list) -> str:
    tools_name = '['+ ", ".join(tools.keys()) +']'
    print(f"tools_name: {tools_name}")
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



def build_evaluator_prompt(task: str, output: str) -> str:
    return "\n".join(
        [
            f"Task: {task}",
            "",
            "Agent output:",
            output,
        ]
    )
    
def build_reflector_prompt(
    task: str,
    output: str,
    feedback: str,
    score: float,
    reflections: list[str],
) -> str:
    lines = [
        f"Task: {task}",
        f"Score: {score}",
        f"Feedback: {feedback}",
        "",
        "Agent output:",
        output,
    ]
    if reflections:
        lines += ["", "Prior refections (avoid duplcating):"]
        for i, r in enumerate(reflections, 1):
            lines.append(f"{i}. {r}")
    return "\n".join(lines)


def parse_evaluation(text: str) -> tuple[bool, float, str]:
    success = False
    score = 0.0
    feedback = text.strip()
    for line in text.splitlines():
        lower = line.lower()
        if lower.startswith("success:"):
            val = line.split(":", 1)[1].strip().lower()
            success = val in ("yes", "true", "1", "成功", "是")
        elif lower.startswith("score:"):
            try:
                score = float(line.split(":", 1)[1].strip())
            except ValueError:
                score = 0.0
        elif line.startswith("Feedback:"):
            feedback = line.split("Feedback:", 1)[1].strip()
    score = max(0.0, min(1.0, score))
    return success, score, feedback

def parse_reflection(text: str) -> str:
    for line in text.splitlines():
        if line.startswith("Reflection:"):
            return line.split("Reflection", 1)[1].strip()
    return text.strip()[:500]

