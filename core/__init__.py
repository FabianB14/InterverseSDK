"""
Interverse SDK Core Module

This module contains the core functionality of the Interverse SDK,
providing interfaces to interact with the Interverse blockchain.
"""

import logging
from .chain import InterverseChain
from .asset import InterverseAsset, ItemCategory, Rarity, Color
from .wallet import InterverseWallet, WalletManager
from .types import (
    Transaction, 
    TransactionType, 
    TransactionStatus,
    GameLinkConfig,
    PlayerIdentity,
    GameRegistration,
    ChainResponse,
    ChainResponseStatus
)

# Configure logging
logger = logging.getLogger("interverse")
logger.setLevel(logging.INFO)

# Create console handler
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)

# Create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add handler to logger
logger.addHandler(handler)

__version__ = "0.1.0"
__all__ = [
    'InterverseChain',
    'InterverseAsset',
    'InterverseWallet',
    'WalletManager',
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
    'ChainResponseStatus'
]