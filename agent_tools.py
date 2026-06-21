import requests

from langchain_core.tools import tool

from rag_files import load_knowledge
from vector_index import get_or_build_vector_index, vector_search

@tool
def search_knowledge(query: str) -> str:
    """回答知识性问题前必须调用，用于检索个人知识库中的相关资料。"""

    try:
        chunks = load_knowledge()

        vector_index = get_or_build_vector_index(chunks)

        results = vector_search(query, vector_index)

        if len(results) == 0:
            return "知识库中没有检索到相关资料。"

        result_texts= []

        for result in results:
            text = (
                "[chunk "
                + str(result["chunk_id"])
                + "]\n"
                + result["chunk"]
                + "\n相似度："
                + f'{result["score"]:.4f}'
            )

            result_texts.append(text)

        return "\n\n".join(result_texts)

    except requests.RequestException as error:
        print("知识库检索失败：", error)

        return "检索工具暂时不可用，无法连接 Embedding 服务，请稍后再试。"
