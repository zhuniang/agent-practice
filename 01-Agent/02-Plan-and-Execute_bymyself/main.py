from agent import react_loop, build_tools_registry, create_llm, plan_and_executor



def main():
    question = "请计算233*2333，并返回结果字符串的长度，同时返回当前时间。"
    tools = build_tools_registry()
    llm = create_llm()
    print("="*88)
    print(f"User>> {question}")
    print("="*88)
    print()
    fianl_answer = plan_and_executor(task=question, tools = tools, llm = llm, verbose=True)

    print(f"最终结果：{fianl_answer}")


if __name__ == "__main__":
    main()

