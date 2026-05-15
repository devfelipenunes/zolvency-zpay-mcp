import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional

class ZPaySettings(BaseSettings):
    # Stellar Configuration
    stellar_network: str = "TESTNET"
    stellar_rpc_url: str = "https://soroban-testnet.stellar.org"
    stellar_horizon_url: str = "https://horizon-testnet.stellar.org"
    stellar_network_passphrase: str = "Test SDF Network ; September 2015"

    # Contract IDs
    contract_id_nexus: str = "CDT2JUGATFANH3NN6XKBRVPXD3Y3I5K7FIAR6CTA3XUM4VVBV4BEN4U7"
    contract_id_gateway: str = "CAQHJPCHL72ZP45LNOLXSIZQET7R2XEH65VYTQCKMZ2DVHJ6O5DIZ5IE"
    contract_id_identity: Optional[str] = "CAO7GUDIMPJFR2QZROJPBKIDBLNXNACMEGYV36XPQTV5IAPSKCMHGHDJ"
    contract_id_direct_sovereign: Optional[str] = "CDIC65LUXGRZHU2FHIB7OJSVQCB7NIVVOD2DJUQWTWJQYKBVETUREYA7"

    # Backend Configuration
    backend_api_url: str = "http://localhost:3000/api/zpay"
    
    # Identity Configuration
    agent_identity_pk: Optional[str] = None
    agent_identity_sk: Optional[str] = None
    
    # Path Configuration
    config_dir: Path = Path.home() / ".config" / "zolvency"
    project_root: Path = Path(__file__).parent.parent.parent.parent
    registry_path: Path = project_root / "contracts" / "registry.json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="ZPAY_"
    )

    def model_post_init(self, __context):
        """Override settings with values from registry.json if available."""
        self.ensure_dirs()
        if self.registry_path.exists():
            try:
                import json
                with open(self.registry_path, "r") as f:
                    registry = json.load(f)
                
                # Priority: Registry > Env Vars > Defaults
                if "NEXUS_CONTRACT_ID" in registry:
                    self.contract_id_nexus = registry["NEXUS_CONTRACT_ID"]
                if "SOUL_CONTRACT_ID" in registry:
                    self.contract_id_identity = registry["SOUL_CONTRACT_ID"]
                if "ZPAY_CONTRACT_ID" in registry:
                    self.contract_id_gateway = registry["ZPAY_CONTRACT_ID"]
                if "DIRECT_SOVEREIGN_ID" in registry:
                    self.contract_id_direct_sovereign = registry["DIRECT_SOVEREIGN_ID"]
                    
            except Exception as e:
                # Fallback to env vars if registry fails
                pass

    def ensure_dirs(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

settings = ZPaySettings()
settings.ensure_dirs()
