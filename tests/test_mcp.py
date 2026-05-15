import asyncio
from mcp.server import Server
from mcp.server.models import InitializationOptions
import mcp.types as types
from server import server, handle_list_tools

async def test_listing():
    print("Testing tool listing...")
    tools = await handle_list_tools()
    for t in tools:
        print(f"- {t.name}: {t.description}")

if __name__ == "__main__":
    asyncio.run(test_listing())
