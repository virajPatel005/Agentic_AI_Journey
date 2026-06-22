import langgraph
from typing import TypedDict,Annotated,Literal
from langchain_core.messages import HumanMessage,AIMessage,BaseMessage
from langgraph.graph import START,END,StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langchain_openai import ChatOpenAI
from pydantic import BaseModel,Field
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode,tools_condition
from langchain_community.tools import TavilySearchResults
from dotenv import load_dotenv
import os

load_dotenv()
model=ChatOpenAI(
model="google/gemma-4-e2b",
base_url="http://localhost:1234/v1",
api_key="lm-studio"#type:ignore
)


class Chatbot_state(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]



@tool
def calculator(first_num:float,second_num:float,operation:str)->float:
    """
    Perform arithmetic calculations.

Use this tool whenever you need to add +, subtract -,
multiply *, or divide numbers /."""

    if operation == "+":
        return first_num + second_num

    elif operation == "-":
        return first_num - second_num

    elif operation == "*":
        return first_num * second_num

    elif operation == "/":
        if second_num == 0:
            raise ValueError("Division by zero is not allowed.")
        return first_num / second_num

    else:
        raise ValueError("Unsupported operation. Use +, -, *, or /.")
    
    
search_tool=TavilySearchResults(max_results=3)
tools=[search_tool,calculator]
tool_model=model.bind_tools(tools)


def chat_node(state:Chatbot_state):
    """LLM node that can answer the query or call the tools".
    If a ToolMessage is present in the conversation:
1. Read the tool output carefully.
2. Extract the answer from the tool output.
3. Return only the final answer to the user.
4. Do not repeat raw tool results.
"""
    messages=state["messages"]
    response = tool_model.invoke(messages)
    return{"messages":[response]}


tool_node=ToolNode(tools)
graph=StateGraph(Chatbot_state)
graph.add_node("chat_node",chat_node)
graph.add_node("tool_node",tool_node)

graph.add_edge(START,"chat_node")
graph.add_conditional_edges("chat_node",tools_condition,{"tools":"tool_node","__end__":END})
graph.add_edge("tool_node","chat_node")

conn=sqlite3.connect(
    database="tool_chatbot.db",
    check_same_thread=False
    
)

checkpointer=SqliteSaver(conn=conn)
chatbot=graph.compile(checkpointer=checkpointer)


def get_all_threads():
    threads=set()
    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config["configurable"]["thread_id"])#type:ignore
    return list(threads)


