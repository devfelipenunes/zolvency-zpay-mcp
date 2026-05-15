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
            
            # Endereço do agente que já sabemos ter identidade persistente
            address = "GBEHFEGXWEDPATKLFIASIMCRNABYFMA322JRXXJA7W3AMIQTIKKZU4IJ"
            
            print(f"\n--- Consultando Mandatos para {address} ---")
            # Usando o recurso (resource) definido no server.py: @mcp.resource("zpay://mandates/{address}")
            result = await session.read_resource(f"zpay://mandates/{address}")
            
            # O conteúdo de um resource costuma estar em result.contents[0].text ou .blob
            mandates = json.loads(result.contents[0].text)
            
            if not mandates:
                print("Nenhum mandato encontrado para este agente.")
            else:
                print(f"Total de mandatos encontrados: {len(mandates)}")
                for m in mandates:
                    print(f"- ID: {m.get('id')} | Status: {'Ativo' if m.get('active') else 'Inativo'}")

if __name__ == "__main__":
    asyncio.run(run())
