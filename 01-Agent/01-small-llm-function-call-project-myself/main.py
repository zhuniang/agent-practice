from openai import OpenAI
import os
from dotenv import load_dotenv
from agent.prompt import SYSTEM_PROMPT
from agent.agent import call_llm_with_tools
from llm.llm import print_messages
load_dotenv()
MODEL = "deepseek-flash"
def main():
    messages: list[dict] = [{"role": "system", "content": SYSTEM_PROMPT}]
    base_url = os.environ.get("base_url".upper())
    api_key = os.environ.get("api_key".upper())
    if not base_url or not api_key:
        raise ValueError("缺少api_key,请在.env文件中配置") if not api_key else ValueError("缺少base_url,请在.env文件中配置")
    client = OpenAI(
        base_url=base_url,
        api_key=api_key
    )
    while True:

        user_input = input(f"请输入问题:\n")
        messages.append({"role": "user", "content": user_input})
        print_messages(messages)
        msg = call_llm_with_tools(client,messages,model=MODEL)
        if not msg.tool_calls:
            print("*"*60)
            print(f"Assistant> {msg.content}")
            print("*"*60)
        
            



if __name__ == "__main__":
    main()