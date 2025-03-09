# Interverse SDK

A cross-platform SDK for interacting with the Interverse blockchain platform, enabling seamless cross-game asset transfers and management.

## Installation

### Python (Core)
```bash
pip install interverse-sdk
```

### Unreal Engine
Add the `InterverseSDK` plugin to your project's `Plugins` directory.

### Unity
Import the `Interverse SDK for Unity` package from the Asset Store or add the files directly to your project.

### RPG Maker
Add the `interverse-rpgmaker.js` plugin to your project's `js/plugins` directory.

## Quick Start

### Python

```python
import asyncio
from interverse import create_interverse_sdk, ItemCategory, Rarity, Color

async def main():
    # Initialize SDK
    sdk = await create_interverse_sdk(
        game_id="your_game_id",
        api_key="your_api_key"
    )
    
    # Create a wallet
    wallet_result = await sdk.create_wallet()
    if wallet_result["success"]:
        print(f"Wallet created: {wallet_result['wallet']['address']}")
    
    # Mint an asset
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
    
    mint_result = await sdk.mint_asset(wallet_result["wallet"]["address"], asset_properties)
    if mint_result["success"]:
        print(f"Asset minted: {mint_result['asset']['asset_id']}")
    
    # Clean up
    await sdk.close()

if __name__ == "__main__":
    asyncio.run(main())
```

### Unreal Engine (C++)

```cpp
// Example of integrating Interverse SDK in Unreal Engine

void AMyGameCharacter::SendItemToBlockchain()
{
    // 1. Get the Interverse component
    UInterverseSDKComponent* InterverseSDK = GetComponentByClass<UInterverseSDKComponent>();
    if (!InterverseSDK) return;
    
    // 2. Get the item from player inventory
    UInventoryItem* Item = Inventory->GetSelectedItem();
    if (!Item) return;
    
    // 3. Convert item to Interverse properties format
    FInterverseBaseProperties ItemProps;
    ItemProps.Category = ConvertItemTypeToCategory(Item->Type);
    ItemProps.Rarity = ConvertQualityToRarity(Item->Quality);
    ItemProps.Level = Item->Level;
    ItemProps.ModelIdentifier = Item->ModelId;
    ItemProps.NumericProperties.Add("Damage", Item->Damage);
    ItemProps.NumericProperties.Add("Durability", Item->Durability);
    ItemProps.StringProperties.Add("Effect", Item->EffectType);
    
    // 4. Mint the asset on blockchain
    InterverseSDK->MintGameAsset(PlayerState->WalletAddress, ItemProps, TMap<FString, FString>());
    
    // Log and notify player
    UE_LOG(LogInterverse, Log, TEXT("Sending item %s to blockchain"), *Item->GetName());
    ShowNotification(TEXT("Item is being minted on the blockchain..."));
}
```

### Unity (C#)

```csharp
// Example of integrating Interverse SDK in Unity

public void TransferItemToAnotherGame()
{
    // 1. Get references
    var interverse = InterverseManager.Instance;
    var inventory = PlayerInventory.Instance;
    var selectedItem = inventory.SelectedItem;
    
    // 2. Check if connected
    if (!interverse.IsConnected)
    {
        interverse.ConnectWebSocket();
        StartCoroutine(WaitForConnectionAndTransfer());
        return;
    }
    
    // 3. Create the asset properties
    var itemProps = new InterverseAssetProperties
    {
        category = ConvertItemTypeToCategory(selectedItem.type),
        rarity = ConvertQualityToRarity(selectedItem.quality),
        level = selectedItem.level,
        model_id = selectedItem.prefabPath,
        numeric_properties = new Dictionary<string, float>
        {
            { "damage", selectedItem.damage },
            { "durability", selectedItem.durability }
        },
        string_properties = new Dictionary<string, string>
        {
            { "effect", selectedItem.effectType }
        }
    };
    
    // 4. Transfer the asset
    interverse.TransferAsset(selectedItem.assetId, PlayerData.WalletAddress, TargetGamePlayerId,
        success => { ShowNotification(success ? "Item transferred!" : "Transfer failed!"); });
}
```

### RPG Maker (JavaScript)

```javascript
// Example of integrating Interverse SDK in RPG Maker

// Function to equip blockchain items as game items
function equipBlockchainItem(assetId) {
    // 1. Get the player and Interverse SDK
    const player = $gameParty.leader();
    if (!Interverse.isConnected) {
        Interverse.connect().then(connected => {
            if (connected) equipBlockchainItem(assetId);
        });
        return;
    }
    
    // 2. Get player wallet from game system
    const wallet = $gameSystem.getInterverseWallet();
    if (!wallet) {
        $gameMessage.add("No wallet found. Please create a wallet first.");
        return;
    }
    
    // 3. Get all player's assets
    Interverse.getPlayerAssets(wallet.address).then(assets => {
        // 4. Find the specific asset
        const asset = assets.find(a => a.asset_id === assetId);
        if (!asset) {
            $gameMessage.add("Asset not found in your wallet!");
            return;
        }
        
        // 5. Convert to game item and equip
        const gameItem = createGameItemFromAsset(asset);
        if (gameItem) {
            player.changeEquip(gameItem.etypeId, gameItem.id);
            $gameMessage.add(`Equipped ${gameItem.name} from blockchain!`);
        }
    });
}
```

## Features

- **Cross-Game Asset Management**: Transfer and transform assets between different games
- **Wallet Management**: Create and manage blockchain wallets
- **Asset Minting**: Create new game assets on the blockchain
- **Asset Transfers**: Transfer assets between players
- **Real-time Updates**: WebSocket connection for instant notifications
- **Extension System**: Add custom functionality through extensions

## Type Classes

Each platform implementation includes standardized type classes to ensure consistent asset representation:

### Python Core Types
- `ItemCategory`: Standard categories across games (Weapon, Armor, etc.)
- `Rarity`: Standard rarity levels (Common, Rare, etc.)
- `Color`: RGBA color representation
- `InterverseAsset`: Complete asset representation
- `Transaction`: Blockchain transaction representation

### Unreal Engine Types
- `EInterverseItemCategory`: Enum for item categories
- `EInterverseRarity`: Enum for rarity levels
- `FInterverseBaseProperties`: Struct for asset properties
- `FInterverseAsset`: Struct for complete asset representation
- `FInterversePlayerID`: Player identity representation

### Unity Types
- `InterverseItemCategory`: Item category enum
- `InterverseRarity`: Rarity level enum
- `InterverseAssetProperties`: Class for asset properties
- `InterverseAsset`: Class for complete asset representation
- `InterversePlayerIdentity`: Player identity representation

### RPG Maker Types
- `InterverseAsset`: JavaScript object with asset properties
- `InterverseWallet`: JavaScript object with wallet properties
- `InterversePlayer`: JavaScript object with player information

## Extensions

Interverse SDK supports extensions to add additional functionality:

### Material Styles Extension

```python
from interverse.extensions.material_styles import MaterialStylesExtension, MaterialStyle
from interverse.extensions.material_styles.material_extension import MaterialProperty

# Enable extension
material_ext = MaterialStylesExtension(sdk)

# Create a style
fire_style = MaterialStyle(
    id="fire_style",
    name="Fiery",
    description="A fiery red style with glowing effects",
    texture_overrides={
        "diffuse": "textures/fire_diffuse.png",
        "normal": "textures/fire_normal.png"
    },
    color_overrides={
        "primary": Color(1.0, 0.2, 0.1),  # Red
        "secondary": Color(1.0, 0.8, 0.0)  # Yellow
    },
    numeric_parameters={
        "emission_strength": 2.0,
        "heat_factor": 1.5
    }
)

# Register style
await material_ext.register_style(fire_style)

# Apply style to an asset
result = await material_ext.apply_style_to_asset("asset_id_123", "fire_style")
```

## Complete Example: Material Styles

Here's a complete example of using the Material Styles extension to create themed weapons:

```python
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
    
    # Register styles
    await material_ext.register_style(fire_style)
    await material_ext.register_style(ice_style)
    
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
    else:
        print(f"Failed to create fire sword: {fire_sword_result.get('error', 'Unknown error')}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Documentation

Complete API documentation is available at [Coming soon](https://docs.interverse.io)

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Contributing

We welcome contributions! Please see [Coming soon](CONTRIBUTING.md) for details.