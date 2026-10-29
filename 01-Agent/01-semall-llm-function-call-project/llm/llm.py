import os
import json
from openai import OpenAI
from tool import TOOLS
def print_message(messages):
    """格式化打印单条消息,去除NULL"""
    if hasattr(messages,"model_dump"):
        data = messages.model_dump(exclude_none=True)
    elif isinstance(messages,dict):
        data = {k:v for k,v in messages.items() if v is not None}
    else :
        data = messages
    print(json.dumps(data,indent=2,ensure_ascii=False))
  
def print_messages(messages: list):
    for i,msg in enumerate(messages):
        role = msg.get("role") if isinstance(msg,dict) else getattr(msg,"role",None)
        print(f"===第{i}条：role:{role}===")
        print_message(msg)

def call_llm(client: OpenAI, messages: list[dict], model: str):
    print_messages(messages)

    resp = client.chat.completions.create(
        model=model,
        messages=messages,
        tools=TOOLS,
    )
    msg = resp.choices[0].message
    print("\n=== LLM response ===\n")
    print_message(msg)
    return msg

def append_assistant(messages: list[dict], msg):
    if hasattr(msg, "model_dump"):
        messages.append(msg.model_dump(exclude_none=True))
    else:
        record: dict = {"role": "assistant", "content": msg.content}
        if msg.tool_calls:
            record["tool_calls"] = [
                tc.model_dumps(exlude_none=True) for tc in msg.tool_calls
            ]
        messages.append(record)


    
