import json

from agent import create_llm,react_loop,build_tool_registry


def main():
    llm = create_llm()
    tools = build_tool_registry()
    question = "请计算233*2333，并输出当前的时间和结果字符串的长度"

    print("="*60)
    print(f"工具列表{tools}")
    print("="*60)
    print("\n")
    print("="*60)
    print(f"USER>> {question}")
    print("="*60)
    print("\n")
    answer = react_loop(question=question,tools=tools,llm=llm)
    print("\n")
    print("="*60)
    print(f"ASSISTANT>> {answer}")
    print("="*60)

if __name__ == "__main__":
    main()

