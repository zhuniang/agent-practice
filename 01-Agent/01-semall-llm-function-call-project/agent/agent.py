import json
from openai import OpenAI
from tool import TOOLS_REGISTRY
from agent.prompt import SYSTEM_PROMPT
from llm.llm import call_llm,append_assistant
def _execute_tool(name: str, arguments: str) -> str:
    func = TOOLS_REGISTRY.get(name)
    if not func:
        return f"ERROR:unknown tool '{name}'"
    try:
        args = json.loads(arguments or "{}")
        return str(func(**args))
    except Exception as e:
        return f"ERROR: {e}"

def chat_with_tools(client: OpenAI, user_message: str, model: str = "deepseek-flash") -> str:
    """单问题问答：最多 1 次工具调用 + 1 次最终生成。"""
    messages:list[dict] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message}
    ]
    msg = call_llm(client=client,messages=messages,model=model)
    append_assistant(messages=messages,msg=msg)
    if not msg.tool_calls:
        return msg.content or ""
    for tc in msg.tool_calls:
        result = _execute_tool(tc.function.name,tc.function.arguments)
        messages.append({"role": "tool", "content": result, "tool_call_id": tc.id})
    final_msg = call_llm(client=client,messages=messages,model=model)
    print(f"Model>\t {final_msg.content or ''}")
    return final_msg.content
