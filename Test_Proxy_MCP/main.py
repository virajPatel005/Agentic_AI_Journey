from fastmcp import FastMCP

# Create a proxy to your remote FastMCP Cloud server
# FastMCP Cloud uses Streamable HTTP (default), so just use the /mcp URL
mcp = FastMCP.as_proxy(
    "https://complicated-copper-goose.fastmcp.app/mcp",  # Standard FastMCP Cloud URL
    name="Viraj Server Proxy"
)

if __name__ == "__main__":
# Run the proxy MCP server over STDIO for local MCP clients
    mcp.run()