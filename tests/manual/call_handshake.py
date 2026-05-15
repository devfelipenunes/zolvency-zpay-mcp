import asyncio
import os
import json
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    server_params = StdioServerParameters(
        command=os.path.join(os.getcwd(), "zpay/zpay-mcp/venv/bin/python"),
        args=[os.path.join(os.getcwd(), "zpay/zpay-mcp/server.py")],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            
            print("\n--- Solicitando Sovereign Link ---")
            result = await session.call_tool("request_sovereign_link", arguments={})
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run())
