# This example shows how to use the Material Styles extension for Interverse SDK to create and apply material styles to game assets.
"""
Example showing how to use the Material Styles extension
for Interverse SDK to create and apply material styles to game assets.
"""

import asyncio
from interverse import create_interverse_sdk, ItemCategory, Rarity, Color
from interverse.extensions.material_styles import MaterialStylesExtension, MaterialStyle

async def main():
    # Initialize SDK
    sdk = await create_interverse_sdk(
        game_id="fantasy_quest",
        api_key="your_api_key"
    )
    
    # Enable Material Styles extension
    material_ext = MaterialStylesExtension(sdk)
    
    # Create a new player wallet
    wallet_result = await sdk.create_wallet()
    if wallet_result["success"]:
        player_address = wallet_result["wallet"]["address"]
        print(f"Created wallet: {player_address}")
    else:
        print("Failed to create wallet")
        return
    
    # Define material styles
    
    # 1. Fire style
    fire_style = MaterialStyle(
        id="fire_style",
        name="Fiery",
        description="A fiery red style with glowing effects",
        texture_overrides={
            "diffuse": "textures/fire_diffuse.png",
            "normal": "textures/fire_normal.png"
        },
        color_overrides={
            "primary": Color(1.0, 0.2, 0.1, 1.0),  # Red
            "secondary": Color(1.0, 0.8, 0.0, 1.0)  # Yellow
        },
        numeric_parameters={
            "emission_strength": 2.0,
            "heat_factor": 1.5
        },
        tags=["fire", "elemental", "glowing"]
    )
    
    # 2. Ice style
    ice_style = MaterialStyle(
        id="ice_style",
        name="Frozen",
        description="A chilling ice style with frost effects",
        texture_overrides={
            "diffuse": "textures/ice_diffuse.png",
            "normal": "textures/ice_normal.png"
        },
        color_overrides={
            "primary": Color(0.8, 0.9, 1.0, 1.0),  # Light blue
            "secondary": Color(0.4, 0.6, 0.9, 1.0)  # Medium blue
        },
        numeric_parameters={
            "roughness": 0.1,
            "metallic": 0.8,
            "cold_factor": 1.5
        },
        tags=["ice", "elemental", "shiny"]
    )
    
    # 3. Shadow style
    shadow_style = MaterialStyle(
        id="shadow_style",
        name="Shadow",
        description="A dark, shadowy style with smoky effects",
        texture_overrides={
            "diffuse": "textures/shadow_diffuse.png",
            "normal": "textures/shadow_normal.png"
        },
        color_overrides={
            "primary": Color(0.1, 0.1, 0.2, 1.0),  # Dark blue
            "secondary": Color(0.2, 0.0, 0.3, 0.8)  # Purple with transparency
        },
        numeric_parameters={
            "roughness": 0.7,
            "metallic": 0.0,
            "shadowiness": 0.8
        },
        tags=["shadow", "dark", "ethereal"]
    )
    
    # Register styles
    await material_ext.register_style(fire_style)
    await material_ext.register_style(ice_style)
    await material_ext.register_style(shadow_style)
    
    print("Registered material styles")
    
    # Create an asset with base properties
    sword_properties = {
        "category": ItemCategory.WEAPON.value,
        "rarity": Rarity.RARE.value,
        "level": 30,
        "model_id": "sword_01",
        "numeric_properties": {
            "damage": 75,
            "durability": 800
        },
        "string_properties": {
            "type": "sword",
            "effect": "none"
        },
        "tags": ["melee", "two_handed"]
    }
    
    # Create a sword asset with the fire style
    print("Creating fire sword...")
    fire_sword_result = await material_ext.create_asset_with_style(
        player_address, 
        sword_properties,
        "fire_style"
    )
    
    if fire_sword_result["success"]:
        fire_sword_id = fire_sword_result["asset"]["id"]
        print(f"Created fire sword: {fire_sword_id}")
        
        # Modify sword properties to make it an ice sword
        ice_sword_properties = sword_properties.copy()
        ice_sword_properties["string_properties"]["effect"] = "ice"
        ice_sword_properties["numeric_properties"]["damage"] = 65  # Less damage but...
        ice_sword_properties["numeric_properties"]["critical_chance"] = 15  # Higher crit chance
        
        # Create an ice sword
        print("Creating ice sword...")
        ice_sword_result = await material_ext.create_asset_with_style(
            player_address, 
            ice_sword_properties,
            "ice_style"
        )
        
        if ice_sword_result["success"]:
            ice_sword_id = ice_sword_result["asset"]["id"]
            print(f"Created ice sword: {ice_sword_id}")
            
            # Get all player assets
            player_assets = await sdk.get_player_assets(player_address)
            print(f"Player has {len(player_assets['assets'])} assets")
            
            # Show available styles
            print("\nAvailable styles:")
            for style in material_ext.get_all_styles():
                print(f"- {style.name}: {style.description}")
            
            # Apply shadow style to the ice sword as an example of changing styles
            print("\nTransforming ice sword to shadow sword...")
            shadow_result = await material_ext.apply_style_to_asset(ice_sword_id, "shadow_style")
            
            if shadow_result["success"]:
                print("Ice sword transformed to shadow sword!")
            else:
                print(f"Failed to apply shadow style: {shadow_result.get('error', 'Unknown error')}")
        else:
            print(f"Failed to create ice sword: {ice_sword_result.get('error', 'Unknown error')}")
    else:
        print(f"Failed to create fire sword: {fire_sword_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())