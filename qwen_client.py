import requests

from settings import settings


def ask_qwen(messages, api_key):
    headers = {
        "Authorization":"Bearer "+ api_key,
        "Content-Type":"application/json"
    }

    data = {
        "model":settings.chat_model_name,
        "messages":messages,
        "temperature":0.2,
        "max_tokens":200
    }

    response = requests.post(
        settings.chat_api_url,
        headers=headers,
        json=data,
        timeout=settings.chat_request_timeout
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
        "model":settings.chat_model_name,
        "messages":messages,
        "tools":tools,
        "tool_choice":"auto",
        "temperature":0.2,
        "max_tokens":500
    }

    response = requests.post(
        settings.chat_api_url,
        headers= headers,
        json=data,
        timeout = settings.chat_request_timeout
    )

    response.raise_for_status()

    result  = response.json()

    message = result["choices"][0]["message"]
    usage = result.get("usage", {})

    return message, usage
