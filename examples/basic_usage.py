#!/usr/bin/env python3
"""
Basic usage example for the Interverse SDK.

This example demonstrates how to initialize the SDK, create a wallet,
mint an asset, and transfer it to another wallet.
"""

import asyncio
import logging
import os
import sys

# Add parent directory to path to import the SDK
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from interverse import create_interverse_sdk
from interverse.core.asset import ItemCategory, Rarity, Color

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("interverse.example")

# Replace these with your actual credentials
GAME_ID = "your_game_id"
API_KEY = "your_api_key"
NODE_URL = "https://verse-coin-7b67e4d49b53.herokuapp.com"

async def main():
    """Main example function"""
    # Initialize SDK
    logger.info("Initializing Interverse SDK...")
    sdk = await create_interverse_sdk(
        game_id=GAME_ID,
        api_key=API_KEY,
        node_url=NODE_URL
    )
    
    try:
        # Create a wallet
        logger.info("Creating a wallet...")
        wallet_result = await sdk.create_wallet()
        if not wallet_result["success"]:
            logger.error(f"Failed to create wallet: {wallet_result.get('error', 'Unknown error')}")
            return
            
        wallet_address = wallet_result["wallet"]["address"]
        logger.info(f"Wallet created: {wallet_address}")
        
        # Get wallet balance
        logger.info("Checking wallet balance...")
        balance_result = await sdk.get_balance(wallet_address)
        if balance_result["success"]:
            logger.info(f"Wallet balance: {balance_result['balance']}")
        
        # Mint an asset
        logger.info("Minting an asset...")
        asset_properties = {
            "category": ItemCategory.WEAPON.value,
            "rarity": Rarity.LEGENDARY.value,
            "level": 50,
            "model_id": "sword_01",
            "primary_color": Color(1.0, 0.1, 0.1).to_dict(),  # Red
            "numeric_properties": {
                "damage": 100,
                "durability": 1000
            },
            "string_properties": {
                "effect": "fire_damage",
                "type": "sword"
            },
            "tags": ["fire", "melee", "two_handed"]
        }
        
        mint_result = await sdk.mint_asset(wallet_address, asset_properties)
        if not mint_result["success"]:
            logger.error(f"Failed to mint asset: {mint_result.get('error', 'Unknown error')}")
            return
            
        asset_id = mint_result["asset"]["asset_id"]
        logger.info(f"Asset minted: {asset_id}")
        
        # Create a second wallet for transfer demonstration
        logger.info("Creating a second wallet...")
        wallet2_result = await sdk.create_wallet()
        if not wallet2_result["success"]:
            logger.error(f"Failed to create second wallet: {wallet2_result.get('error', 'Unknown error')}")
            return
            
        wallet2_address = wallet2_result["wallet"]["address"]
        logger.info(f"Second wallet created: {wallet2_address}")
        
        # Transfer the asset to the second wallet
        logger.info(f"Transferring asset {asset_id} from {wallet_address} to {wallet2_address}...")
        transfer_result = await sdk.transfer_asset(asset_id, wallet_address, wallet2_address)
        if not transfer_result["success"]:
            logger.error(f"Failed to transfer asset: {transfer_result.get('error', 'Unknown error')}")
            return
            
        logger.info(f"Asset transferred successfully: {transfer_result}")
        
        # Get asset details
        logger.info(f"Getting details for asset {asset_id}...")
        asset_result = await sdk.get_asset(asset_id)
        if asset_result["success"]:
            logger.info(f"Asset details: {asset_result['asset']}")
        
        # Get player assets
        logger.info(f"Getting assets for wallet {wallet2_address}...")
        assets_result = await sdk.get_player_assets(wallet2_address)
        if assets_result["success"]:
            assets = assets_result["assets"]
            logger.info(f"Found {len(assets)} assets")
            for asset in assets:
                logger.info(f"  - {asset['asset_id']}: {asset.get('metadata', {}).get('type', 'Unknown')}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
    finally:
        # Clean up
        logger.info("Cleaning up...")
        await sdk.close()
        logger.info("Done!")

if __name__ == "__main__":
    asyncio.run(main())