import json
from datetime import datetime

from langchain_core.messages import ToolMessage

from agent_config import HISTORY_FILE
from rag_files import get_data_file_path

def load_agent_history():
    file_path = get_data_file_path(HISTORY_FILE)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            history = json.load(file)

        if isinstance(history, list):
            return history

        return []

    except json.JSONDecodeError:
        print("Agent 历史记录文件损坏，已使用空记录")
        return []


def extract_tool_results(messages):
    tool_results = []

    for message in messages:
        if isinstance(message, ToolMessage):
            tool_results.append(str(message.content))

    return tool_results



def save_agent_history(result):
    history = load_agent_history()

    tool_results = extract_tool_results(result["messages"])

    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": result["question"],
        "answer": result["answer"],
        "step_count": result["step_count"],
        "tool_used": len(tool_results) > 0,
        "tool_results": tool_results
    }

    history.append(record)

    file_path = get_data_file_path(HISTORY_FILE)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii= False, indent = 2)

    print("Agent 运行记录已保存：", HISTORY_FILE)
