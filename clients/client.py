import json
import os
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from openai import OpenAI

load_dotenv()
secret_token = os.getenv('SECRET_TOKEN')
model_url = os.getenv('MODEL_API_URL')
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
          all_tools = await self.list_tools(session=session)

          # List and test available resources
          await self.list_and_test_resources(session=session)

          """
            Test the model calling with a sample prompt

            1. If LLM suggests a tool calls, loop through and call suggested tools
            2. Else diplay response.content returned by LLM
          """
          functions = []
          if(all_tools):
            for tool in all_tools:
              functions.append(self.convert_to_llm_tool(tool=tool))

          # Ask LLM
          llm_response_message = self.call_llm(prompt="add 20 + 5", functions=functions)

          if(llm_response_message):
            # Loop through tools if suggested by LLM
            if(llm_response_message.tool_calls):
              functions_to_call = []
              for tool_call in llm_response_message.tool_calls:
                print("TOOL: ", tool_call)
                functions_to_call.append({ "name": tool_call.function.name, "args": json.loads(tool_call.function.arguments) })

                if functions_to_call:
                  # Call Suggested functions by LLM
                  for fn in functions_to_call:
                    result = await session.call_tool(fn["name"], arguments=fn["args"])
                    print(f"Result: {result.content[0].text}")
              
            elif llm_response_message.content:
              return print(f"Result: {llm_response_message.content}")

          print("All MCP Client operations completed successfully!")

    except Exception as e:
      print("Error running MCP Client : ", e)
      return False
  
  def call_llm(self, prompt, functions, model="openai/gpt-4o-mini", endpoint=model_url):
    """Call Chosen Large Language Model"""

    token = secret_token
    endpoint_url = endpoint
    model_name = model

    # TODO: Check if model_name contains "openai" then elif:
    try:
      client = OpenAI(
        base_url=endpoint_url,
        api_key=token
      )

      print(f"Calling LLM: {model_name}")
      response = client.chat.completions.create(
        messages=[
          {
            "role": "system",
            "content": "You are a helpful assistant"
          },
          {
            "role": "user",
            "content": prompt
          }
        ],
        model=model_name,
        tools=functions,
        temperature=1.0,
        top_p=1.0,
        max_tokens=1000,
      )
      response_message = response.choices[0].message
      return response_message
    
    except Exception as e:
      print(f"Failed to call LLM: ${model_name}", e)
      return False
    
  
  def convert_to_llm_tool(self, tool):
    return {
      "type": "function",
      "function": {
        "name": tool.name,
        "description": tool.description,
        "type": "function",
        "parameters": {
            "type": "object",
            "properties": tool.inputSchema["properties"]
        }
      }
    }

  
  async def list_tools(self, session: ClientSession):
    """List all the available tools on the server"""
    print("Listing available tools on the MCP server")

    try:
      all_available_tools = []
      tools = await session.list_tools()

      for tool in tools.tools:
        print(f" - {tool.name}: ${tool.description}")
        all_available_tools.append(tool)
      
      return all_available_tools
    except Exception as e:
      print(f"Error listing tools: ${e}")
      return False
  
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