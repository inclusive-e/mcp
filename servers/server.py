from mcp.server.fastmcp import FastMCP

mcp = FastMCP("mcp-project-server")

@mcp.tool()
def add_numbers(a: int, b: int) -> int:
  "Add two numbers from given arguments"
  return a + b

def main():
  """Run the MCP Server as stdio transport"""
  return mcp.run(transport='stdio')

if __name__ == "__main__":
  main()