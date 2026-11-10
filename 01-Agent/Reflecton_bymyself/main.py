from agent import reflection_loop,build_tools_registry, create_llm


def main():
    tools = build_tools_registry()
    llm = create_llm()
    task = "请计算233*2333，并返回结果字符串长度"
    print("="*80)
    print(f"User>> {task}")
    print("="*80)
    output = reflection_loop(task=task, llm=llm, tools=tools, verbose=True)
    print("="*80)
    print(f"Final Answer>> {output}")
    print("="*80)





if __name__ == "__main__":
    main()
    