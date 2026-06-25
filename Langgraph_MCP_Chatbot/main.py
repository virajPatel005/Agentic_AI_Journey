from langgraph.graph import StateGraph,START,END
from typing import Annotated,Literal,TypedDict
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage,BaseMessage,SystemMessage
from dotenv import load_dotenv
from langchain_tavily import TavilySearch
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
load_dotenv()
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode,tools_condition
from langgraph.checkpoint.memory import InMemorySaver

SYSTEM = SystemMessage(content="""You are a helpful assistant with access to tools.

IMPORTANT CONTEXT:
- You have filesystem access to ONLY this directory: C:\\Users\\viraj\\Desktop
- All file operations must use this exact path as the base. Example: C:\\Users\\viraj\\Desktop\\mcp.py
- Do NOT call list_allowed_directories — you already know the allowed directory.

RULES:
1. For news, current events, stock prices, or any real-time data → call tavily_search immediately. Never answer from memory.
2. For file/directory tasks → construct the full path using C:\\Users\\viraj\\Desktop, then call the correct tool ONCE. If it fails, report the error. Do not retry.
3. For math operations → use the math tools (add, subtract, multiply, divide).
4. Never fabricate tool results. Only use what the tool actually returned.
5. After a tool returns results, give a clean concise summary. No raw JSON.
6. When you create or find a file, always tell the user the full path.
""")


model=ChatOpenAI(
    model="qwen/qwen3.5-9b",
    base_url="http://localhost:1234/v1",
    api_key="lm-studio",#type:ignore
    
)

client = MultiServerMCPClient(
    {
        "math": {
            "command": r"C:\Users\viraj\Desktop\Github_projcts\git_project\Scripts\python.exe",
            "args": [
                r"C:\Users\viraj\Desktop\Github_projcts\LangGraph_MCP_Integration\math_server.py"
            ],
            "transport": "stdio"
        },
        
        "filesystem": {
        "command": "npx",
        "args": [
            "-y",
            "@modelcontextprotocol/server-filesystem",
            "C:\\Users\\viraj\\Desktop"
        ],
        "transport": "stdio"
         }
    }
)

class ChatState(TypedDict):
    messages:Annotated[list[BaseMessage],add_messages]
    

async def build_graph():
    search_tool=TavilySearch(max_results=3)
    tools=await client.get_tools()
    tools=tools+[search_tool]
    print("Available Tools:\n")
    for tool in tools:
        print(tool.name)
    mcp_model=model.bind_tools(tools)
    
    async def chat_node(state:ChatState):

        messages=[SYSTEM] +state["messages"]
        response=await mcp_model.ainvoke(messages)
        return {"messages":[response]}
    
    tool_node=ToolNode(tools)
    graph=StateGraph(ChatState)
    graph.add_node("chat_node",chat_node)
    graph.add_node("tool_node",tool_node)
    
    graph.add_edge(START,"chat_node")
    graph.add_conditional_edges("chat_node",tools_condition,{"tools":"tool_node","__end__":END})
    graph.add_edge("tool_node","chat_node")
    checkpointer=InMemorySaver()
    
    chatbot=graph.compile(checkpointer=checkpointer)
    return chatbot

async def main():
    chatbot=await build_graph()
    CONFIG={"recursion_limit":25,"configurable":{
        "thread_id":"1"
    }}
    while True:
        quit=["exit","bye"]
        user_input=input("YOU: ")
        if not user_input.strip():      # <-- add this
            continue
        if user_input.strip().lower() in quit:
            print("Thx Have a Good day")
            break
        print("AI: ", end="", flush=True)
        async for chunk,metadata in chatbot.astream(
        {
            "messages":[HumanMessage(content=user_input)]
        },stream_mode="messages",config=CONFIG#type:ignore
        ):
          if (
              hasattr(chunk,"content")
              and chunk.content#type:ignore
              and metadata.get("langgraph_node")=="chat_node"#type:ignore
          ):
              print(chunk.content,end="",flush=True)#type:ignore
        print()
         
if __name__=="__main__":
    asyncio.run(main())
        
    
       

