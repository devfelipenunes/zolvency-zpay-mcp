import asyncio
import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path to import zpay_python
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from zpay_python.zpay.agent_kit import ZPayAgentKit

async def main():
    load_dotenv()
    # Initialize the kit with the same parameters as the MCP server
    kit = ZPayAgentKit(
        rpc_url=os.getenv("ZPAY_STELLAR_RPC_URL", "https://soroban-testnet.stellar.org"),
        network_passphrase=os.getenv("ZPAY_STELLAR_NETWORK_PASSPHRASE", "Test SDF Network ; September 2015"),
        nexus_id=os.getenv("ZPAY_CONTRACT_ID_NEXUS"),
        zpay_id=os.getenv("ZPAY_CONTRACT_ID_GATEWAY"),
        soul_id=os.getenv("ZPAY_CONTRACT_ID_IDENTITY"),
        debug=True
    )
    
    print(f"🤖 My Identity: {kit.keypair.public_key}")
    print("🔍 Scanning for authorized mandates...")
    
    # We use the scan method we just implemented
    mandates = await kit.scan_agent_mandates()
    
    if not mandates:
        print("❌ No mandates found on-chain for this agent identity.")
    else:
        print(f"✅ Found {len(mandates)} mandate(s):")
        for m in mandates:
            print(f"- Mandate #{m['mandate_id']}: {m['status']}")
            # Let's try to get more details for each
            details = await kit.get_mandate_details(m['mandate_id'])
            print(f"  Limit: {details.get('limit')} {details.get('currency')}")

if __name__ == "__main__":
    asyncio.run(main())
