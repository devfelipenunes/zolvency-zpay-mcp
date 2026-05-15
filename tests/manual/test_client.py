import asyncio
import sys
import os
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

async def run():
    # Caminho para o executável do python no venv e o script do servidor
    server_params = StdioServerParameters(
        command=os.path.join(os.getcwd(), "zpay/zpay-mcp/venv/bin/python"),
        args=[os.path.join(os.getcwd(), "zpay/zpay-mcp/server.py")],
        env=None
    )

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Inicializa a sessão
            await session.initialize()

            # Lista as ferramentas disponíveis
            print("\n--- Ferramentas Disponíveis ---")
            tools = await session.list_tools()
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

            # Exemplo: Chamar get_agent_identity
            print("\n--- Chamando get_agent_identity ---")
            result = await session.call_tool("get_agent_identity", arguments={})
            print(f"Resultado: {result.content[0].text}")

if __name__ == "__main__":
    asyncio.run(run())
