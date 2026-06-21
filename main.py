from langchain_core.messages import HumanMessage, ToolMessage

from agent_graph import agent_graph
from agent_history import save_agent_history




def get_source_chunk_ids(messages):
    source_chunk_ids = []

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        lines = str(message.content).splitlines()

        for line in lines:
            if not line.startswith("[chunk "):
                continue

            if not line.endswith("]"):
                continue

            chunk_id = line[len("[chunk "):-1]

            if chunk_id.isdigit() and chunk_id not in source_chunk_ids:
                source_chunk_ids.append(chunk_id)

    return source_chunk_ids





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

        state = {
            "question":question,
            "messages":[
                HumanMessage(content=question)
            ],
            "answer":"",
            "step_count":0
        }

        result = agent_graph.invoke(state)



        print("最终回答：")
        print(result["answer"])

        source_chunk_ids = get_source_chunk_ids(result["messages"])

        if source_chunk_ids:
            sources = []

            for chunk_id in source_chunk_ids:
                sources.append("chunk " + chunk_id)

            print("参考来源：", "、".join(sources))

        save_agent_history(result)

        print("-" * 30)



if __name__=="__main__":
    main()
