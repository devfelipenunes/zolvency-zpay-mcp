# Z-Pay Universal MCP Server

Este servidor permite que qualquer cliente compatível com **Model Context Protocol (MCP)**, como o **Claude Desktop**, integre pagamentos e mandatos do Z-Pay.

## Ferramentas Disponíveis

1.  `zpay_request_identity`: Inicia o login via Passkey.
2.  `zpay_poll_identity`: Verifica o status da autorização.
3.  `zpay_link_account`: Importa identidade SoulID via JSON.
4.  `zpay_sync_identity`: Sincroniza sessão com o navegador.
5.  `zpay_search_providers`: Busca serviços de infraestrutura (com filtro).
6.  `zpay_get_balance`: Consulta saldo do mandato ou carteira.
7.  `zpay_check_intent`: Valida se o gasto está autorizado.
8.  `zpay_execute_payment`: Realiza o pagamento usando Session Keys.

## Configuração

1.  Crie um arquivo `.env` baseado no `.env.example`:
    ```bash
    cp .env.example .env
    ```
2.  Instale as dependências em um ambiente virtual:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pip install -e ../zpay_python/
    ```

## Instalação no Claude Desktop

Adicione o seguinte trecho ao seu arquivo `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "zpay": {
      "command": "/caminho/para/seu/projeto/zpay-mcp-server/venv/bin/python",
      "args": [
        "/caminho/para/seu/projeto/zpay-mcp-server/server.py"
      ],
      "env": {
        "PYTHONPATH": "/caminho/para/seu/projeto"
      }
    }
  }
}
```

## Requisitos

- Python 3.10+
- `mcp` SDK
- `httpx` (Assíncrono)
- `python-dotenv`
- Servidor Mock Provider rodando (`poc_zpay_crewai/mock_provider/server.py`)

## Por que isso é Universal?

Ao expor as ferramentas via MCP, você não precisa mais escrever código de integração para cada nova IA. O próprio modelo de linguagem (LLM) entende as descrições das ferramentas e decide quando chamá-las para resolver o problema do usuário.
