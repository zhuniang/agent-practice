"""打印消息"""
# from  __future__ import annotations
import json

def print_messages(messages: list):
    if not messages:
        raise ValueError("messages为空")
    try:
        for i,msg in enumerate(messages,1):
            print(f"第:{i}条：")
            print_message(msg)
    except Exception as e:
        print(f"打印出错：{e}")
def print_message(msg):
    """打印单条信息，输出去除NULL"""
    if hasattr(msg,"model_dump"):
        data = msg.model_dump(exclude_none = True)
    elif isinstance(msg,dict):
        data = {k:v for k,v in msg.items() if v is not None}
    else :
        data = msg
    print(json.dumps(data, ensure_ascii=False, indent=2))

def _print_tool_messages(action: str, action_input: str, observation: str):
    
    print(json.dumps(
        {
            "action": action,
            "action_input": action_input,
            "observation": observation,
        },
        indent=2,
        ensure_ascii=False
    ))
