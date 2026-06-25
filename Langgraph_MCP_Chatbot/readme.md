# LangGraph MCP Chatbot

A chatbot built using LangGraph that integrates MCP (Model Context Protocol) servers, external tools, memory persistence, and real-time search capabilities.

## Features

* LangGraph StateGraph workflow
* Tool calling with ToolNode
* Conditional routing using tools_condition
* MCP integration
* Filesystem MCP server
* Custom Math MCP server
* Tavily Search integration
* Conversation memory using InMemorySaver
* Streaming responses
* Thread-based checkpoint persistence

## Tech Stack

* Python
* LangGraph
* LangChain
* MCP (Model Context Protocol)
* Tavily Search
* LM Studio
* Qwen 3.5

## Architecture

User Input
→ Chat Node
→ Tool Decision
→ Tool Node (Math / Filesystem / Tavily)
→ Chat Node
→ Response

## Concepts Demonstrated

* State Management
* Nodes and Edges
* Conditional Edges
* Tool Calling
* MCP Integration
* Checkpointing
* Memory Persistence
* Streaming

## Example Queries

* What is 25 * 12?
* Create a folder named test on Desktop.
* List files on Desktop.
* What is the weather in Pune today?
* Remember my name is Raj. What is my name?

This project was created as part of a LangGraph learning journey to understand graph-based agent workflows and MCP integrations.
