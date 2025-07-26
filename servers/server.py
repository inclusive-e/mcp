from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-project-server")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
  "Add two numbers from given arguments"
  return a + b

if __name__ == "__main__":
  """Run the MCP Server as stdio transport"""
  mcp.run(transport='stdio')