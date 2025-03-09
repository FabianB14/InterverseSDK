from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import logging

logger = logging.getLogger("interverse.asset")

class ItemCategory(str, Enum):
    """Standard item categories across all games"""
    WEAPON = "weapon"
    ARMOR = "armor"
    ACCESSORY = "accessory"
    CONSUMABLE = "consumable"
    CURRENCY = "currency"
    COSMETIC = "cosmetic"
    MOUNT = "mount"
    PET = "pet"
    
    @classmethod
    def from_string(cls, category_str: str) -> 'ItemCategory':
        """Convert string to ItemCategory enum"""
        category_str = category_str.lower()
        for category in cls:
            if category.value.lower() == category_str:
                return category
        return cls.COSMETIC  # Default to COSMETIC if not found

class Rarity(str, Enum):
    """Standard rarity levels across all games"""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"
    
    @classmethod
    def from_string(cls, rarity_str: str) -> 'Rarity':
        """Convert string to Rarity enum"""
        rarity_str = rarity_str.lower()
        for rarity in cls:
            if rarity.value.lower() == rarity_str:
                return rarity
        return cls.COMMON  # Default to COMMON if not found

@dataclass
class Color:
    """RGBA color representation"""
    r: float = 1.0
    g: float = 1.0
    b: float = 1.0
    a: float = 1.0
    
    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary for API serialization"""
        return {
            "r": self.r,
            "g": self.g,
            "b": self.b,
            "a": self.a
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, float]) -> 'Color':
        """Create Color from dictionary"""
        return cls(
            r=float(data.get("r", 1.0)),
            g=float(data.get("g", 1.0)),
            b=float(data.get("b", 1.0)),
            a=float(data.get("a", 1.0))
        )
    
    @classmethod
    def from_hex(cls, hex_color: str) -> 'Color':
        """Create Color from hex string (e.g., '#FF0000' for red)"""
        hex_color = hex_color.lstrip('#')
        
        if len(hex_color) == 3:  # Shorthand #RGB
            r = int(hex_color[0] + hex_color[0], 16) / 255.0
            g = int(hex_color[1] + hex_color[1], 16) / 255.0
            b = int(hex_color[2] + hex_color[2], 16) / 255.0
            return cls(r=r, g=g, b=b)
            
        elif len(hex_color) == 6:  # Standard #RRGGBB
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return cls(r=r, g=g, b=b)
            
        elif len(hex_color) == 8:  # #RRGGBBAA with alpha
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            a = int(hex_color[6:8], 16) / 255.0
            return cls(r=r, g=g, b=b, a=a)
            
        else:
            raise ValueError(f"Invalid hex color format: {hex_color}")
    
    def to_hex(self, include_alpha: bool = False) -> str:
        """Convert to hex string"""
        if include_alpha:
            return f"#{int(self.r * 255):02x}{int(self.g * 255):02x}{int(self.b * 255):02x}{int(self.a * 255):02x}"
        else:
            return f"#{int(self.r * 255):02x}{int(self.g * 255):02x}{int(self.b * 255):02x}"

@dataclass
class InterverseAsset:
    """Standard asset representation across all platforms"""
    # Required identifiers
    asset_id: Optional[str] = None
    owner: Optional[str] = None
    game_id: Optional[str] = None
    
    # Basic properties
    category: ItemCategory = ItemCategory.COSMETIC
    rarity: Rarity = Rarity.COMMON
    level: int = 1
    model_id: str = ""
    
    # Visual properties
    primary_color: Color = field(default_factory=Color)
    secondary_color: Color = field(default_factory=Color)
    
    # Extended properties
    numeric_properties: Dict[str, float] = field(default_factory=dict)
    string_properties: Dict[str, str] = field(default_factory=dict)
    tags: List[str] = field(default_factory=list)
    
    # Cross-game metadata
    source_game: Optional[str] = None
    conversion_history: List[Dict[str, Any]] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for blockchain transactions"""
        result = {
            "category": self.category.value,
            "rarity": self.rarity.value,
            "level": self.level,
            "model_id": self.model_id,
            "primary_color": self.primary_color.to_dict(),
            "secondary_color": self.secondary_color.to_dict(),
            "numeric_properties": self.numeric_properties,
            "string_properties": self.string_properties,
            "tags": self.tags
        }
        
        # Add optional fields if they exist
        if self.asset_id:
            result["asset_id"] = self.asset_id
        if self.owner:
            result["owner"] = self.owner
        if self.game_id:
            result["game_id"] = self.game_id
        if self.source_game:
            result["source_game"] = self.source_game
        if self.conversion_history:
            result["conversion_history"] = self.conversion_history
            
        return result
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'InterverseAsset':
        """Create asset from dictionary"""
        # Process nested objects
        primary_color = Color.from_dict(data.get("primary_color", {})) if "primary_color" in data else Color()
        secondary_color = Color.from_dict(data.get("secondary_color", {})) if "secondary_color" in data else Color()
        
        # Handle category and rarity
        category_str = data.get("category", "cosmetic")
        rarity_str = data.get("rarity", "common")
        
        try:
            category = ItemCategory.from_string(category_str)
        except Exception as e:
            logger.warning(f"Invalid category: {category_str}, using default")
            category = ItemCategory.COSMETIC
            
        try:
            rarity = Rarity.from_string(rarity_str)
        except Exception as e:
            logger.warning(f"Invalid rarity: {rarity_str}, using default")
            rarity = Rarity.COMMON
        
        # Create asset object
        return cls(
            asset_id=data.get("asset_id"),
            owner=data.get("owner"),
            game_id=data.get("game_id"),
            category=category,
            rarity=rarity,
            level=int(data.get("level", 1)),
            model_id=data.get("model_id", ""),
            primary_color=primary_color,
            secondary_color=secondary_color,
            numeric_properties=data.get("numeric_properties", {}),
            string_properties=data.get("string_properties", {}),
            tags=data.get("tags", []),
            source_game=data.get("source_game"),
            conversion_history=data.get("conversion_history", [])
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'InterverseAsset':
        """Create asset from JSON string"""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for asset: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
    
    @classmethod
    def from_blockchain_format(cls, blockchain_data: Dict[str, Any]) -> 'InterverseAsset':
        """Create asset from blockchain API response format"""
        try:
            # Handle different possible response formats
            
            # If data is already in our format
            if "category" in blockchain_data:
                return cls.from_dict(blockchain_data)
                
            # If data is in the format returned by the Heroku API
            metadata = blockchain_data.get("metadata", {})
            if isinstance(metadata, dict):
                # Merge the metadata with the base data
                combined_data = {**blockchain_data, **metadata}
                return cls.from_dict(combined_data)
                
            # If we can't determine the format, use raw data
            asset = cls(
                asset_id=blockchain_data.get("id") or blockchain_data.get("asset_id"),
                owner=blockchain_data.get("owner") or blockchain_data.get("owner_address"),
                game_id=blockchain_data.get("game_id")
            )
            
            # Store the original data in string properties for reference
            asset.string_properties["_original_data"] = json.dumps(blockchain_data)
            return asset
            
        except Exception as e:
            logger.error(f"Error converting blockchain data: {e}")
            # Return minimal asset with original data preserved
            asset = cls()
            asset.string_properties["_original_data"] = json.dumps(blockchain_data)
            return asset
    
    def get_numeric_property(self, name: str, default: float = 0.0) -> float:
        """Get a numeric property with default fallback"""
        return self.numeric_properties.get(name, default)
    
    def get_string_property(self, name: str, default: str = "") -> str:
        """Get a string property with default fallback"""
        return self.string_properties.get(name, default)
    
    def set_numeric_property(self, name: str, value: float) -> None:
        """Set a numeric property"""
        self.numeric_properties[name] = float(value)
    
    def set_string_property(self, name: str, value: str) -> None:
        """Set a string property"""
        self.string_properties[name] = str(value)
    
    def add_tag(self, tag: str) -> None:
        """Add a tag if it doesn't exist"""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> None:
        """Remove a tag if it exists"""
        if tag in self.tags:
            self.tags.remove(tag)
    
    def has_tag(self, tag: str) -> bool:
        """Check if asset has a specific tag"""
        return tag in self.tags
    
    def add_conversion_record(self, from_game: str, to_game: str, timestamp: Optional[str] = None) -> None:
        """Add a record of asset conversion between games"""
        import datetime
        
        # Use current time if not provided
        if timestamp is None:
            timestamp = datetime.datetime.utcnow().isoformat()
            
        self.conversion_history.append({
            "from_game": from_game,
            "to_game": to_game,
            "timestamp": timestamp
        })
        
        # Update source game to the original if this is the first conversion
        if not self.source_game and len(self.conversion_history) == 1:
            self.source_game = from_game