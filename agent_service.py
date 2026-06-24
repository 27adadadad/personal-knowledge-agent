from langchain_core.messages import HumanMessage, ToolMessage

from agent_graph import agent_graph
from agent_history import save_agent_history




def get_source_chunk_ids(messages):
    source_chunk_ids = []

    for message in messages:
        if not isinstance(message, ToolMessage):
            continue

        lines = str(message.content).splitlines()

        for line in lines:
            if not line.startswith("[chunk "):
                continue

            if not line.endswith("]"):
                continue

            chunk_id_text = line[len("[chunk "):-1]


            if not chunk_id_text.isdigit():
                continue

            chunk_id = int(chunk_id_text)

            if chunk_id not in source_chunk_ids:
                source_chunk_ids.append(chunk_id)

    return source_chunk_ids


def run_agent(question):
    state = {
        "question":question,
        "messages":[
            HumanMessage(content=question)
        ],
        "answer":"",
        "step_count":0
    }

    result = agent_graph.invoke(state)

    source_chunk_ids = get_source_chunk_ids(
        result["messages"]
    )

    save_agent_history(result)

    return {
        "answer":result["answer"],
        "sources":source_chunk_ids,
        "step_count":result["step_count"]
    }