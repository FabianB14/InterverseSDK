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