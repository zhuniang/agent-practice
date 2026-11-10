
import json

def print_message(msg):
    """输出单条消息，并去除NULL"""
    try:
        if hasattr(msg, "model_dump"):
            data = msg.model_dump(exclude_none=True)
        elif isinstance(msg,dict):
            data = {k: v for k, v in msg.items() if v is not None}
        else: data = msg
        print(json.dumps(data,ensure_ascii=False,indent=2))
    except Exception as e:
        print(f"输出单条消息出错{e}")

def print_messages(messages: list):
    """输出多条msg"""
    try:
        for i, msg in enumerate(messages, 1):
            print(f" --- 第{i}条 --- ")
            print_message(msg)
    except Exception as e:
        print(f"输出多条消息出错{e}")

    