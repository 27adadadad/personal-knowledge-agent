import requests

from agent_config import (
    QWEN_API_URL,
    QWEN_MODEL_NAME,
    QWEN_REQUEST_TIMEOUT
)


def ask_qwen(messages, api_key):
    headers = {
        "Authorization":"Bearer "+ api_key,
        "Content-Type":"application/json"
    }

    data = {
        "model":QWEN_MODEL_NAME,
        "messages":messages,
        "temperature":0.2,
        "max_token":200
    }

    response = requests.post(
        QWEN_API_URL,
        headers= headers,
        json=data,
        timeout=QWEN_REQUEST_TIMEOUT
    )

    response.raise_for_status()

    result = response.json()

    answer = result["choices"][0]["message"]["content"]
    usage = result.get("usage", {})

    return answer ,usage


def ask_qwen_with_tools(messages, tools, api_key):
    headers = {
        "Authorization":"Bearer "+ api_key,
        "Content-Type":"application/json"
    }

    data = {
        "model":QWEN_MODEL_NAME,
        "messages":messages,
        "tools":tools,
        "tool_choice":"auto",
        "temperature":0.2,
        "max_tokens":500
    }

    response = requests.post(
        QWEN_API_URL,
        headers= headers,
        json=data,
        timeout = QWEN_REQUEST_TIMEOUT
    )

    response.raise_for_status()

    result  = response.json()

    message = result["choices"][0]["message"]
    usage = result.get("usage", {})

    return message, usage
