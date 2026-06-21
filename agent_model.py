import json
import os
import requests

from langchain_core.messages import(
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage
)


from agent_config import MAX_STEPS
from agent_state import AgentState
from agent_tools import search_knowledge
from qwen_client import ask_qwen_with_tools


SYSTEM_PROMPT = (
    "你是个人知识库 Agent。"
    "对于任何需要事实、概念、技术说明的用户问题，必须先调用 "
    "search_knowledge 工具检索个人知识库。"
    "第一次回答时，不得直接使用你已有的外部知识生成答案。"
    "只有收到工具结果后，才能生成最终回答。"
    "最终回答只能依据工具结果，不能补充工具结果中没有的信息。"
    "如果工具结果没有相关信息，回答：资料中未提供相关信息。"
    "如果工具结果说明检索工具暂时不可用，必须告诉用户知识库检索服务暂时不可用，请稍后再试，不能使用外部知识回答。"
)


def build_qwen_tools():
    parameters = search_knowledge.args_schema.model_json_schema()

    tools = [
        {
            "type":"function",
            "function":{
                "name":search_knowledge.name,
                "description":search_knowledge.description,
                "parameters":parameters
            }
        }
    ]

    return tools


def convert_messages_to_qwen(messages:list[BaseMessage]):
    qwen_messages = [
        {
            "role":"system",
            "content":SYSTEM_PROMPT
        }
    ]

    for message in messages:
        if isinstance(message, SystemMessage):
            qwen_messages.append({
                "role":"system",
                "content":str(message.content)
            })

        elif isinstance(message, HumanMessage):
            qwen_messages.append({
                "role":"user",
                "content":str(message.content)
            })

        elif isinstance(message, AIMessage):
            qwen_message = {
                "role":"assistant",
                "content":str(message.content or "")
            }

            if message.tool_calls:
                tool_calls = []

                for tool_call in message.tool_calls:
                    tool_calls.append({
                        "id":tool_call["id"],
                        "type":"function",
                        "function":{
                            "name":tool_call["name"],
                            "arguments":json.dumps(
                                tool_call["args"],
                                ensure_ascii=False
                            )
                        }
                    })

                qwen_message["tool_calls"]= tool_calls

            qwen_messages.append(qwen_message)

        elif isinstance(message, ToolMessage):
            qwen_messages.append({
                "role":"tool",
                "tool_call_id":message.tool_call_id,
                "content":str(message.content)
            })

    return qwen_messages


def convert_tool_calls(qwen_tool_calls):
    tool_calls = []

    for qwen_call in qwen_tool_calls:
        function = qwen_call["function"]
        arguments = function.get("arguments", "{}")

        if isinstance(arguments, str):
            args = json.loads(arguments)
        else:
            args = arguments

        if not isinstance(args, dict):
            raise ValueError("工具参数必须是字典")

        tool_calls.append({
            "name":function["name"],
            "args":args,
            "id":qwen_call["id"],
            "type":"tool_call"
        })

    return tool_calls


def model_node(state:AgentState):
    if state["step_count"]>=MAX_STEPS:
        answer = "执行轮数达到上限，已自动结束。"

        return {
            "messages":[AIMessage(content=answer)],
            "answer":answer
        }

    api_key = os.getenv("DASHSCOPE_API_KEY")

    if api_key is None:
        answer = "没有找到 DASHSCOPE_API_KEY。"

        return {
            "messages":[AIMessage(content=answer)],
            "answer":answer
        }

    qwen_messages = convert_messages_to_qwen(state["messages"])
    qwen_tools = build_qwen_tools()

    try:
        model_message, _ =ask_qwen_with_tools(
            qwen_messages,
            qwen_tools,
            api_key
        )

        content = model_message.get("content")or""
        qwen_tool_calls = model_message.get("tool_calls", [])

        if qwen_tool_calls:
            tool_calls = convert_tool_calls(qwen_tool_calls)

            return {
                "messages":[
                    AIMessage(
                        content=content,
                        tool_calls=tool_calls
                    )
                ],
                "step_count":state["step_count"]+1
            }

        answer = content or "模型没有返回有效回答。"

        return {
            "messages":[AIMessage(content=answer)],
            "answer":answer,
            "step_count":state["step_count"]+1
        }

    except (requests.RequestException, ValueError) as error:
        answer = "模型请求失败：" + str(error)

        return {
            "messages": [AIMessage(content=answer)],
            "answer": answer,
            "step_count": state["step_count"] + 1
        }
