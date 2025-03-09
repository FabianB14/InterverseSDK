"""
Interverse SDK

A Python SDK for interacting with the Interverse blockchain,
enabling cross-game asset transfers and blockchain operations.
"""

import logging
import asyncio
from typing import Dict, Any, Optional, List, Callable, Union

from .core import (
    InterverseChain,
    InterverseAsset,
    InterverseWallet,
    WalletManager,
    ItemCategory,
    Rarity,
    Color,
    Transaction,
    TransactionType,
    TransactionStatus,
    GameLinkConfig,
    PlayerIdentity,
    GameRegistration,
    ChainResponse,
    ChainResponseStatus
)

__version__ = "0.1.0"

class Interverse:
    """
    Main entry point for the Interverse SDK.
    
    This class provides a simplified interface to interact with the Interverse
    blockchain, manage wallets, and handle cross-game asset transfers.
    """
    
    def __init__(
        self, 
        game_id: str = "", 
        api_key: str = "", 
        node_url: str = "https://verse-coin-7b67e4d49b53.herokuapp.com"
    ):
        """
        Initialize the Interverse SDK.
        
        Args:
            game_id: The ID of your game
            api_key: Your API key for the Interverse blockchain
            node_url: The URL of the Interverse blockchain node
        """
        self.chain = InterverseChain(node_url=node_url, game_id=game_id, api_key=api_key)
        self.wallet_manager = WalletManager(self.chain)
        self._initialized = False
        self._connected = False
        
        # Configure logging
        self.logger = logging.getLogger("interverse")
    
    async def initialize(self) -> bool:
        """
        Initialize the SDK and required components.
        
        Returns:
            bool: True if initialization was successful, False otherwise
        """
        try:
            if await self.chain.initialize():
                self._initialized = True
                # Load existing wallets
                self.wallet_manager.storage.load_wallets()
                return True
            return False
        except Exception as e:
            self.logger.error(f"Initialization error: {e}")
            return False
    
    async def connect(self) -> bool:
        """
        Connect to the Interverse blockchain.
        
        Returns:
            bool: True if connection was successful, False otherwise
        """
        if not self._initialized:
            if not await self.initialize():
                return False
                
        try:
            if await self.chain.connect():
                self._connected = True
                return True
            return False
        except Exception as e:
            self.logger.error(f"Connection error: {e}")
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the Interverse blockchain."""
        try:
            await self.chain.disconnect()
            self._connected = False
        except Exception as e:
            self.logger.error(f"Disconnect error: {e}")
    
    async def close(self) -> None:
        """Close all connections and resources."""
        try:
            await self.disconnect()
            await self.chain.close()
        except Exception as e:
            self.logger.error(f"Close error: {e}")
    
    def on(self, event_name: str, callback: Callable) -> None:
        """
        Register an event handler.
        
        Args:
            event_name: Name of the event to listen for
            callback: Function to call when the event occurs
        """
        self.chain.on(event_name, callback)
    
    def off(self, event_name: str, callback: Callable) -> None:
        """
        Remove an event handler.
        
        Args:
            event_name: Name of the event
            callback: Function to remove
        """
        self.chain.off(event_name, callback)
    
    async def create_wallet(self) -> Dict[str, Any]:
        """
        Create a new wallet on the blockchain.
        
        Returns:
            Dict containing wallet information if successful
        """
        success, wallet, error = await self.wallet_manager.create_wallet()
        if success and wallet:
            return {
                "success": True,
                "wallet": {
                    "address": wallet.address,
                    "balance": wallet.balance,
                    "created_at": wallet.created_at.isoformat()
                }
            }
        return {
            "success": False,
            "error": error
        }
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """
        Get the balance of a wallet.
        
        Args:
            address: Wallet address
            
        Returns:
            Dict containing balance information
        """
        return await self.chain.get_balance(address)
    
    async def mint_asset(self, owner_address: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mint a new asset on the blockchain.
        
        Args:
            owner_address: Address of the asset owner
            properties: Asset properties
            
        Returns:
            Dict containing the minted asset information
        """
        return await self.chain.mint_asset(owner_address, properties)
    
    async def transfer_asset(self, asset_id: str, from_address: str, to_address: str) -> Dict[str, Any]:
        """
        Transfer an asset between wallets.
        
        Args:
            asset_id: ID of the asset to transfer
            from_address: Sender wallet address
            to_address: Recipient wallet address
            
        Returns:
            Dict containing transfer result
        """
        return await self.chain.transfer_asset(asset_id, from_address, to_address)
    
    async def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """
        Get details of a specific asset.
        
        Args:
            asset_id: ID of the asset
            
        Returns:
            Dict containing asset details
        """
        return await self.chain.get_asset(asset_id)
    
    async def get_player_assets(self, address: str) -> Dict[str, Any]:
        """
        Get all assets owned by a player.
        
        Args:
            address: Player wallet address
            
        Returns:
            Dict containing list of assets
        """
        return await self.chain.get_player_assets(address)
    
    async def update_asset(self, asset_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update properties of an existing asset.
        
        Args:
            asset_id: ID of the asset to update
            properties: New asset properties
            
        Returns:
            Dict containing update result
        """
        return await self.chain.update_asset(asset_id, properties)
    
    async def get_transaction_history(self, address: str) -> Dict[str, Any]:
        """
        Get transaction history for an address.
        
        Args:
            address: Wallet address
            
        Returns:
            Dict containing transaction history
        """
        return await self.chain.get_transaction_history(address)
    
    async def verify_game(self) -> Dict[str, Any]:
        """
        Verify game registration with the blockchain.
        
        Returns:
            Dict containing verification result
        """
        return await self.chain.verify_game()

async def create_interverse_sdk(game_id: str, api_key: str, node_url: str = "https://verse-coin-7b67e4d49b53.herokuapp.com") -> Interverse:
    """
    Factory function to create and initialize an Interverse SDK instance.
    
    Args:
        game_id: The ID of your game
        api_key: Your API key for the Interverse blockchain
        node_url: The URL of the Interverse blockchain node
        
    Returns:
        Initialized Interverse SDK instance
    """
    sdk = Interverse(game_id=game_id, api_key=api_key, node_url=node_url)
    await sdk.initialize()
    await sdk.connect()
    return sdk

__all__ = [
    'Interverse',
    'create_interverse_sdk',
    'InterverseChain',
    'InterverseAsset',
    'InterverseWallet',
    'ItemCategory',
    'Rarity',
    'Color',
    'Transaction',
    'TransactionType',
    'TransactionStatus',
    'GameLinkConfig',
    'PlayerIdentity',
    'GameRegistration',
    'ChainResponse',
    'ChainResponseStatus',
]