import time
import requests

from settings import settings


def embed_text(text):
    api_key = settings.dashscope_api_key

    if api_key is None:
        print("没有找到 DASHSCOPE_API_KEY")
        raise SystemExit

    headers = {
        "Authorization":"Bearer " + api_key,
        "Content-Type":"application/json"
    }

    data = {
        "model":settings.embedding_model_name,
        "input":text
    }

    last_error = None

    for attempt in range(settings.max_retries):
        try:
            response = requests.post(
                settings.embedding_api_url,
                headers=headers,
                json=data,
                timeout=settings.embedding_request_timeout
            )

            response.raise_for_status()

            result = response.json()
            embedding = result["data"][0]["embedding"]

            return embedding

        except requests.RequestException as error:
            last_error = error

            print("Embedding 请求失败，正在重试：", attempt + 1, "/", settings.max_retries)
            print("错误信息：", error)

            time.sleep(settings.retry_sleep_seconds)

    raise last_error


def embed_texts(texts):
    embeddings = []

    for text in texts:
        embedding = embed_text(text)
        embeddings.append(embedding)

        print("向量长度：", len(embedding))

    return embeddings
