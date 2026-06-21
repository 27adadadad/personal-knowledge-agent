from rag_files import load_knowledge
from vector_index import get_or_build_vector_index, vector_search

def main():
    chunks = load_knowledge()
    vector_index = get_or_build_vector_index(chunks)

    question = input("请输入你的问题：").strip()

    if question == "":
        print("问题不能为空")
        return

    results = vector_search(question, vector_index)

    print("向量检索结果：")

    for result in results:
        print("chunk 编号：", result["chunk_id"])
        print("相似度分数：", result["score"])
        print("内容：", result["chunk"])
        print("-" * 30)


if __name__ == "__main__":
    main()
