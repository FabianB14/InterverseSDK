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