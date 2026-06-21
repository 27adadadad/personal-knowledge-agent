import json
import math
import hashlib

from rag_files import get_file_path
from embedding_client import embed_text, embed_texts
from agent_config import VECTOR_INDEX_FILE, VECTOR_SEARCH_TOP_K, MIN_SIMILARITY_SCORE



def cosine_similarity(vector_a, vector_b):

    dot_sum = 0
    length_a_sum = 0
    length_b_sum = 0

    for index in range(len(vector_a)):
        dot_sum += vector_a[index] * vector_b[index]
        length_a_sum += vector_a[index]*vector_a[index]
        length_b_sum += vector_b[index]*vector_b[index]

    length_a = math.sqrt(length_a_sum)
    length_b= math.sqrt(length_b_sum)

    if length_a == 0 or length_b==0:
        return 0

    return dot_sum / (length_a*length_b)


def calculate_knowledge_hash(chunks):
    parts = []

    for chunk in chunks:
        part = str(chunk["id"]) + "\n" + chunk["text"]
        parts.append(part)

    combined_text = "\n\n".join(parts)

    text_bytes = combined_text.encode("utf-8")

    hash_value = hashlib.md5(text_bytes).hexdigest()

    return hash_value



def build_vector_index(chunks):
    texts = []

    for chunk in chunks:
        texts.append(chunk["text"])

    vectors = embed_texts(texts)

    vector_index= []

    for index in range(len(chunks)):
        chunk = chunks[index]
        vector = vectors[index]

        vector_index.append({
            "chunk_id":chunk["id"],
            "chunk":chunk["text"],
            "vector":vector
        })

    return vector_index

def save_vector_index(vector_index, knowledge_hash):
    file_path = get_file_path(VECTOR_INDEX_FILE)

    index_data = {
        "knowledge_hash":knowledge_hash,
        "items":vector_index
    }

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(index_data, file, ensure_ascii=False, indent = 2)

    print("向量索引已保存：", VECTOR_INDEX_FILE)


def load_vector_index():
    file_path = get_file_path(VECTOR_INDEX_FILE)

    if not file_path.exists():
        return None

    with open (file_path, "r", encoding= "utf-8") as file:
        index_data = json.load(file)

    if not isinstance(index_data, dict):
        return None

    if "knowledge_hash" not in index_data:
        return None

    if "items" not in index_data:
        return None

    return index_data


def get_or_build_vector_index(chunks):
    current_hash = calculate_knowledge_hash(chunks)

    index_data = load_vector_index()

    if index_data is not None:
        saved_hash = index_data["knowledge_hash"]

        if saved_hash == current_hash:
            print("向量索引未过期，直接加载")
            return index_data["items"]

        print("知识库内容已变化，开始重建向量索引")

    else:
        print("向量索引不存在或格式已过期，开始构建")

    vector_index = build_vector_index(chunks)

    save_vector_index(vector_index, current_hash)

    return vector_index


def vector_search(question, vector_index):
    question_vector = embed_text(question)


    results = []

    for item in vector_index:
        score = cosine_similarity(question_vector, item["vector"])

        results.append({
            "chunk_id":item["chunk_id"],
            "chunk":item["chunk"],
            "score":score
        })

    results.sort(key=lambda item:item["score"], reverse=True)

    filtered_results= []

    for result in results:
        if result["score"]<MIN_SIMILARITY_SCORE:
            continue

        filtered_results.append(result)

    return filtered_results[:VECTOR_SEARCH_TOP_K]
