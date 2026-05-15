import asyncio
import os
import json
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def call_tool(tool_name, arguments):
    # Auto-detect paths relative to this script
    CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
    # Going up from tests/manual/ to zpay-mcp/
    BASE_DIR = os.path.abspath(os.path.join(CURRENT_DIR, "..", ".."))
    
    PYTHON_BIN = os.path.join(BASE_DIR, "venv", "bin", "python")
    SERVER_SCRIPT = os.path.join(BASE_DIR, "zpay_mcp", "server.py")

    server_params = StdioServerParameters(
        command=PYTHON_BIN,
        args=[SERVER_SCRIPT],
        env=None
    )

    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                result = await session.call_tool(tool_name, arguments)
                if hasattr(result, 'content'):
                    return result.content[0].text
                return str(result)
    except Exception as e:
        return f"Error connecting to MCP Server: {str(e)}\nTested Path: {SERVER_SCRIPT}"

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python mcp_client.py <tool_name> [json_arguments]")
        sys.exit(1)
    
    tool = sys.argv[1]
    args = json.loads(sys.argv[2]) if len(sys.argv) > 2 else {}
    
    output = asyncio.run(call_tool(tool, args))
    print(output)
