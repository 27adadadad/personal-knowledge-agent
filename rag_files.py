import os

from pathlib import Path

from agent_config import KNOWLEDGE_FILE



def get_file_path(filename):
    current_dir= Path(__file__).parent
    return current_dir / filename


def get_data_file_path(filename):
    data_dir_text = os.getenv("DATA_DIR")

    if data_dir_text:
        return Path(data_dir_text) / filename

    return get_file_path(filename)


def load_knowledge_text():
    file_path = get_file_path(KNOWLEDGE_FILE)

    with open(file_path, "r", encoding= "utf-8") as file:
        text = file.read()

    return text

def split_text_to_chunks(text):
    parts = text.split("\n\n")

    chunks = []
    chunk_id = 1

    for part in parts:
        content = part.strip()

        if content == "":
            continue

        chunk = {
            "id":chunk_id,
            "text":content
        }

        chunks.append(chunk)
        chunk_id+=1

    return chunks


def load_knowledge():
    text = load_knowledge_text()
    chunks = split_text_to_chunks(text)

    return chunks
