import asyncio
import os
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
            
            # Usando uma conta de teste conhecida ou a própria conta do agente para teste
            address = "GBEHFEGXWEDPATKLFIASIMCRNABYFMA322JRXXJA7W3AMIQTIKKZU4IJ"
            
            print(f"\n--- Consultando Saldo para {address} ---")
            result = await session.call_tool("get_on_chain_balance", arguments={"address": address})
            print(result.content[0].text)

if __name__ == "__main__":
    asyncio.run(run())
