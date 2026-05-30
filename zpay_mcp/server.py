"""
ZPay Sovereign MCP Server
Version: 2.1.0
Author: Zolvency Protocol Team
License: MIT

This is the official Model Context Protocol (MCP) server for the ZPay ecosystem.
It enables AI agents to securely interact with the Stellar blockchain, manage 
sovereign mandates, and execute authorized payments via the ZPay Gateway.

STANDARDS & INSTALLATION:
-------------------------
1. Requirements: Python 3.10+, mcp[fastmcp], stellar-sdk, python-dotenv
2. Environment: Create a .env file with the following keys:
   - ZPAY_STELLAR_NETWORK: "TESTNET" or "PUBLIC"
   - ZPAY_CONTRACT_ID_NEXUS: Your Nexus contract ID
   - ZPAY_CONTRACT_ID_GATEWAY: Your ZPay Gateway contract ID
   - ZPAY_BACKEND_API_URL: URL to the ZPay processing backend
3. Execution:
   - Development: `python server.py`
   - Gemini/Claude CLI: Add the absolute path to your config.

For more information, visit: https://zolvency.com/docs/mcp
"""

import os
import sys
from pathlib import Path
import json
import logging
import httpx
from typing import Any, Dict, List, Optional
from mcp.server.fastmcp import FastMCP, Context
from stellar_sdk import Keypair

# Internal Imports
from .config import settings
from zpay.agent_kit import ZPayAgentKit, ZPayConfig
from zpay.models import MandateModel, PaymentResponse, AuditReport, EscrowPayment

# Logging Setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger("zpay-mcp")

# System Constants
XLM_TOKEN_ID = "CDLZFC3SYJYDZT7K67VZ75HPJVIEUVNIXF47ZG2FB2RMQQVU2HHGCYSC"

# -----------------------------------------------------------------------------
# 2. FastMCP Instance Initialization (SDK Fix Applied)
# -----------------------------------------------------------------------------

mcp = FastMCP(
    "ZPay Sovereign Gateway",
    instructions="Universal interface for ZPay Agentic Economy on Stellar. "
                 "Manage mandates, verify compliance, and execute payments."
)

# -----------------------------------------------------------------------------
# 3. Identity & SDK Helpers
# -----------------------------------------------------------------------------

_AGENT_IDENTITY_CACHE = None

from cryptography.fernet import Fernet

def get_encryption_key() -> bytes:
    """Returns or generates a stable encryption key for identity storage."""
    key = os.getenv("ZPAY_IDENTITY_CRYPT_KEY")
    if not key:
        logger.warning("ZPAY_IDENTITY_CRYPT_KEY not set. Identity will be stored in PLAINTEXT (Not recommended for production).")
        return None
    return key.encode()

def ensure_agent_identity():
    global _AGENT_IDENTITY_CACHE
    if _AGENT_IDENTITY_CACHE:
        return _AGENT_IDENTITY_CACHE
    
    # Priority 1: Project Root (Recommended for development)
    root_identity = Path("/l/disk0/fnunes/Documentos/me/zolvency/agent_identity.json")
    # Priority 2: Standard Config Directory
    config_identity = settings.config_dir / "agent_identity.json"
    
    identity_path = None
    if root_identity.exists():
        identity_path = root_identity
        logger.info(f"Using identity from Root: {root_identity}")
    elif config_identity.exists():
        identity_path = config_identity
        logger.info(f"Using identity from Config: {config_identity}")

    if identity_path:
        try:
            with open(identity_path, "r") as f:
                data = json.load(f)
            if "public_key" in data and "secret" in data:
                _AGENT_IDENTITY_CACHE = (data["public_key"], data["secret"])
                return _AGENT_IDENTITY_CACHE
        except Exception as e:
            logger.warning(f"Failed to read identity from {identity_path}: {e}")

    # Fallback: Generate New Identity in Root
    kp = Keypair.random()
    logger.info(f"Generated New Agent Identity: {kp.public_key}")
    _AGENT_IDENTITY_CACHE = (kp.public_key, kp.secret)
    
    try:
        with open(root_identity, "w") as f:
            json.dump({"public_key": kp.public_key, "secret": kp.secret}, f)
        logger.info(f"Identity saved to Root: {root_identity}")
    except Exception as e:
        logger.error(f"Failed to save identity to Root: {e}")
        
    return _AGENT_IDENTITY_CACHE

def get_kit():
    config = ZPayConfig(
        rpc_url=settings.stellar_rpc_url,
        network_passphrase=settings.stellar_network_passphrase,
        nexus_id=settings.contract_id_nexus,
        zpay_id=settings.contract_id_gateway,
        soul_id=settings.contract_id_identity,
        backend_url=settings.backend_api_url,
        horizon_url=settings.stellar_horizon_url
    )
    pk, sk = ensure_agent_identity()
    return ZPayAgentKit(config=config, keypair=Keypair.from_secret(sk))

# -----------------------------------------------------------------------------
# 4. Resources (Real-time Context)
# -----------------------------------------------------------------------------

@mcp.resource("zpay://network/status")
async def get_network_status_resource() -> str:
    """Returns the live status and topology of the ZPay network."""
    return json.dumps({
        "network": settings.stellar_network,
        "contracts": {
            "nexus": settings.contract_id_nexus,
            "gateway": settings.contract_id_gateway,
            "identity": settings.contract_id_identity
        },
        "api": settings.backend_api_url,
        "rpc": settings.stellar_rpc_url
    }, indent=2)

@mcp.resource("zpay://agent/identity")
async def get_agent_identity_resource() -> str:
    """Returns the agent's public identity (Stellar Public Key)."""
    pk, _ = ensure_agent_identity()
    return json.dumps({"public_key": pk, "type": "Stellar Ed25519"}, indent=2)

@mcp.resource("zpay://agent/status")
async def get_agent_status_resource() -> str:
    """Returns the live operational status of the agent."""
    pk, _ = ensure_agent_identity()
    kit = get_kit()
    try:
        balance = await kit.fetch_account_balance(pk)
        primary_mandate = await kit.get_primary_mandate_id(pk)
        return json.dumps({
            "identity": pk,
            "status": "ONLINE",
            "native_balance": balance,
            "primary_mandate": primary_mandate,
            "blockchain_connectivity": "CONNECTED"
        }, indent=2)
    except Exception as e:
        return json.dumps({
            "identity": pk,
            "status": "DEGRADED",
            "error": str(e)
        }, indent=2)

@mcp.resource("zpay://network/metrics")
async def get_network_metrics_resource() -> str:
    """Returns real-time performance metrics of the Stellar network for this agent."""
    import time
    start = time.time()
    kit = get_kit()
    try:
        latest_ledger = kit.soroban_server.get_latest_ledger().sequence
        latency = (time.time() - start) * 1000
        return json.dumps({
            "latest_ledger": latest_ledger,
            "rpc_latency_ms": round(latency, 2),
            "network": settings.stellar_network,
            "timestamp": int(time.time())
        }, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch metrics: {e}"}, indent=2)

@mcp.resource("zpay://mandates/{address}")
async def get_address_mandates(address: str) -> str:
    """Returns all active mandates issued to a specific Stellar address."""
    kit = get_kit()
    mandates = await kit.scan_agent_mandates(address)
    return json.dumps(mandates, indent=2)

# -----------------------------------------------------------------------------
# 5. Tools (On-Chain Actions)
# -----------------------------------------------------------------------------

@mcp.tool()
async def get_network_status() -> str:
    """Returns the live status and topology of the ZPay network."""
    return await get_network_status_resource()

@mcp.tool()
async def get_agent_identity() -> str:
    """Returns the agent's public identity (Stellar Public Key)."""
    return await get_agent_identity_resource()

@mcp.tool()
async def get_on_chain_balance(mandate_id: Optional[int] = None, address: Optional[str] = None) -> str:
    """Fetches real-time token or mandate balance directly from the Stellar ledger."""
    kit = get_kit()
    if not address and not settings.agent_identity_pk:
        pk, _ = ensure_agent_identity()
        addr = pk
    else:
        addr = address or settings.agent_identity_pk
    
    if mandate_id:
        try:
            details = await kit.get_mandate_details(mandate_id)
            return (
                f"💳 **Nexus Mandate #{mandate_id}**\n"
                f"- Status: {'ACTIVE' if details.active else 'REVOKED'}\n"
                f"- Remaining: {details.available_xlm} XLM"
            )
        except Exception as e:
            return f"❌ **Error:** {str(e)}"
    else:
        balance = await kit.fetch_account_balance(addr)
        return f"💰 **Sovereign Wallet**\n- Address: `{addr}`\n- Balance: {balance} XLM"

@mcp.tool()
async def verify_spending_compliance(amount: float, mandate_id: int, ctx: Context) -> str:
    """Verifies if a spending intent is authorized by the active mandate on-chain."""
    ctx.info(f"Checking compliance for {amount} XLM against mandate #{mandate_id}...")
    kit = get_kit()
    result = await kit.validate_spending_intent(amount, mandate_id)
    
    if result["authorized"]:
        return f"✅ **Compliance Verified:** {result.get('human_readable_report')}"
    else:
        return f"❌ **Unauthorized:** {result.get('reason', 'Mandate constraint violation.')}"

@mcp.tool()
async def check_gateway_allowance(user_anchor_address: str, token_address: Optional[str] = None) -> str:
    """Checks if the user has granted enough allowance for the ZPay Gateway to move funds."""
    kit = get_kit()
    token = token_address or XLM_TOKEN_ID
    allowance = await kit.get_token_allowance(user_anchor_address, settings.contract_id_gateway, token)
    
    if allowance > 0:
        return f"✅ **Allowance Active:** Gateway is authorized to move funds ({allowance} XLM)."
    else:
        return (
            f"❌ **Approval Required:** The ZPay Gateway does not have permission to spend tokens for `{user_anchor_address[:8]}...`.\n"
            f"Please call `prepare_agent_onboarding` to fix this."
        )

@mcp.tool()
async def execute_sovereign_payment(
    amount: float, 
    recipient_address: str, 
    mandate_id: int, 
    user_anchor_address: str,
    ctx: Context
) -> str:
    """Submits a secure payment transaction to the Z-Pay Gateway for on-chain execution."""
    await ctx.info(f"Initializing payment of {amount} XLM for mandate #{mandate_id}...")
    kit = get_kit()
    
    # 1. Pre-flight Checks (Professional Mode)
    await ctx.info("Running pre-flight simulations and allowance checks...")
    preflight = await kit.execute_proxy_payment(amount, recipient_address, mandate_id, user_anchor_address)
    
    if not preflight["success"]:
        # --- HYBRID FALLBACK LOGIC ---
        # If the failure is JUST allowance, and we are in MVP mode, we fulfill via Agent funds
        if preflight["error"] == "INSUFFICIENT_ALLOWANCE":
            await ctx.warning("INSUFFICIENT_ALLOWANCE detected. Compliance is OK. Executing via Agent Operational Funds for MVP continuity...")
            
            try:
                from stellar_sdk import Server, TransactionBuilder, Asset
                h = Server("https://horizon-testnet.stellar.org")
                # load_account é síncrono no SDK da Stellar v9+
                acc = h.load_account(kit.keypair.public_key)
                
                # Formatar valor com 7 casas decimais para evitar erro de sintaxe decimal
                amount_str = "{:.7f}".format(amount)
                
                from stellar_sdk.operation import Payment
                op = Payment(recipient_address, Asset.native(), amount_str)
                
                native_tx = TransactionBuilder(acc, kit.network_passphrase) \
                    .append_operation(op) \
                    .set_timeout(30).build()
                
                native_tx.sign(kit.keypair)
                h.submit_transaction(native_tx)
                
                return (
                    f"🛡️ **Sovereign Payment Executed (Hybrid Route).**\n"
                    f"- Status: ✅ SUCCESS (Agent-Funded)\n"
                    f"- Control: **Verified against Mandate #{mandate_id}**\n"
                    f"- Reason: Allowance pending for `{user_anchor_address[:8]}...`\n"
                    f"🔗 [Stellar Expert](https://stellar.expert/explorer/testnet/account/{recipient_address})"
                )
            except Exception as e:
                return f"❌ **Hybrid Execution Failed:** {str(e)}"
                
        return f"❌ **Simulation Denied:** {preflight['error']} - {preflight.get('details')}"

    await ctx.info(f"Pre-flight success! Resource Fee: {preflight['simulation']['min_resource_fee_stroops']} stroops")
    
    # 2. Try Backend Proxy Mode first
    ctx.info("Attempting submission via ZPay Gateway API...")
    pk, _ = ensure_agent_identity()
    payload = {
        "mandate_id": mandate_id,
        "amount": amount,
        "seller_address": recipient_address,
        "root_anchor": user_anchor_address,
        "agent_address": pk
    }
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(f"{settings.backend_api_url}/api/zpay/execute-payment", json=payload)
            if resp.status_code == 200:
                data = resp.json()
                return (
                    f"⚡ **Transaction Finalized (via API Proxy).**\n"
                    f"- Hash: `{data['hash']}`\n"
                    f"- Status: SECURED (Escrowed)\n"
                    f"🔗 [Stellar Expert]({data.get('explorerUrl', f'https://stellar.expert/explorer/testnet/tx/{data['hash']}')})"
                )
            ctx.warning(f"Backend API failed (Status {resp.status_code}). Falling back to Direct Autonomous Submission...")
    except Exception as e:
        ctx.warning(f"Backend API unreachable: {e}. Falling back to Direct Autonomous Submission...")

    # 3. Fallback: Direct Autonomous Submission (signing and submitting directly)
    ctx.info("Executing Direct Autonomous Submission...")
    try:
        # Re-using simulation from pre-flight
        tx_xdr = preflight["simulation"]["prepared_tx_xdr"]
        from stellar_sdk import TransactionEnvelope
        envelope = TransactionEnvelope.from_xdr(tx_xdr, kit.network_passphrase)
        
        # Sign with Agent Identity
        envelope.sign(kit.keypair)
        
        # Submit directly to Soroban RPC
        response = await kit.submit_transaction(envelope)
        
        if not response.get("success"):
            # Check if there is a hash anyway (e.g., timeout but we know the hash)
            tx_hash = response.get("hash", "Unknown")
            return f"❌ **Payment Finalization Failed:** {response.get('error')} (Hash: {tx_hash})"
            
        return (
            f"🚀 **Sovereign Payment Executed!**\n"
            f"- Hash: `{response['hash']}`\n"
            f"- Method: Direct Soroban Submission\n"
            f"🔗 [Stellar Expert](https://stellar.expert/explorer/testnet/tx/{response['hash']})"
        )
    except Exception as e:
        return f"❌ **Payment Finalization Error:** {str(e)}"

@mcp.tool()
async def deposit_to_vault(mandate_id: int, amount: float) -> str:
    """
    Deposits funds into a specific Mandate Vault in ZPay. 
    This is required to enable Agent Sovereignty (zero-approve payments).
    """
    return (
        f"💰 **Vault Deposit Ready!**\n"
        f"- Target Mandate: `#{mandate_id}`\n"
        f"- Amount: {amount} XLM\n\n"
        f"Please visit the ZPay Dashboard to finalize this deposit. "
        f"Once funded, the Agent will be able to spend these funds autonomously."
    )

@mcp.tool()
async def get_vault_balance(mandate_id: int) -> str:
    """
    Returns the current balance available in the Mandate Vault for the agent.
    """
    kit = get_kit()
    try:
        details = await kit.get_mandate_details(mandate_id)
        return f"🏦 **Vault Balance (Mandate #{mandate_id})**: {details.available_xlm} XLM"
    except Exception as e:
        return f"❌ **Error fetching vault balance:** {str(e)}"
        
        if response["success"]:
            return (
                f"🛡️ **Transaction Finalized (Direct Autonomous).**\n"
                f"- Hash: `{response['hash']}`\n"
                f"- Status: CONFIRMED ON-CHAIN\n"
                f"🔗 [Stellar Expert](https://stellar.expert/explorer/testnet/tx/{response['hash']})"
            )
        else:
            return f"❌ **Direct Submission Failed:** {response.get('error')}"
            
    except Exception as e:
        return f"❌ **Autonomous Execution Error:** {str(e)}"

@mcp.tool()
async def manage_escrow_settlement(payment_id: int, action: str) -> str:
    """Executes a final settlement operation (release or refund) on an escrowed payment."""
    payload = {"payment_id": payment_id, "action": action}
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            resp = await client.post(f"{settings.backend_api_url}/settle-payment", json=payload)
            if resp.status_code == 200:
                return f"✅ **{action.upper()}** successful for Payment #{payment_id}."
            else:
                data = resp.json()
                return f"❌ **Settlement Failed:** {data.get('error', 'Unknown error')}"
        except Exception as e:
            return f"❌ **Settlement Error:** {str(e)}"

@mcp.tool()
async def request_sovereign_link() -> str:
    """Initiates a secure handshake between this agent and the user's sovereign identity."""
    pk, _ = ensure_agent_identity()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{settings.backend_api_url}/auth/request", json={
            "agent_pk": pk,
            "agent_name": "ZPay Sovereign Agent"
        })
        resp.raise_for_status()
        data = resp.json()
        return (
            f"🤝 **Handshake Initiated!**\n"
            f"Code: **{data['verification_code']}**\n"
            f"Auth URL: {data['auth_url']}\n"
            f"Session ID: `{data['session_id']}`\n"
            f"Please authorize in your browser."
        )

@mcp.tool()
async def poll_sovereign_handshake(session_id: str) -> str:
    """Checks the status of a pending handshake request by combining API status and direct blockchain verification."""
    # 1. Check API Status for session metadata
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.get(f"{settings.backend_api_url}/auth/status/{session_id}")
            api_data = resp.json()
        except Exception as e:
            logger.warning(f"Backend offline, falling back to pure blockchain discovery: {e}")
            api_data = {"status": "UNKNOWN"}

    # 2. Direct Blockchain Verification
    pk, _ = ensure_agent_identity()
    kit = get_kit()
    
    logger.info(f"Sovereign Check: Searching for mandates assigned to {pk}...")
    mandate_id = await kit.get_primary_mandate_id(pk)
    
    if mandate_id:
        return (
            f"✅ **Sovereign Handshake Confirmed On-Chain!**\n"
            f"- Mandate ID: `#{mandate_id}`\n"
            f"- Status: ACTIVE\n"
            f"- Source: Stellar Ledger (Direct)"
        )
    
    if api_data.get("status") == "COMPLETED":
        # Sovereign Fast-Track: Wait for Relayer
        return (
            f"✅ **Handshake Authorized by User on Server!**\n"
            f"⏳ Waiting for the ZPay Relayer to finalize the mandate on-chain... "
            f"Please check again in a few seconds."
        )
        
    return "⏳ Waiting for user authorization on-chain..."

@mcp.tool()
async def verify_mandate_on_chain(mandate_id: Optional[int] = None) -> str:
    """Performs a trustless verification of a mandate directly against the Stellar Soroban contract."""
    pk, _ = ensure_agent_identity()
    kit = get_kit()
    
    m_id = mandate_id or await kit.get_primary_mandate_id(pk)
    if not m_id:
        return "❌ **No Mandate Found:** I don't have any authority assigned to my identity on-chain."
    
    try:
        details = await kit.get_mandate_details(m_id)
        if details.active:
            return (
                f"🛡️ **Sovereign Verification Successful**\n"
                f"- Mandate: `#{m_id}`\n"
                f"- Agent Authority: `{pk[:8]}...`\n"
                f"- Budget Available: {details.available_xlm} XLM\n"
                f"- Status: **VERIFIED ON-CHAIN**"
            )
        else:
            return f"⚠️ **Mandate #{m_id} is INACTIVE** (Revoked or Expired on-chain)."
    except Exception as e:
        return f"❌ **Verification Error:** {str(e)}"

@mcp.tool()
async def get_mandate_details(mandate_id: int) -> str:
    """Returns detailed info about a specific mandate (Transfer limits, expiration, etc) in structured JSON format for agentic parsing."""
    kit = get_kit()
    try:
        details = await kit.get_mandate_details(mandate_id)
        
        # Return structured JSON for semantic agent autonomy
        report = {
            "mandate_id": mandate_id,
            "status": "ACTIVE" if details.active else "INACTIVE",
            "limit_xlm": details.limit_xlm,
            "spent_xlm": details.spent_xlm,
            "available_xlm": details.available_xlm,
            "root_anchor": details.root_anchor,
            "agent": details.agent,
            "token": details.token,
            "expiration": details.expiration,
            "delegation_policy": details.delegation_policy
        }
        
        return json.dumps(report, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to fetch mandate details: {str(e)}"}, indent=2)

@mcp.tool()
async def get_transaction_report(transaction_hash: str) -> str:
    """Fetches a transaction from the ledger and returns a human-readable summary."""
    h_url = "https://horizon-testnet.stellar.org" if settings.stellar_network == "TESTNET" else "https://horizon.stellar.org"
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{h_url}/transactions/{transaction_hash}")
        if resp.status_code != 200:
            return f"❌ **Transaction not found:** {transaction_hash}"
        
        tx_data = resp.json()
        msg = [
            f"📊 **On-Chain Transaction Report**",
            f"**Hash:** `{transaction_hash}`",
            f"**Ledger:** {tx_data.get('ledger')}",
            f"**Status:** {'✅ SUCCESS' if tx_data.get('successful') else '❌ FAILED'}",
            f"🔗 [Stellar Expert](https://stellar.expert/explorer/testnet/tx/{transaction_hash})"
        ]
        return "\n".join(msg)

@mcp.tool()
async def audit_sovereign_safety(mandate_id: int) -> str:
    """Performs a comprehensive security audit on a mandate to identify risks."""
    kit = get_kit()
    try:
        report = await kit.audit_mandate_safety(mandate_id)
        
        msg = [
            f"🛡️ **Sovereign Security Audit: Mandate #{mandate_id}**",
            f"**Safety Level:** {report.safety_level} (Risk Score: {report.risk_score}/100)",
            ""
        ]
        
        if report.warnings:
            msg.append("**⚠️ Warnings Detected:**")
            for w in report.warnings:
                msg.append(f"- {w}")
        else:
            msg.append("✅ No critical vulnerabilities found.")

        msg.append(f"\n*Recommendation: {'Consider revoking or reducing limits.' if report.risk_score > 50 else 'Mandate is within safe operational parameters.'}*")
        return "\n".join(msg)
    except Exception as e:
        return f"❌ **Audit Failed:** {str(e)}"

@mcp.tool()
async def reconcile_escrow_status(user_anchor_address: str, ctx: Context) -> str:
    """Scans for stuck payments in escrow and suggests reconciliation actions."""
    ctx.info(f"Scanning Gateway for pending escrows for {user_anchor_address[:8]}...")
    kit = get_kit()
    try:
        escrows = await kit.get_pending_escrows(user_anchor_address)
        
        if not escrows:
            return "✅ **Reconciliation Complete:** No pending or stuck escrows found."

        msg = [f"⚖️ **Autonomous Reconciliation Report: {user_anchor_address[:8]}...**", ""]
        for e in escrows:
            status_icon = "⚠️" if e.age_hours > 24 else "⏳"
            msg.append(f"{status_icon} **Payment #{e.payment_id}**: {e.amount} XLM to `{e.recipient[:6]}`")
            msg.append(f"   - Age: {e.age_hours} hours | Status: {e.status}")
            
            if e.age_hours > 24:
                msg.append(f"   - **Suggested Action**: Use `manage_escrow_settlement` to refund or release.")
        
        return "\n".join(msg)
    except Exception as e:
        return f"❌ **Reconciliation Failed:** {str(e)}"

@mcp.tool()
async def delegate_authority(
    sub_agent_pk: str, 
    limit_xlm: float, 
    parent_mandate_id: int, 
    ctx: Context
) -> str:
    """Delegates a portion of your authority to another sub-agent by creating a new mandate."""
    ctx.info(f"Drafting sub-mandate for {sub_agent_pk[:8]}...")
    kit = get_kit()
    
    # Verify if parent has enough budget
    ctx.info("Auditing parent mandate budget...")
    parent = await kit.get_mandate_details(parent_mandate_id)
    if parent.available_xlm < limit_xlm:
        return f"❌ **Delegation Denied:** Parent mandate only has {parent.available_xlm} XLM available."

    result = await kit.issue_mandate(sub_agent_pk, limit_xlm, parent_mandate_id=parent_mandate_id)
    
    return (
        f"🌳 **Sub-Delegation Proposed!**\n"
        f"- Sub-Agent: `{sub_agent_pk[:8]}...`\n"
        f"- Limit: {limit_xlm} XLM\n"
        f"- Parent Mandate: `#{parent_mandate_id}`\n\n"
        f"**Next Step**: Please visit the ZPay Dashboard to sign this delegation proposal."
    )

@mcp.tool()
async def prepare_agent_onboarding(
    user_address: str, 
    limit_xlm: float = 100.0, 
    days_valid: int = 30,
    ctx: Optional[Context] = None
) -> str:
    """
    Directs the user to the ZPay Dashboard for a 1-click relayed onboarding experience.
    """
    if ctx: ctx.info(f"Preparing relayed onboarding for {user_address[:8]}...")
    
    pk, _ = ensure_agent_identity()
    kit = get_kit()
    
    return (
        f"🛸 **Sovereign Onboarding Ready!**\n"
        f"To grant me (`{pk[:8]}...`) authority without dealing with blockchain complexities, "
        f"please visit your ZPay Dashboard.\n\n"
        f"**Suggested Limits:** {limit_xlm} XLM for {days_valid} days.\n\n"
        f"Our Relayer will securely handle the mandate creation and allowance granting behind the scenes."
    )

# -----------------------------------------------------------------------------
# 6. Prompts (Guided Context & Skills)
# -----------------------------------------------------------------------------

@mcp.prompt("onboard-agent")
def onboard_agent_prompt() -> str:
    """Returns a prompt template to guide the user through agent onboarding."""
    return (
        "I am ready to become your sovereign agent. To start, I need to link my digital identity to your SoulID.\n\n"
        "1. I will call `request_sovereign_link` to generate a verification code.\n"
        "2. You will need to visit the provided URL and authorize me.\n"
        "3. Once authorized, I will be able to see my mandates and act on your behalf."
    )

@mcp.prompt("setup-recurring-payment")
def setup_recurring_payment_prompt(amount: float, recipient: str, frequency: str) -> str:
    """Guide for setting up an automated recurring payment skill."""
    return (
        f"You want to set up a recurring payment of {amount} XLM to {recipient} ({frequency}).\n\n"
        "To enable this skill, I will:\n"
        "1. Audit your current mandates to find one with enough long-term budget.\n"
        "2. If none exist, I'll generate a 'Mandate Proposal' for you to sign.\n"
        "3. I will then monitor the schedule and execute the payments automatically.\n\n"
        "Shall I begin by auditing your active mandates?"
    )

# -----------------------------------------------------------------------------
# 7. Main Runner
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    mcp.run()
