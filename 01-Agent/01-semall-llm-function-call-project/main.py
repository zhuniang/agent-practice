from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()

from agent.agent import chat_with_tools

def main():
    api_key = os.environ.get("API_KEY")
    base_url = os.environ.get("BASE_URL")
    if not api_key:
        raise ValueError("未找到API_KEY，请在 .env 文件中配置。")
    if not base_url:
        raise ValueError("未找到BASE_URL，请在 .env 文件中配置。")
    client = OpenAI(
        api_key=api_key,
        base_url=base_url,
    )
    print("="*60)
    print("LLM Function Calling 小工程")
    print("输入 'exit' 或 'quit' 退出")
    print("="*60)

    while True:
        try:
            user_input = input("\n请输入问题:\n").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n再见！")
            break
        if not user_input:
            continue
        if user_input in ("quit","exit"):
            print("\n再见！")
            break
        print("\n\n")
        print("*" * 60)
        print(f"User>\t {user_input}")
        print("*" * 60)
        answer = chat_with_tools(client=client,user_message=user_input)
        print("\n\n")
        print("=" * 60)
        print(f"Assistant>\t {answer}")
        print("*" * 60)
if __name__ == "__main__":
    main()