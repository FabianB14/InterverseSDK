from enum import Enum
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import json
import logging

from ...core.asset import Color

logger = logging.getLogger(__name__)

class MaterialProperty(Enum):
    """Standard material properties that can be controlled by styles"""
    DIFFUSE_COLOR = "diffuse_color"
    SPECULAR_COLOR = "specular_color"
    EMISSION_COLOR = "emission_color"
    METALLIC = "metallic"
    ROUGHNESS = "roughness"
    NORMAL_STRENGTH = "normal_strength"
    EMISSION_STRENGTH = "emission_strength"
    TRANSPARENCY = "transparency"

@dataclass
class MaterialStyle:
    """Represents a reusable material style that can be applied to assets"""
    id: str
    name: str
    description: str = ""
    
    # Visual property overrides
    texture_overrides: Dict[str, str] = field(default_factory=dict)
    color_overrides: Dict[str, Color] = field(default_factory=dict)
    numeric_parameters: Dict[str, float] = field(default_factory=dict)
    string_parameters: Dict[str, str] = field(default_factory=dict)
    
    # Tags for categorization and filtering
    tags: List[str] = field(default_factory=list)
    
    # Game-specific compatibility
    compatible_games: List[str] = field(default_factory=list)
    base_style: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert style to dictionary for API serialization"""
        color_dict = {}
        for key, color in self.color_overrides.items():
            color_dict[key] = color.to_dict() if hasattr(color, 'to_dict') else color
            
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "texture_overrides": self.texture_overrides,
            "color_overrides": color_dict,
            "numeric_parameters": self.numeric_parameters,
            "string_parameters": self.string_parameters,
            "tags": self.tags,
            "compatible_games": self.compatible_games,
            "base_style": self.base_style
        }
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return json.dumps(self.to_dict())
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MaterialStyle':
        """Create style from dictionary"""
        # Process color overrides to convert them to Color objects
        color_overrides = {}
        if "color_overrides" in data:
            for key, color_data in data["color_overrides"].items():
                if isinstance(color_data, dict):
                    color_overrides[key] = Color.from_dict(color_data)
                else:
                    color_overrides[key] = color_data
                    
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            description=data.get("description", ""),
            texture_overrides=data.get("texture_overrides", {}),
            color_overrides=color_overrides,
            numeric_parameters=data.get("numeric_parameters", {}),
            string_parameters=data.get("string_parameters", {}),
            tags=data.get("tags", []),
            compatible_games=data.get("compatible_games", []),
            base_style=data.get("base_style")
        )
    
    @classmethod
    def from_json(cls, json_str: str) -> 'MaterialStyle':
        """Create style from JSON string"""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON for style: {e}")
            raise ValueError(f"Invalid JSON format: {e}")

class MaterialStylesExtension:
    """
    Extension that adds material style functionality to the SDK.
    
    This extension enables:
    - Material style registration and management
    - Applying styles to assets
    - Converting styles between games
    """
    
    def __init__(self, sdk):
        self.sdk = sdk
        self.registered_styles: Dict[str, MaterialStyle] = {}
        self.style_mappings: Dict[str, Dict[str, str]] = {}
        logger.info("Material Styles Extension initialized")
    
    async def register_style(self, style: MaterialStyle) -> bool:
        """Register a new material style"""
        if not style.id:
            logger.error("Style must have an ID")
            return False
            
        # Store locally
        self.registered_styles[style.id] = style
        
        # Register on blockchain if connected
        try:
            if self.sdk.chain.is_connected:
                await self.sdk.chain.http_session.post(
                    f"{self.sdk.chain.node_url}/verse/material_styles/register",
                    json=style.to_dict(),
                    headers={"X-API-Key": self.sdk.chain.api_key, "Content-Type": "application/json"}
                )
                logger.info(f"Registered style on blockchain: {style.id}")
        except Exception as e:
            logger.error(f"Failed to register style on blockchain: {e}")
            # Continue even if blockchain registration failed - we still have it locally
        
        logger.info(f"Material style registered: {style.id}")
        return True
    
    def get_style(self, style_id: str) -> Optional[MaterialStyle]:
        """Get a registered style by ID"""
        return self.registered_styles.get(style_id)
    
    def get_all_styles(self) -> List[MaterialStyle]:
        """Get all registered styles"""
        return list(self.registered_styles.values())
    
    def get_styles_by_tag(self, tag: str) -> List[MaterialStyle]:
        """Get all styles with a specific tag"""
        return [
            style for style in self.registered_styles.values()
            if tag in style.tags
        ]
    
    def get_styles_for_game(self, game_id: str) -> List[MaterialStyle]:
        """Get all styles compatible with a specific game"""
        return [
            style for style in self.registered_styles.values()
            if not style.compatible_games or game_id in style.compatible_games
        ]
    
    def register_style_mapping(self, source_game: str, target_game: str, source_style: str, target_style: str) -> None:
        """Register a style mapping between games"""
        if source_game not in self.style_mappings:
            self.style_mappings[source_game] = {}
            
        if target_game not in self.style_mappings[source_game]:
            self.style_mappings[source_game][target_game] = {}
            
        self.style_mappings[source_game][target_game][source_style] = target_style
        logger.info(f"Registered style mapping: {source_game}.{source_style} -> {target_game}.{target_style}")
    
    def get_mapped_style(self, source_game: str, target_game: str, source_style: str) -> Optional[str]:
        """Get the mapped style ID for a target game"""
        try:
            return self.style_mappings[source_game][target_game][source_style]
        except KeyError:
            return None
    
    async def apply_style_to_asset(self, asset_id: str, style_id: str) -> Dict[str, Any]:
        """Apply a style to an existing asset"""
        style = self.get_style(style_id)
        if not style:
            logger.error(f"Style not found: {style_id}")
            return {"success": False, "error": f"Style not found: {style_id}"}
            
        try:
            # Get the current asset
            asset_response = await self.sdk.chain.get_asset(asset_id)
            if not asset_response.get("success", False):
                return {"success": False, "error": "Failed to retrieve asset"}
                
            asset = asset_response.get("asset", {})
            
            # Update asset properties with style
            # Note: This implementation assumes your blockchain supports asset updates
            properties = asset.copy()
            
            # Apply style properties
            if "primary_color" in style.color_overrides:
                properties["primary_color"] = style.color_overrides["primary_color"].to_dict()
                
            if "secondary_color" in style.color_overrides:
                properties["secondary_color"] = style.color_overrides["secondary_color"].to_dict()
                
            # Apply numeric parameters
            if "numeric_properties" not in properties:
                properties["numeric_properties"] = {}
                
            for key, value in style.numeric_parameters.items():
                properties["numeric_properties"][key] = value
                
            # Apply string parameters
            if "string_properties" not in properties:
                properties["string_properties"] = {}
                
            for key, value in style.string_parameters.items():
                properties["string_properties"][key] = value
                
            # Add style reference
            if "string_properties" not in properties:
                properties["string_properties"] = {}
                
            properties["string_properties"]["applied_style"] = style_id
            
            # Update the asset on blockchain
            update_response = await self.sdk.chain.update_asset(asset_id, properties)
            
            return update_response
        except Exception as e:
            logger.error(f"Error applying style: {e}")
            return {"success": False, "error": str(e)}
    
    async def create_asset_with_style(self, owner_address: str, base_properties: Dict[str, Any], style_id: str) -> Dict[str, Any]:
        """Create a new asset with a style applied"""
        style = self.get_style(style_id)
        if not style:
            logger.error(f"Style not found: {style_id}")
            return {"success": False, "error": f"Style not found: {style_id}"}
            
        try:
            # Clone base properties
            properties = base_properties.copy()
            
            # Apply style properties
            if "primary_color" in style.color_overrides:
                properties["primary_color"] = style.color_overrides["primary_color"].to_dict()
                
            if "secondary_color" in style.color_overrides:
                properties["secondary_color"] = style.color_overrides["secondary_color"].to_dict()
                
            # Apply numeric parameters
            if "numeric_properties" not in properties:
                properties["numeric_properties"] = {}
                
            for key, value in style.numeric_parameters.items():
                properties["numeric_properties"][key] = value
                
            # Apply string parameters
            if "string_properties" not in properties:
                properties["string_properties"] = {}
                
            for key, value in style.string_parameters.items():
                properties["string_properties"][key] = value
                
            # Add style reference
            properties["string_properties"]["applied_style"] = style_id
            
            # Create the asset on blockchain
            return await self.sdk.chain.mint_asset(owner_address, properties)
        except Exception as e:
            logger.error(f"Error creating asset with style: {e}")
            return {"success": False, "error": str(e)}