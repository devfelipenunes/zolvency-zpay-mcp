import asyncio
import sys
import os
from server_v2 import mcp

async def test_server_init():
    print("Initializing server...")
    # List tools to see if they are registered correctly
    tools = await mcp.list_tools()
    print(f"Found {len(tools)} tools:")
    for tool in tools:
        print(f"- {tool.name}: {tool.description}")
    
    # List resources
    resources = await mcp.list_resources()
    print(f"\nFound {len(resources)} resources:")
    for res in resources:
        print(f"- {res.name}: {res.uri}")

    # List prompts
    prompts = await mcp.list_prompts()
    print(f"\nFound {len(prompts)} prompts:")
    for p in prompts:
        print(f"- {p.name}: {p.description}")

if __name__ == "__main__":
    asyncio.run(test_server_init())
