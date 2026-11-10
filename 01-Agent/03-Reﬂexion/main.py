from agent import reflect_until_success, build_tools_registry, create_llm

def main() -> None:
    tools = build_tools_registry()
    llm = create_llm()
    task = "计算21+21，并统计结果字符串长度"
    output = reflect_until_success(llm=llm, tools=tools, task=task, verbose=True)
    print("="*60)
    print(f"User>> {task}")
    print("="*60)
    print()
    print("="*60)
    print(f"Final Answer>> {output}")
    print("="*60)


if __name__ == "__main__":
    main()