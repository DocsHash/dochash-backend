import os
from typing import List

import json
import os
from pathlib import Path


def load_contract_abi():
    try:
        possible_paths = [
            Path("./app/artifacts/contracts/DocumentHash.sol/DocumentHash.json"),
            Path("./artifacts/contracts/DocumentHash.sol/DocumentHash.json"),
            Path("artifacts/contracts/DocumentHash.sol/DocumentHash.json")
        ]

        artifact_path = None
        for path in possible_paths:
            if path.exists():
                artifact_path = path
                break

        if not artifact_path:
            searched_paths = [str(p) for p in possible_paths]
            raise FileNotFoundError(f"Файл артефакта не найден по путям: {searched_paths}")

        with open(artifact_path, 'r', encoding='utf-8') as file:
            artifact_data = json.load(file)

        abi = artifact_data.get('abi')
        if not abi:
            raise ValueError("ABI не найден в файле артефакта")

        return abi
    except Exception as e:
        raise RuntimeError(f"Ошибка загрузки ABI: {str(e)}")




class Config:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/document_hash")
    BLOCKCHAIN_NETWORK: str = os.getenv("BLOCKCHAIN_NETWORK", "localhost")
    CONTRACT_ADDRESS: str = os.getenv("CONTRACT_ADDRESS", "0x5FbDB2315678afecb367f032d93F642f64180aa3")
    RPC_URL: str = os.getenv("RPC_URL", "http://127.0.0.1:8545")
    CORS_ORIGINS: List[str] = os.getenv("CORS_ORIGINS", "http://localhost:3000,http://localhost:3001").split(",")
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LAST_BLOCK_FILE: str = "data/last_block.txt"


    CONTRACT_ABI = load_contract_abi()


config = Config()