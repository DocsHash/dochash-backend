import os
import json
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any

class ConfigLoader:
    @staticmethod
    def load_contract_abi() -> List[Dict[str, Any]]:
        """Load contract ABI from JSON file"""
        possible_paths = [
            Path("./app/artifacts/contracts/DocumentHash.sol/DocumentHash.json"),
            Path("./artifacts/contracts/DocumentHash.sol/DocumentHash.json"),
            Path("artifacts/contracts/DocumentHash.sol/DocumentHash.json")
        ]
        
        # Find first existing path
        artifact_path = next((p for p in possible_paths if p.exists()), None)
        if not artifact_path:
            searched_paths = [str(p) for p in possible_paths]
            raise FileNotFoundError(f"Файл артефакта не найден по путям: {searched_paths}")
        
        # Load and parse JSON
        with open(artifact_path, 'r', encoding='utf-8') as file:
            artifact_data = json.load(file)
        
        abi = artifact_data.get('abi')
        if not abi:
            raise ValueError("ABI не найден в файле артефакта")
        
        return abi

@dataclass
class AppConfig:
    """Application configuration"""
    DATABASE_URL: str
    BLOCKCHAIN_NETWORK: str
    CONTRACT_ADDRESS: str
    RPC_URL: str
    CORS_ORIGINS: List[str]
    DEBUG: bool
    LOG_LEVEL: str
    LAST_BLOCK_FILE: str
    CONTRACT_ABI: List[Dict[str, Any]]

class Config:
    def __init__(self):
        # Load configuration from environment
        self.config = AppConfig(
            DATABASE_URL=os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/document_hash"),
            BLOCKCHAIN_NETWORK=os.getenv("BLOCKCHAIN_NETWORK", "localhost"),
            CONTRACT_ADDRESS=os.getenv("CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3"),
            RPC_URL=os.getenv("RPC_URL", "http://127.0.0.1:8545"),
            CORS_ORIGINS=os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(","),
            DEBUG=os.getenv("DEBUG", "false").lower() == "true",
            LOG_LEVEL=os.getenv("LOG_LEVEL", "INFO"),
            LAST_BLOCK_FILE="data/last_block.txt",
            CONTRACT_ABI=ConfigLoader.load_contract_abi()
        )
    
    @property
    def DATABASE_URL(self) -> str:
        return self.config.DATABASE_URL
    
    @property
    def BLOCKCHAIN_NETWORK(self) -> str:
        return self.config.BLOCKCHAIN_NETWORK
    
    @property
    def CONTRACT_ADDRESS(self) -> str:
        return self.config.CONTRACT_ADDRESS
    
    @property
    def RPC_URL(self) -> str:
        return self.config.RPC_URL
    
    @property
    def CORS_ORIGINS(self) -> List[str]:
        return self.config.CORS_ORIGINS
    
    @property
    def DEBUG(self) -> bool:
        return self.config.DEBUG
    
    @property
    def LOG_LEVEL(self) -> str:
        return self.config.LOG_LEVEL
    
    @property
    def LAST_BLOCK_FILE(self) -> str:
        return self.config.LAST_BLOCK_FILE
    
    @property
    def CONTRACT_ABI(self) -> List[Dict[str, Any]]:
        return self.config.CONTRACT_ABI

# Singleton instance
config = Config()