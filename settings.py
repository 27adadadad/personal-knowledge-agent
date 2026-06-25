from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    data_dir: str | None = None

    dashscope_api_key: str | None = None

    chat_api_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/chat/completions"
    chat_model_name: str = "qwen-plus"
    chat_request_timeout: int = 60

    embedding_api_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1/embeddings"
    embedding_model_name: str = "text-embedding-v4"
    embedding_request_timeout: int = 60

    vector_search_top_k: int = 3
    min_similarity_score: float = 0.3

    max_retries: int = 3
    retry_sleep_seconds: int = 2


settings = Settings()