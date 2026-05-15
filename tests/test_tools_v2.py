import asyncio
import sys
import os
import json
from server_v2 import mcp

async def test_tools():
    print("Testing get_network_status tool...")
    # FastMCP doesn't expose a direct way to call tools easily without running the server
    # but we can call the functions directly since they are decorated.
    # Actually, we can use mcp.call_tool
    
    try:
        result = await mcp.call_tool("get_network_status", {})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    print("\nTesting get_agent_identity tool...")
    try:
        result = await mcp.call_tool("get_agent_identity", {})
        print(f"Result: {result}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_tools())
