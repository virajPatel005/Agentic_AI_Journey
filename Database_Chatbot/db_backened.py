import langgraph
from typing import TypedDict,Annotated,Literal
from langchain_core.messages import HumanMessage,AIMessage,BaseMessage
from langgraph.graph import START,END,StateGraph
from langgraph.graph.message import add_messages
from langgraph.checkpoint.sqlite import SqliteSaver
import sqlite3
from langchain_openai import ChatOpenAI
from pydantic import BaseModel,Field
import uuid 

model=ChatOpenAI(
model="google/gemma-4-e2b",
base_url="http://localhost:1234/v1",
api_key="lm-studio"#type:ignore
)

class Chatbot_state(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]

def chat_node(state:Chatbot_state):
    message=state["messages"]
    response=model.invoke(message)
    return{"messages":response}

graph=StateGraph(Chatbot_state)
graph.add_node("chat_node",chat_node)
graph.add_edge(START,"chat_node")
graph.add_edge("chat_node",END)

conn = sqlite3.connect(
    "basic_chatbot.db",
    check_same_thread=False
)



checkpointer=SqliteSaver(conn=conn)
chatbot=graph.compile(checkpointer=checkpointer)


def get_all_threads():
    threads=set()
    for checkpoint in checkpointer.list(None):
        threads.add(checkpoint.config["configurable"]["thread_id"])#type:ignore
    return list(threads)
    

class Thread_schema(BaseModel):
    thread:str=Field(description="short Title Based on first conversation with user.")
thread_model=model.with_structured_output(Thread_schema)


