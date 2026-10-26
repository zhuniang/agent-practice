import json

from tools import TOOLS_REGISTRY
from llm.llm import call_llm,append_assistant,print_message
from openai import OpenAI
def _exect_func(func, parameters:dict) -> str:
    """内部执行函数，返回结果字符串

    Args:
        name (str): _description_
    
    Returns:
        str: _description_
    """
    if not func:
        return f"没有这个函数，请重新调用"
    try:
        return str(func(**parameters))
    except Exception as e:
        return f"ERROR: {e}"

def call_llm_with_tools(client: OpenAI, messages: list[dict], model: str):
    msg = call_llm(client= client, messages= messages, model= model)
    if not msg.tool_calls:
        return msg
    for tc in msg.tool_calls:
        func = TOOLS_REGISTRY.get(tc.function.name)
        arguments = json.loads(tc.function.arguments)
        res = _exect_func(func= func, parameters= arguments)
        messages.append({
            "role": "tool",
            "content": res,
            "tool_call_id": tc.id
        })
        print_message(messages[-1])
    final_res = call_llm(client=client, messages= messages, model= model)
    return final_res
