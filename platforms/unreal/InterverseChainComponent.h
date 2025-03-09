// platforms/unreal/InterverseSDKComponent.h
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "InterverseTypes.h"
#include "InterverseSDKComponent.generated.h"

// Delegate declarations
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnWebSocketConnected, bool, Success);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnWebSocketMessage, const FString&, Message);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAssetMinted, const FInterverseAsset&, Asset, const FString&, OwnerID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTransferComplete, const FString&, AssetId, const FString&, PlayerID, bool, Success);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnBalanceUpdated, float, NewBalance);

UCLASS(ClassGroup=(Interverse), meta=(BlueprintSpawnableComponent))
class INTERVERSESDK_API UInterverseSDKComponent : public UActorComponent
{
    GENERATED_BODY()

public:    
    UInterverseSDKComponent();

    virtual void BeginPlay() override;
    virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

    // Configuration properties
    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interverse|Configuration")
    FString NodeUrl = TEXT("https://verse-coin-7b67e4d49b53.herokuapp.com");

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interverse|Configuration")
    FString GameId;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Interverse|Configuration")
    FString ApiKey;

    // Blockchain functions
    UFUNCTION(BlueprintCallable, Category = "Interverse|Wallet")
    void CreateWallet();

    UFUNCTION(BlueprintCallable, Category = "Interverse|Wallet")
    void GetBalance(const FString& Address);

    UFUNCTION(BlueprintCallable, Category = "Interverse|Assets")
    void MintGameAsset(const FString& OwnerAddress, 
                      const FInterverseBaseProperties& Properties,
                      const TMap<FString, FString>& CustomProperties);

    UFUNCTION(BlueprintCallable, Category = "Interverse|Assets")
    void TransferAsset(const FString& AssetId, 
                      const FString& FromAddress, 
                      const FString& ToAddress);

    UFUNCTION(BlueprintCallable, Category = "Interverse|Assets")
    void GetPlayerAssets(const FString& PlayerAddress);

    // Network functions
    UFUNCTION(BlueprintCallable, Category = "Interverse|Network")
    void ConnectWebSocket();

    UFUNCTION(BlueprintCallable, Category = "Interverse|Network")
    void DisconnectWebSocket();

    UFUNCTION(BlueprintCallable, Category = "Interverse|Network")
    void SendWebSocketMessage(const FString& Message);

    UFUNCTION(BlueprintPure, Category = "Interverse|Network")
    bool IsWebSocketConnected() const;

    UFUNCTION(BlueprintPure, Category = "Interverse|Network")
    FString GetConnectionStatus() const;

    // Events
    UPROPERTY(BlueprintAssignable, Category = "Interverse|Events")
    FOnWebSocketConnected OnWebSocketConnected;

    UPROPERTY(BlueprintAssignable, Category = "Interverse|Events")
    FOnWebSocketMessage OnWebSocketMessage;

    UPROPERTY(BlueprintAssignable, Category = "Interverse|Events")
    FOnAssetMinted OnAssetMinted;

    UPROPERTY(BlueprintAssignable, Category = "Interverse|Events")
    FOnTransferComplete OnTransferComplete;

    UPROPERTY(BlueprintAssignable, Category = "Interverse|Events")
    FOnBalanceUpdated OnBalanceUpdated;

private:
    // Implementation details
    TSharedPtr<IWebSocket> WebSocket;
    FHttpModule* Http;
    
    void OnHttpResponseReceived(FHttpRequestPtr Request, FHttpResponsePtr Response, bool bSuccess);
    void ProcessWebSocketMessage(const FString& Message);
    FString GetEndpointPath(const FString& Endpoint);
    TSharedPtr<FJsonObject> ConvertPropertiesToJson(const FInterverseBaseProperties& Properties);
};