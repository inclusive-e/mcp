from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client

class MCPClient:
  def __init__(self):
    # Create server params for stdio connection
    self.server_params = StdioServerParameters(
      command="mcp", # Executable
      args=["run", "./servers/server.py"], # Server script
      env=None
    )

  async def run(self):
    """Main client execution function"""
    print("Starting MCP Client")

    try:
      async with stdio_client(server=self.server_params) as (read, write):
        async with ClientSession(read_stream=read, write_stream=write) as session:
          print("Connecting to MCP Server")

          # Initialize the connection
          await session.initialize()
          print("Connected to MCP Server successfully")

          # List available tools
          await self.list_tools(session=session)

          # List and test available resources
          await self.list_and_test_resources(session=session)

          print("All MCP Client operations completed successfully!")

    except Exception as e:
      print("Error running MCP Client : ", e)
      return False
    

  async def list_tools(self, session: ClientSession):
    """List all the available tools on the server"""
    print("Listing available tools on the MCP server")

    try:
      tools = await session.list_tools()

      for tool in tools.tools:
        print(f" - {tool.name}: ${tool.description}")
    except Exception as e:
      print(f"Error listing tools: ${e}")
  
  async def list_and_test_resources(self, session: ClientSession):
    """List all the available resources on the server"""
    print("Listing available resources on the MCP server")


    # Test reading a resource if available
    try:
      resources = await session.list_resources()
      for resource in resources.resources:
         print(f" - {resource.name}: {resource.description}")
         print(f"URI: {resource.uri}")

      if resources.resources:
        try:
          if resources.resources:
            first_resource = resources.resources[0]
            content = await session.read_resource(first_resource.uri)
            print(f"Resource content: {content}")
        except Exception as e:
            print(f"Error reading resource: {e}")
      else:
        print("No resources available")
      
    except Exception as e:
      print(f"Error listing resources: ${e}")


async def main():
  """Entry point for the client"""
  client = MCPClient()
  await client.run()

if __name__ == "__main__":
  import asyncio
  asyncio.run(main())