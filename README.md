# ZPay Sovereign MCP Server

O gateway oficial para a Economia de Agentes Soberanos na rede Stellar.

## 🚀 Instalação Rápida (Zero-Friction)

Para que o seu agente (Claude/Gemini) consiga usar este servidor sem erros de caminho ou dependências, siga estes passos:

### 1. Preparar o Ambiente
```bash
cd zpay/zpay-mcp
# Instala o servidor como um comando global no seu venv
venv/bin/pip install -e .
```

### 2. Configurar o Cliente (Claude/Gemini)
Agora você não precisa mais de caminhos longos e complexos. Use apenas o caminho do executável `zpay-mcp` gerado dentro do seu venv.

**Exemplo de Configuração:**
*   **Comando**: `/l/disk0/fnunes/Documentos/me/zolvency/zpay/zpay-mcp/venv/bin/zpay-mcp`
*   **Argumentos**: `[]` (Vazio)

## 🛠️ Autodiagnóstico
Se o agente estiver com problemas, peça para ele rodar a ferramenta:
`check_health` ou `get_network_status`.

## 📁 Estrutura Organizada
- `server.py`: O núcleo do servidor FastMCP.
- `tests/manual/`: Scripts para você testar sem precisar do LLM.
- `agent_identity.json`: Sua identidade persistente (gerada automaticamente).

---
Para mais detalhes sobre o protocolo, veja `docs/ZOLVENCY_SYSTEM_MANIFEST.md`.
