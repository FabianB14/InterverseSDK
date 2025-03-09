from enum import Enum
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass, field
import json
from datetime import datetime

class TransactionType(str, Enum):
    """Types of transactions supported by the blockchain"""
    TRANSFER = "TRANSFER"
    MINT = "MINT"
    BURN = "BURN"
    STAKE = "STAKE"
    GAME_REWARD = "GAME_REWARD"
    VESTING_RELEASE = "VESTING_RELEASE"
    AUTOMATIC_VESTING_RELEASE = "AUTOMATIC_VESTING_RELEASE"
    MULTI_SIG = "MULTI_SIG"
    GAME_ASSET = "GAME_ASSET"
    
    @classmethod
    def from_string(cls, type_str: str) -> 'TransactionType':
        """Convert string to TransactionType enum"""
        type_str = type_str.upper()
        for tx_type in cls:
            if tx_type.value == type_str:
                return tx_type
        return cls.TRANSFER  # Default to TRANSFER if not found

class TransactionStatus(str, Enum):
    """Status of a transaction on the blockchain"""
    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    REVERTED = "reverted"
    
    @classmethod
    def from_string(cls, status_str: str) -> 'TransactionStatus':
        """Convert string to TransactionStatus enum"""
        status_str = status_str.lower()
        for status in cls:
            if status.value == status_str:
                return status
        return cls.PENDING  # Default to PENDING if not found

@dataclass
class Transaction:
    """Represents a blockchain transaction"""
    id: str
    sender_address: str
    recipient_address: str
    amount: float
    transaction_type: TransactionType
    status: TransactionStatus
    timestamp: datetime
    metadata: Dict[str, Any] = field(default_factory=dict)
    block_number: Optional[int] = None
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Transaction':
        """Create transaction from dictionary"""
        # Parse timestamp
        timestamp = datetime.utcnow()
        if "timestamp" in data:
            try:
                if isinstance(data["timestamp"], str):
                    timestamp = datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
                elif isinstance(data["timestamp"], (int, float)):
                    timestamp = datetime.fromtimestamp(data["timestamp"])
            except Exception:
                pass
                
        # Parse transaction type
        try:
            tx_type = TransactionType.from_string(data.get("transaction_type", "TRANSFER"))
        except Exception:
            tx_type = TransactionType.TRANSFER
            
        # Parse status
        try:
            status = TransactionStatus.from_string(data.get("status", "pending"))
        except Exception:
            status = TransactionStatus.PENDING
        
        return cls(
            id=data.get("id", ""),
            sender_address=data.get("sender_address", ""),
            recipient_address=data.get("recipient_address", ""),
            amount=float(data.get("amount", 0.0)),
            transaction_type=tx_type,
            status=status,
            timestamp=timestamp,
            metadata=data.get("metadata", {}),
            block_number=data.get("block_number")
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "sender_address": self.sender_address,
            "recipient_address": self.recipient_address,
            "amount": self.amount,
            "transaction_type": self.transaction_type.value,
            "status": self.status.value,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata,
            "block_number": self.block_number
        }

@dataclass
class GameLinkConfig:
    """Configuration for linking games together"""
    source_game_id: str
    target_game_id: str
    allow_direct_transfers: bool = True
    asset_mappings: Dict[str, str] = field(default_factory=dict)
    property_conversions: Dict[str, Dict[str, float]] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "source_game_id": self.source_game_id,
            "target_game_id": self.target_game_id,
            "allow_direct_transfers": self.allow_direct_transfers,
            "asset_mappings": self.asset_mappings,
            "property_conversions": self.property_conversions
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameLinkConfig':
        """Create from dictionary"""
        return cls(
            source_game_id=data.get("source_game_id", ""),
            target_game_id=data.get("target_game_id", ""),
            allow_direct_transfers=data.get("allow_direct_transfers", True),
            asset_mappings=data.get("asset_mappings", {}),
            property_conversions=data.get("property_conversions", {})
        )

@dataclass
class PlayerIdentity:
    """Player identity information"""
    global_id: str
    game_specific_id: str
    display_name: str
    last_active: datetime = field(default_factory=datetime.utcnow)
    game_metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "global_id": self.global_id,
            "game_specific_id": self.game_specific_id,
            "display_name": self.display_name,
            "last_active": self.last_active.isoformat(),
            "game_metadata": self.game_metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerIdentity':
        """Create from dictionary"""
        # Parse datetime
        last_active = datetime.utcnow()
        if "last_active" in data:
            try:
                if isinstance(data["last_active"], str):
                    last_active = datetime.fromisoformat(data["last_active"].replace('Z', '+00:00'))
            except Exception:
                pass
                
        return cls(
            global_id=data.get("global_id", ""),
            game_specific_id=data.get("game_specific_id", ""),
            display_name=data.get("display_name", ""),
            last_active=last_active,
            game_metadata=data.get("game_metadata", {})
        )

@dataclass
class GameRegistration:
    """Game registration information"""
    game_id: str
    developer_name: str
    game_name: str
    api_key: str
    status: str = "active"
    created_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "game_id": self.game_id,
            "developer_name": self.developer_name,
            "game_name": self.game_name,
            "api_key": self.api_key,
            "status": self.status,
            "created_at": self.created_at.isoformat(),
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameRegistration':
        """Create from dictionary"""
        # Parse datetime
        created_at = datetime.utcnow()
        if "created_at" in data:
            try:
                if isinstance(data["created_at"], str):
                    created_at = datetime.fromisoformat(data["created_at"].replace('Z', '+00:00'))
            except Exception:
                pass
                
        return cls(
            game_id=data.get("game_id", ""),
            developer_name=data.get("developer_name", ""),
            game_name=data.get("game_name", ""),
            api_key=data.get("api_key", ""),
            status=data.get("status", "active"),
            created_at=created_at,
            metadata=data.get("metadata", {})
        )

class ChainResponseStatus(str, Enum):
    """Status codes for chain responses"""
    SUCCESS = "success"
    ERROR = "error"
    PENDING = "pending"

@dataclass
class ChainResponse:
    """Standardized response format for chain operations"""
    status: ChainResponseStatus
    message: str
    data: Optional[Dict[str, Any]] = None
    error_code: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = {
            "status": self.status.value,
            "message": self.message
        }
        
        if self.data:
            result["data"] = self.data
            
        if self.error_code:
            result["error_code"] = self.error_code
            
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def success(cls, message: str = "Operation successful", data: Optional[Dict[str, Any]] = None) -> 'ChainResponse':
        """Create a success response"""
        return cls(
            status=ChainResponseStatus.SUCCESS,
            message=message,
            data=data
        )
    
    @classmethod
    def error(cls, message: str, error_code: Optional[str] = None, data: Optional[Dict[str, Any]] = None) -> 'ChainResponse':
        """Create an error response"""
        return cls(
            status=ChainResponseStatus.ERROR,
            message=message,
            error_code=error_code,
            data=data
        )
    
    @classmethod
    def pending(cls, message: str = "Operation pending", data: Optional[Dict[str, Any]] = None) -> 'ChainResponse':
        """Create a pending response"""
        return cls(
            status=ChainResponseStatus.PENDING,
            message=message,
            data=data
        )