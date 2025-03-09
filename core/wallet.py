import json
import os
import base64
import hashlib
import logging
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime

logger = logging.getLogger("interverse.wallet")

class InterverseWallet:
    """Wallet management for Interverse chain"""
    
    def __init__(
        self, 
        address: str = "",
        balance: float = 0.0,
        public_key: str = "",
        private_key: str = "",
        created_at: Optional[datetime] = None
    ):
        self.address = address
        self.balance = balance
        self.public_key = public_key
        self._private_key = private_key  # Store privately
        self.created_at = created_at or datetime.utcnow()
        self.last_updated = datetime.utcnow()
        self.transactions: List[Dict[str, Any]] = []
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterverseWallet':
        """Create wallet from dictionary data"""
        created_at = None
        if "created_at" in data:
            try:
                if isinstance(data["created_at"], str):
                    created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
                elif isinstance(data["created_at"], (int, float)):
                    created_at = datetime.fromtimestamp(data["created_at"])
            except Exception as e:
                logger.warning(f"Error parsing created_at: {e}")
                
        return cls(
            address=data.get("address", ""),
            balance=float(data.get("balance", 0.0)),
            public_key=data.get("public_key", ""),
            private_key=data.get("private_key", ""),
            created_at=created_at
        )
    
    def to_dict(self, include_private: bool = False) -> Dict[str, Any]:
        """Convert wallet to dictionary"""
        result = {
            "address": self.address,
            "balance": self.balance,
            "public_key": self.public_key,
            "created_at": self.created_at.isoformat(),
            "last_updated": self.last_updated.isoformat()
        }
        
        if include_private and self._private_key:
            result["private_key"] = self._private_key
            
        return result
    
    def to_json(self, include_private: bool = False) -> str:
        """Convert wallet to JSON string"""
        return json.dumps(self.to_dict(include_private=include_private))
    
    @property
    def has_private_key(self) -> bool:
        """Check if wallet has private key"""
        return bool(self._private_key)
    
    def update_balance(self, new_balance: float) -> None:
        """Update wallet balance"""
        self.balance = float(new_balance)
        self.last_updated = datetime.utcnow()
    
    def add_transaction(self, transaction: Dict[str, Any]) -> None:
        """Add transaction to wallet history"""
        self.transactions.append(transaction)
        
        # Update balance if transaction has amount
        if "amount" in transaction:
            if transaction.get("type") == "TRANSFER" and transaction.get("sender") == self.address:
                self.balance -= float(transaction["amount"])
            elif transaction.get("recipient") == self.address:
                self.balance += float(transaction["amount"])
                
        self.last_updated = datetime.utcnow()
    
    def clear_private_key(self) -> None:
        """Clear private key from memory for security"""
        self._private_key = ""


class WalletStorage:
    """Handles secure storage of wallet information"""
    
    def __init__(self, storage_dir: str = None):
        # Default to user's home directory if not specified
        if storage_dir is None:
            home_dir = os.path.expanduser("~")
            self.storage_dir = os.path.join(home_dir, ".interverse", "wallets")
        else:
            self.storage_dir = storage_dir
            
        # Create directory if it doesn't exist
        os.makedirs(self.storage_dir, exist_ok=True)
        
        self.wallets: Dict[str, InterverseWallet] = {}
    
    def load_wallets(self, password: Optional[str] = None) -> int:
        """Load all wallets from storage"""
        count = 0
        try:
            for filename in os.listdir(self.storage_dir):
                if filename.endswith('.json'):
                    wallet_path = os.path.join(self.storage_dir, filename)
                    try:
                        with open(wallet_path, 'r') as f:
                            wallet_data = json.load(f)
                            
                        # Handle encrypted files
                        if wallet_data.get("encrypted", False) and password:
                            wallet_data = self._decrypt_wallet_data(wallet_data, password)
                            
                        wallet = InterverseWallet.from_dict(wallet_data)
                        self.wallets[wallet.address] = wallet
                        count += 1
                            
                    except Exception as e:
                        logger.error(f"Error loading wallet {filename}: {e}")
        except Exception as e:
            logger.error(f"Error loading wallets: {e}")
            
        return count
    
    def save_wallet(self, wallet: InterverseWallet, password: Optional[str] = None) -> bool:
        """Save wallet to storage"""
        try:
            wallet_data = wallet.to_dict(include_private=True)
            
            # Encrypt if password provided
            if password:
                wallet_data = self._encrypt_wallet_data(wallet_data, password)
            
            filename = f"{wallet.address}.json"
            wallet_path = os.path.join(self.storage_dir, filename)
            
            with open(wallet_path, 'w') as f:
                json.dump(wallet_data, f, indent=2)
                
            # Add to memory cache
            self.wallets[wallet.address] = wallet
            return True
                
        except Exception as e:
            logger.error(f"Error saving wallet {wallet.address}: {e}")
            return False
    
    def get_wallet(self, address: str) -> Optional[InterverseWallet]:
        """Get wallet by address"""
        return self.wallets.get(address)
    
    def get_all_wallets(self) -> List[InterverseWallet]:
        """Get all loaded wallets"""
        return list(self.wallets.values())
    
    def delete_wallet(self, address: str) -> bool:
        """Delete wallet from storage"""
        try:
            if address in self.wallets:
                del self.wallets[address]
                
            filename = f"{address}.json"
            wallet_path = os.path.join(self.storage_dir, filename)
            
            if os.path.exists(wallet_path):
                os.remove(wallet_path)
                return True
            return False
                
        except Exception as e:
            logger.error(f"Error deleting wallet {address}: {e}")
            return False
    
    def _encrypt_wallet_data(self, wallet_data: Dict[str, Any], password: str) -> Dict[str, Any]:
        """Encrypt wallet data with password"""
        # Simple encryption for demonstration
        # In production, use a proper encryption library
        
        # Generate key from password
        key = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            b'interverse-salt', 
            100000
        )
        
        # Convert wallet data to string
        data_str = json.dumps(wallet_data)
        
        # XOR encryption (very basic, for demonstration only)
        key_bytes = key
        data_bytes = data_str.encode('utf-8')
        encrypted_bytes = bytearray()
        
        for i in range(len(data_bytes)):
            encrypted_bytes.append(data_bytes[i] ^ key_bytes[i % len(key_bytes)])
        
        # Return encrypted data
        return {
            "encrypted": True,
            "data": base64.b64encode(encrypted_bytes).decode('utf-8')
        }
    
    def _decrypt_wallet_data(self, encrypted_data: Dict[str, Any], password: str) -> Dict[str, Any]:
        """Decrypt wallet data with password"""
        # Generate key from password
        key = hashlib.pbkdf2_hmac(
            'sha256', 
            password.encode('utf-8'), 
            b'interverse-salt', 
            100000
        )
        
        # Decode encrypted data
        encrypted_bytes = base64.b64decode(encrypted_data.get("data", ""))
        
        # XOR decryption
        key_bytes = key
        decrypted_bytes = bytearray()
        
        for i in range(len(encrypted_bytes)):
            decrypted_bytes.append(encrypted_bytes[i] ^ key_bytes[i % len(key_bytes)])
        
        # Convert back to dictionary
        return json.loads(decrypted_bytes.decode('utf-8'))


class WalletManager:
    """Manages wallets and interfaces with blockchain"""
    
    def __init__(self, chain, storage_dir: Optional[str] = None):
        self.chain = chain  # InterverseChain instance
        self.storage = WalletStorage(storage_dir)
        self.active_wallet: Optional[InterverseWallet] = None
    
    async def create_wallet(self) -> Tuple[bool, Optional[InterverseWallet], str]:
        """Create a new wallet"""
        try:
            # Request wallet creation from blockchain
            result = await self.chain.create_wallet()
            
            if not result.get("success", False):
                return False, None, result.get("error", "Wallet creation failed")
                
            wallet_data = result.get("wallet", {})
            
            # Create wallet object
            wallet = InterverseWallet(
                address=wallet_data.get("address", ""),
                balance=float(wallet_data.get("balance", 0.0)),
                public_key=wallet_data.get("public_key", ""),
                created_at=datetime.utcnow()
            )
            
            # Store wallet
            self.storage.save_wallet(wallet)
            
            return True, wallet, ""
            
        except Exception as e:
            logger.error(f"Error creating wallet: {e}")
            return False, None, str(e)
    
    async def load_wallet(self, address: str) -> Tuple[bool, Optional[InterverseWallet], str]:
        """Load a wallet and update its balance"""
        try:
            # Load from storage
            wallet = self.storage.get_wallet(address)
            if not wallet:
                return False, None, f"Wallet {address} not found"
                
            # Update balance from blockchain
            balance_result = await self.chain.get_balance(address)
            
            if balance_result.get("success", False):
                wallet.update_balance(balance_result.get("balance", wallet.balance))
                
            # Set as active wallet
            self.active_wallet = wallet
            
            return True, wallet, ""
            
        except Exception as e:
            logger.error(f"Error loading wallet {address}: {e}")
            return False, None, str(e)
    
    async def get_active_wallet(self) -> Optional[InterverseWallet]:
        """Get the currently active wallet"""
        if self.active_wallet:
            # Update balance
            balance_result = await self.chain.get_balance(self.active_wallet.address)
            
            if balance_result.get("success", False):
                self.active_wallet.update_balance(balance_result.get("balance", self.active_wallet.balance))
                
        return self.active_wallet
    
    def set_active_wallet(self, address: str) -> bool:
        """Set the active wallet by address"""
        wallet = self.storage.get_wallet(address)
        if wallet:
            self.active_wallet = wallet
            return True
        return False
    
    async def update_balances(self) -> Dict[str, float]:
        """Update balances for all wallets"""
        updated_balances = {}
        
        for address, wallet in self.storage.wallets.items():
            try:
                balance_result = await self.chain.get_balance(address)
                
                if balance_result.get("success", False):
                    new_balance = balance_result.get("balance", wallet.balance)
                    wallet.update_balance(new_balance)
                    updated_balances[address] = new_balance
                    
            except Exception as e:
                logger.error(f"Error updating balance for {address}: {e}")
                
        return updated_balances
    
    async def update_transactions(self, address: Optional[str] = None) -> int:
        """Update transaction history for a wallet or all wallets"""
        count = 0
        
        if address:
            # Update specific wallet
            wallet = self.storage.get_wallet(address)
            if wallet:
                count += await self._update_wallet_transactions(wallet)
        else:
            # Update all wallets
            for wallet in self.storage.get_all_wallets():
                count += await self._update_wallet_transactions(wallet)
                
        return count
    
    async def _update_wallet_transactions(self, wallet: InterverseWallet) -> int:
        """Update transactions for a specific wallet"""
        try:
            tx_result = await self.chain.get_transaction_history(wallet.address)
            
            if not tx_result.get("success", False):
                return 0
                
            transactions = tx_result.get("transactions", [])
            
            # Clear existing transactions and add new ones
            wallet.transactions = []
            for tx in transactions:
                wallet.add_transaction(tx)
                
            return len(transactions)
            
        except Exception as e:
            logger.error(f"Error updating transactions for {wallet.address}: {e}")
            return 0