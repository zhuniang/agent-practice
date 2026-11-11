from .base import Tool
REACT_SYSTEM_PROMPT = (
    "你是一个ReAct智能体，帮助用户解决问题"
    "每次回复仅输出一轮内容，(Thought+Action+Action Input 或 Thought+Final Answer)"
    "需要时调用工具，用自然语言回答，语言和问题一致。"
)
EVALUATOR_SYSTEM_PROMPT = (
    "你是一个评估员，请评估智能体的回答是否满足要求。"
    "用自然语言回答，语言和问题一致。"
    "回答严格按照以下格式（不要添加额外内容）\n"
    "Success: <yes|no>\n"
    "Score: <根据回答进行打分，分数区间0-1小数>\n"
    "Feedback: <根据回答给出反馈>\n"
)
REFLECTOR_SYSTEM_PROMPT = (
    "你是一个反思者，写出一条简短的改进策略，供智能体在下一次尝试时使用（最多120词）。"
    "关注重点：工具调用，返回格式，约束条件，缺失步骤。"
    "用自然语言回答，语言和问题一致。"
    "以单行形式回复：\n"
    "Reflection: <给出的改进策略>"
)
def build_prompt(question: str, tools: dict[str, Tool], history: list, reflections: list[str]) -> str:
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
    if reflections:
        lines += ["", "Past reflections (strategy memory from failed attempts):"]
        for i, r in enumerate(reflections, 1):
            lines.append(f"{i}. {r}")
    lines.append("")
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

def build_evaluation(task: str, output: str):
    return "\n".join([
        f"Task(任务): {task}",
        f"Agent Output(智能体输出): {output}"
    ])

def parse_evaluation(output: str) -> tuple[str, float, str]:
    success = False
    score = 0.0
    feedback = None
    for line in output.splitlines():
        if line.startswith("Success:"):
            val = line.split("Success:",1)[1].strip()
            success = val in ("yes","是","成功","true","True")
        if line.startswith("Score:"):
            try:
                score = float(line.split("Score:", 1)[1].strip())
            except ValueError:
                score = 0.0
        if line.startswith("Feedback:"):
            feedback = line.split("Feedback:",1)[1].strip()
    score = max(0.0, min(1.0, score))
    return success, score, feedback

def build_reflection_prompt(task: str, output: str, score: float, feedback: str, reflections: list[str]):
    line = [
        f"Task: {task}",
        f"Agent Output: {output}",
        f"Evaluation Score: {score}",
        f"Feedback: {feedback}",
        f"之前的反思，不要重复生成"
    ]
    for i, j in enumerate(reflections, 1):
        line.append(f"{i}.: {j}")
    return "\n".join(line)

def parse_reflection(output: str) -> str:
    for line in output.splitlines():
        if line.startswith("Reflection:"):
            return line.split("Reflection", 1)[1].strip()
    return output[:500]        


