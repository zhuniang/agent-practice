# import sys
from agent import build_default_tools,create_deepseek_llm,react_loop




def main() -> None:
    tools = build_default_tools()
    llm = create_deepseek_llm()
    question = "帮我计算一下233*233，并统计答案字符串有多少字符，并且打印当前时间"

    print("=" * 60)
    print("ReAct Agent 示例")
    print("可用工具：[]")
    print("=" * 60)
    print("\n")
    print("=" * 60)
    print("*" * 60)
    print(f"User>\t {question}")

    result = react_loop(question, tools, llm)

    print("\n")
    print("=" * 60)
    print(f"Assistant>\t {result}")
    print("=" * 60)


if __name__ == "__main__":
    main()