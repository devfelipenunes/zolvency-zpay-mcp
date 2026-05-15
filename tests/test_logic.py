import asyncio
from zpay_mcp.server import mcp

async def test_health_check():
    print("Testing get_network_status...")
    # FastMCP doesn't have a global handle_call_tool, we access the tool directly
    tool = mcp._tools["get_network_status"]
    result = await tool.run()
    print(f"Result: {result}")

async def test_balance():
    print("\nTesting get_on_chain_balance (Mandate #2)...")
    tool = mcp._tools["get_on_chain_balance"]
    result = await tool.run(mandate_id=2)
    print(f"Result: {result}")

if __name__ == "__main__":
    asyncio.run(test_health_check())
    asyncio.run(test_balance())
