from typing import Literal
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

from agent_model import model_node
from agent_state import AgentState
from agent_tools import search_knowledge

def decide_after_model(state:AgentState) ->Literal["tools", "end"]:
    if len(state["messages"])==0:
        return "end"

    last_message = state["messages"][-1]

    if isinstance(last_message, AIMessage) and last_message.tool_calls:
        return "tools"

    return "end"


graph_builder = StateGraph(AgentState)

graph_builder.add_node("model" , model_node)

graph_builder.add_node(
    "tools",
    ToolNode([search_knowledge])
)

graph_builder.add_edge(START, "model")

graph_builder.add_conditional_edges(
    "model",
    decide_after_model,
    {
        "tools":"tools",
        "end":END
    }
)

graph_builder.add_edge("tools", "model")

agent_graph = graph_builder.compile()
