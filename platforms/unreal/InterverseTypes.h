#pragma once

#include "CoreMinimal.h"
#include "InterverseTypes.generated.h"

UENUM(BlueprintType)
enum class EInterverseItemCategory : uint8
{
    Weapon      UMETA(DisplayName = "Weapon"),
    Armor       UMETA(DisplayName = "Armor"),
    Accessory   UMETA(DisplayName = "Accessory"),
    Consumable  UMETA(DisplayName = "Consumable"),
    Currency    UMETA(DisplayName = "Currency"),
    Cosmetic    UMETA(DisplayName = "Cosmetic"),
    Mount       UMETA(DisplayName = "Mount"),
    Pet         UMETA(DisplayName = "Pet")
};

UENUM(BlueprintType)
enum class EInterverseRarity : uint8
{
    Common      UMETA(DisplayName = "Common"),
    Uncommon    UMETA(DisplayName = "Uncommon"),
    Rare        UMETA(DisplayName = "Rare"),
    Epic        UMETA(DisplayName = "Epic"),
    Legendary   UMETA(DisplayName = "Legendary"),
    Mythic      UMETA(DisplayName = "Mythic")
};

USTRUCT(BlueprintType)
struct INTERVERSESDK_API FInterverseBaseProperties
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    EInterverseItemCategory Category;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    EInterverseRarity Rarity;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    int32 Level;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString ModelIdentifier;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FLinearColor PrimaryColor;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FLinearColor SecondaryColor;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    TMap<FString, float> NumericProperties;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    TMap<FString, FString> StringProperties;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    TArray<FString> Tags;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString OwnerGlobalID;  // Player global ID

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString TargetPlayerID;  // For transfers

    bool IsValid() const
    {
        return !ModelIdentifier.IsEmpty();
    }
};

// Complete asset representation
USTRUCT(BlueprintType)
struct INTERVERSESDK_API FInterverseAsset
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString AssetId;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString Owner;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString OwnerGlobalID;  // Player global ID

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    EInterverseItemCategory Category;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    EInterverseRarity Rarity;

    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    TMap<FString, FString> Metadata;
    
    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FString GameId;
    
    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FDateTime CreatedAt;
    
    UPROPERTY(BlueprintReadWrite, Category = "Interverse")
    FDateTime ModifiedAt;
};

// Player identity representation
USTRUCT(BlueprintType)
struct INTERVERSESDK_API FInterversePlayerID
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Player")
    FString GlobalPlayerID;

    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Player")
    FString CurrentGameID;

    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Player")
    FString PlayerName;

    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Player")
    FString LastKnownGameID;

    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Player")
    FDateTime LastActiveTime;
};

// Wallet representation
USTRUCT(BlueprintType)
struct INTERVERSESDK_API FInterverseWallet
{
    GENERATED_BODY()
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Wallet")
    FString Address;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Wallet")
    float Balance;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Wallet")
    FString PublicKey;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Wallet")
    FDateTime CreatedAt;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Wallet")
    FDateTime LastUpdated;
};

// Transaction representation
USTRUCT(BlueprintType)
struct INTERVERSESDK_API FInterverseTransaction
{
    GENERATED_BODY()
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    FString Id;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    FString SenderAddress;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    FString RecipientAddress;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    float Amount;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    FString TransactionType;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    FString Status;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    FDateTime Timestamp;
    
    UPROPERTY(BlueprintReadOnly, Category = "Interverse|Transaction")
    TMap<FString, FString> Metadata;
};