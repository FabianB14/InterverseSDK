#include "InterverseSDKComponent.h"
#include "WebSocketsModule.h"
#include "InterverseUtils.h"

UInterverseSDKComponent::UInterverseSDKComponent()
{
    PrimaryComponentTick.bCanEverTick = false;
    Http = &FHttpModule::Get();
}

void UInterverseSDKComponent::BeginPlay()
{
    Super::BeginPlay();

    UE_LOG(LogTemp, Log, TEXT("InterverseSDKComponent BeginPlay"));

    if (NodeUrl.IsEmpty() || GameId.IsEmpty() || ApiKey.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("Missing configuration - NodeUrl: %s, GameId: %s, ApiKey is %s"), 
            *NodeUrl, *GameId, ApiKey.IsEmpty() ? TEXT("empty") : TEXT("set"));
        return;
    }

    ConnectWebSocket();
}

void UInterverseSDKComponent::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
    UE_LOG(LogTemp, Log, TEXT("InterverseSDKComponent EndPlay"));
    DisconnectWebSocket();
    Super::EndPlay(EndPlayReason);
}

void UInterverseSDKComponent::CreateWallet()
{
    TSharedRef<IHttpRequest, ESPMode::ThreadSafe> Request = Http->CreateRequest();
    Request->OnProcessRequestComplete().BindUObject(this, &UInterverseSDKComponent::OnHttpResponseReceived);
    
    FString Endpoint = GetEndpointPath("wallet/create");
    Request->SetURL(FString::Printf(TEXT("%s/%s"), *NodeUrl, *Endpoint));
    
    Request->SetVerb("POST");
    Request->SetHeader("Content-Type", "application/json");
    Request->SetHeader("X-API-Key", ApiKey);
    Request->ProcessRequest();
}

FString UInterverseSDKComponent::GetEndpointPath(const FString& Endpoint)
{
    FString Path = Endpoint;
    if (!Path.StartsWith(TEXT("verse/")))
    {
        Path = FString::Printf(TEXT("verse/%s"), *Path);
    }
    return Path;
}

// Other method implementations...

void UInterverseSDKComponent::ConnectWebSocket()
{
    UE_LOG(LogTemp, Log, TEXT("Starting WebSocket connection process..."));

    if (NodeUrl.IsEmpty() || ApiKey.IsEmpty())
    {
        UE_LOG(LogTemp, Error, TEXT("NodeUrl or ApiKey is empty"));
        return;
    }

    // Build WebSocket URL
    FString BaseUrl = NodeUrl;
    if (BaseUrl.StartsWith(TEXT("http://")))
    {
        BaseUrl = BaseUrl.Replace(TEXT("http://"), TEXT("wss://"));
    }
    else if (BaseUrl.StartsWith(TEXT("https://")))
    {
        BaseUrl = BaseUrl.Replace(TEXT("https://"), TEXT("wss://"));
    }

    // Clean URL
    while (BaseUrl.EndsWith(TEXT("/")))
    {
        BaseUrl.RemoveAt(BaseUrl.Len() - 1);
    }

    // Add endpoint and API key
    FString WsUrl = FString::Printf(TEXT("%s/ws?api_key=%s"), *BaseUrl, *ApiKey);
    UE_LOG(LogTemp, Log, TEXT("Connecting to URL: %s"), *WsUrl);

    // Create WebSocket
    WebSocket = FWebSocketsModule::Get().CreateWebSocket(WsUrl);

    // Set up event handlers
    WebSocket->OnConnected().AddLambda([this]() {
        UE_LOG(LogTemp, Log, TEXT("WebSocket Connected Successfully"));

        AsyncTask(ENamedThreads::GameThread, [this]() {
            OnWebSocketConnected.Broadcast(true);

            // Send handshake message
            const FString HandshakeMessage = FString::Printf(TEXT("{\"type\":\"handshake\",\"game_id\":\"%s\"}"), *GameId);
            WebSocket->Send(HandshakeMessage);
        });
    });

    WebSocket->OnConnectionError().AddLambda([this](const FString& Error) {
        UE_LOG(LogTemp, Error, TEXT("WebSocket Connection Error: %s"), *Error);

        AsyncTask(ENamedThreads::GameThread, [this]() {
            OnWebSocketConnected.Broadcast(false);
        });
    });

    WebSocket->OnMessage().AddLambda([this](const FString& MessageStr) {
        UE_LOG(LogTemp, Log, TEXT("Received message: %s"), *MessageStr);

        AsyncTask(ENamedThreads::GameThread, [this, MessageStr]() {
            OnWebSocketMessage.Broadcast(MessageStr);
            ProcessWebSocketMessage(MessageStr);
        });
    });

    WebSocket->OnClosed().AddLambda([this](int32 StatusCode, const FString& Reason, bool bWasClean) {
        UE_LOG(LogTemp, Warning, TEXT("WebSocket Closed: Status Code: %d, Reason: %s, Clean: %s"), 
            StatusCode, *Reason, bWasClean ? TEXT("Yes") : TEXT("No"));
    });

    WebSocket->Connect();
}

// Additional method implementations...