import os
import sys
from dotenv import load_dotenv

# Add project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from zpay_python.zpay.agent_kit import ZPayAgentKit

load_dotenv()

RPC_URL = os.getenv("ZPAY_STELLAR_RPC_URL", "https://soroban-testnet.stellar.org")
NETWORK_PASSPHRASE = os.getenv("ZPAY_STELLAR_NETWORK_PASSPHRASE", "Test SDF Network ; September 2015")
CONTRACT_NEXUS = os.getenv("ZPAY_CONTRACT_ID_NEXUS")
CONTRACT_GATEWAY = os.getenv("ZPAY_CONTRACT_ID_GATEWAY")
CONTRACT_IDENTITY = os.getenv("ZPAY_CONTRACT_ID_IDENTITY")

try:
    kit = ZPayAgentKit(
        rpc_url=RPC_URL,
        network_passphrase=NETWORK_PASSPHRASE,
        nexus_id=CONTRACT_NEXUS,
        zpay_id=CONTRACT_GATEWAY,
        soul_id=CONTRACT_IDENTITY
    )
    print("SUCCESS: ZPayAgentKit initialized correctly.")
    print(f"Agent PK: {kit.keypair.public_key}")
except Exception as e:
    print(f"FAILURE: {e}")
