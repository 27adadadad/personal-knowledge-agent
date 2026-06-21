import os
import requests

from rag_files import load_knowledge
from vector_index import get_or_build_vector_index, vector_search
from qwen_client import ask_qwen
from rag_history import save_rag_history


def build_context(results):
    chunks=[]

    for result in results:
        chunks.append(result["chunk"])

    context = "\n\n".join(chunks)

    return context


def build_messages(question, context):
    messages = [
        {
            "role":"system",
            "content": (
                "你是个人知识库问答助手。"
                "只能根据用户消息中的【资料】回答问题，不能使用资料外的常识或自行补充内容。"
                "如果资料不足以回答，必须明确回答：资料中未提供相关信息。"
                "回答应简洁、准确。"
            )
        },
        {
            "role":"user",
            "content":"资料：\n" + context + "\n\n问题：\n" + question
        }
    ]

    return messages

def main():
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if api_key is None:
        print("没有找到 DASHSCOPE_API_KEY")
        raise SystemExit

    chunks = load_knowledge()
    vector_index = get_or_build_vector_index(chunks)


    question = input("请输入你的问题：").strip()

    if question == "":
        print("问题不能为空")
        return

    results = vector_search(question, vector_index)

    print("检索结果：")

    for result in results:
        print("chunk 编号：", result["chunk_id"])
        print("相似度分数：", result["score"])
        print("内容：", result["chunk"])
        print("-" * 30)

    context = build_context(results)
    messages = build_messages(question, context)

    try:
        answer, usage = ask_qwen(messages, api_key)

        print("模型回答：")
        print(answer)

        print("-" * 30)
        print("总 token：", usage.get("total_tokens", 0))

        save_rag_history(question, results, answer, usage)

    except requests.RequestException as error:
        print("请求失败：", error)


if __name__ == "__main__":
    main()
