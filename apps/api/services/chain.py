import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from config import settings

# ABI for ModelRegistry.registerModel(bytes32, string, string)
MODEL_REGISTRY_ABI = [
    {
        "inputs": [
            {"name": "contentHash", "type": "bytes32"},
            {"name": "modelSlug", "type": "string"},
            {"name": "licenseType", "type": "string"},
        ],
        "name": "registerModel",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function",
    },
    {
        "inputs": [{"name": "contentHash", "type": "bytes32"}],
        "name": "verifyModel",
        "outputs": [
            {"name": "modelSlug", "type": "string"},
            {"name": "licenseType", "type": "string"},
            {"name": "registrant", "type": "address"},
            {"name": "registeredAt", "type": "uint256"},
            {"name": "version", "type": "uint256"},
        ],
        "stateMutability": "view",
        "type": "function",
    },
]


async def register_model_onchain(
    model_id: uuid.UUID,
    model_slug: str,
    content_hash: str,
    license_type: str,
    db: AsyncSession,
):
    """Register model provenance on-chain. Runs as a background task."""
    if not settings.chain_private_key or not settings.model_registry_address:
        return  # Chain not configured, skip

    try:
        from web3 import Web3

        w3 = Web3(Web3.HTTPProvider(settings.chain_rpc_url))
        account = w3.eth.account.from_key(settings.chain_private_key)

        contract = w3.eth.contract(
            address=Web3.to_checksum_address(settings.model_registry_address),
            abi=MODEL_REGISTRY_ABI,
        )

        # Convert hex string to bytes32
        hash_bytes = bytes.fromhex(content_hash.replace("0x", ""))

        tx = contract.functions.registerModel(
            hash_bytes, model_slug, license_type
        ).build_transaction(
            {
                "from": account.address,
                "nonce": w3.eth.get_transaction_count(account.address),
                "gas": 200000,
                "maxFeePerGas": w3.eth.gas_price * 2,
                "maxPriorityFeePerGas": w3.eth.gas_price,
            }
        )

        signed = account.sign_transaction(tx)
        tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

        # Update model with on-chain data
        from models.model import Model

        result = await db.execute(select(Model).where(Model.id == model_id))
        model = result.scalar_one_or_none()
        if model:
            model.chain_tx_hash = receipt.transactionHash.hex()
            model.chain_block_number = receipt.blockNumber
            model.chain_contract_address = settings.model_registry_address
            model.provenance_registered_at = datetime.utcnow()
            await db.commit()

    except Exception as e:
        # Log but don't fail — on-chain registration is best-effort
        print(f"On-chain registration failed for {model_slug}: {e}")
