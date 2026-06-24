from agent_service import run_agent








def main():
    print("个人知识库 Agent 启动")
    print("输入“退出”结束程序")
    print("-" * 30)

    while True:
        question = input("请输入你的问题：").strip()

        if question == "":
            print("请输入有效内容")
            continue

        if question == "退出":
            print("结束")
            break

        response = run_agent(question)


        print("最终回答：")
        print(response["answer"])

        if response["sources"]:
            sources = []

            for chunk_id in response["sources"]:
                sources.append("chunk " + chunk_id)

            print("参考来源：", "、".join(sources))


        print("-" * 30)



if __name__=="__main__":
    main()
