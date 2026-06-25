import json
from datetime import datetime

from rag_files import get_data_file_path
from agent_config import RAG_HISTORY_FILE


def load_rag_history():
    file_path = get_data_file_path(RAG_HISTORY_FILE)

    if not file_path.exists():
        return []

    try:
        with open(file_path, "r", encoding="utf-8")as file:

            history = json.load(file)

        if isinstance(history, list):
            return history

        return []

    except json.JSONDecodeError:
        print("RAG 历史记录文件损坏，已使用空记录")
        return []


def save_rag_history(question, results, answer, usage):
    file_path = get_data_file_path(RAG_HISTORY_FILE)

    history = load_rag_history()

    record = {
        "time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "retrieved_chunks": results,
        "answer": answer,
        "usage": usage
    }

    history.append(record)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(history, file, ensure_ascii=False, indent=2)

    print("RAG 问答历史已保存：", RAG_HISTORY_FILE)
