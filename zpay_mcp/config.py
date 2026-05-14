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
    contract_id_nexus: str
    contract_id_gateway: str
    contract_id_identity: Optional[str] = None

    # Backend Configuration
    backend_api_url: str = "http://localhost:3000/api/zpay"
    
    # Identity Configuration
    agent_identity_pk: Optional[str] = None
    agent_identity_sk: Optional[str] = None
    
    # Path Configuration
    config_dir: Path = Path.home() / ".config" / "zolvency"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        env_prefix="ZPAY_"
    )

    def ensure_dirs(self):
        self.config_dir.mkdir(parents=True, exist_ok=True)

settings = ZPaySettings()
settings.ensure_dirs()
