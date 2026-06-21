import os
import time
import requests

from agent_config import (
    EMBEDDING_API_URL,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_REQUEST_TIMEOUT
)

MAX_RETRIES = 3
RETRY_SLEEP_SECONDS = 2

def embed_text(text):
    api_key = os.getenv("DASHSCOPE_API_KEY")

    if api_key is None:
        print("没有找到 DASHSCOPE_API_KEY")
        raise SystemExit

    headers = {
        "Authorization":"Bearer " + api_key,
        "Content_Type":"application/json"
    }

    data = {
        "model":EMBEDDING_MODEL_NAME,
        "input":text
    }

    last_error = None

    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                EMBEDDING_API_URL,
                headers=headers,
                json=data,
                timeout=EMBEDDING_REQUEST_TIMEOUT
            )

            response.raise_for_status()

            result = response.json()
            embedding = result["data"][0]["embedding"]

            return embedding

        except requests.RequestException as error:
            last_error = error

            print("Embedding 请求失败，正在重试：", attempt + 1, "/", MAX_RETRIES)
            print("错误信息：", error)

            time.sleep(RETRY_SLEEP_SECONDS)

    raise last_error


def embed_texts(texts):
    embeddings = []

    for text in texts:
        embedding = embed_text(text)
        embeddings.append(embedding)

        print("向量长度：", len(embedding))

    return embeddings
