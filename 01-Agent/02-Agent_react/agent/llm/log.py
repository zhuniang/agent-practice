"""JSON 日志工具"""
import json
def print_message(msg):
    """打印单条信息，过滤NULL"""
    if hasattr(msg,"model_dump"):
        data = msg.model_dump(exclude_none=True)
    elif isinstance(msg,dict):
        data = {k:v for k,v in msg.items() if v is not None}
    else :
        data = msg
    print(json.dumps(data,ensure_ascii=False,indent=2))


def print_messages(messages:list):
    for i,v in enumerate(messages):
        role = v.get("role") if isinstance(v,dict) else getattr(v,"role",None)
        print(f"第{i}条: role:{role}")
        print_message(msg=v)