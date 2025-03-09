using System;
using System.Collections;
using System.Collections.Generic;
using System.Text;
using System.Threading.Tasks;
using Newtonsoft.Json;
using UnityEngine;
using UnityEngine.Networking;

namespace Interverse.SDK
{
    public class InterverseManager : MonoBehaviour
    {
        #region Singleton
        private static InterverseManager _instance;
        
        public static InterverseManager Instance {
            get {
                if (_instance == null) {
                    GameObject go = new GameObject("InterverseManager");
                    _instance = go.AddComponent<InterverseManager>();
                    DontDestroyOnLoad(go);
                }
                return _instance;
            }
        }
        #endregion

        // Configuration
        [Header("Configuration")]
        [SerializeField] private string _nodeUrl = "https://verse-coin-7b67e4d49b53.herokuapp.com";
        [SerializeField] private string _gameId = "";
        [SerializeField] private string _apiKey = "";
        
        // WebSocket
        private WebSocket _webSocket;
        private bool _isConnected = false;
        private Queue<string> _messageQueue = new Queue<string>();
        private Coroutine _processMessageCoroutine;

        // Events
        public delegate void WebSocketConnectedDelegate(bool success);
        public event WebSocketConnectedDelegate OnWebSocketConnected;
        
        public delegate void WebSocketMessageDelegate(string message);
        public event WebSocketMessageDelegate OnWebSocketMessage;
        
        public delegate void AssetMintedDelegate(InterverseAsset asset);
        public event AssetMintedDelegate OnAssetMinted;
        
        public delegate void TransferCompleteDelegate(string assetId, string targetPlayerId, bool success);
        public event TransferCompleteDelegate OnTransferComplete;
        
        public delegate void BalanceUpdatedDelegate(float newBalance);
        public event BalanceUpdatedDelegate OnBalanceUpdated;

        #region Properties
        public string NodeUrl {
            get => _nodeUrl;
            set => _nodeUrl = value;
        }

        public string GameId {
            get => _gameId;
            set => _gameId = value;
        }

        public string ApiKey {
            get => _apiKey;
            set => _apiKey = value;
        }

        public bool IsConnected => _isConnected;
        #endregion

        void Awake() {
            if (_instance != null && _instance != this) {
                Destroy(gameObject);
                return;
            }
            _instance = this;
            DontDestroyOnLoad(gameObject);
        }

        void OnDestroy() {
            DisconnectWebSocket();
        }

        #region Connection
        public void ConnectWebSocket() {
            if (_webSocket != null) {
                DisconnectWebSocket();
            }

            StartCoroutine(ConnectWebSocketCoroutine());
        }

        private IEnumerator ConnectWebSocketCoroutine() {
            // Convert http to ws
            string wsUrl = _nodeUrl.Replace("http://", "ws://").Replace("https://", "wss://");
            
            // Ensure URL ends with no trailing slash
            if (wsUrl.EndsWith("/")) {
                wsUrl = wsUrl.Substring(0, wsUrl.Length - 1);
            }
            
            // Append WebSocket endpoint with API key
            wsUrl += $"/ws?api_key={_apiKey}";
            
            Debug.Log($"Connecting to WebSocket: {wsUrl}");
            
            _webSocket = new WebSocket(wsUrl);
            
            _webSocket.OnOpen += () => {
                Debug.Log("WebSocket connected");
                _isConnected = true;
                
                // Send handshake message
                string handshake = JsonUtility.ToJson(new {
                    type = "handshake",
                    game_id = _gameId
                });
                _webSocket.Send(handshake);
                
                OnWebSocketConnected?.Invoke(true);
            };
            
            _webSocket.OnError += (error) => {
                Debug.LogError($"WebSocket error: {error}");
                _isConnected = false;
                OnWebSocketConnected?.Invoke(false);
            };
            
            _webSocket.OnClose += (code) => {
                Debug.Log($"WebSocket closed with code: {code}");
                _isConnected = false;
            };
            
            _webSocket.OnMessage += (message) => {
                _messageQueue.Enqueue(message);
                if (_processMessageCoroutine == null) {
                    _processMessageCoroutine = StartCoroutine(ProcessMessageQueue());
                }
            };
            
            _webSocket.Connect();
            
            yield return null;
        }

        public void DisconnectWebSocket() {
            if (_webSocket != null) {
                _webSocket.Close();
                _webSocket = null;
                _isConnected = false;
            }
            
            if (_processMessageCoroutine != null) {
                StopCoroutine(_processMessageCoroutine);
                _processMessageCoroutine = null;
            }
        }

        private IEnumerator ProcessMessageQueue() {
            while (_messageQueue.Count > 0) {
                string message = _messageQueue.Dequeue();
                OnWebSocketMessage?.Invoke(message);
                ProcessWebSocketMessage(message);
                yield return null;
            }
            _processMessageCoroutine = null;
        }

        private void ProcessWebSocketMessage(string message) {
            try {
                var msg = JsonUtility.FromJson<WebSocketMessage>(message);
                
                switch (msg.type) {
                    case "asset_update":
                        var assetMsg = JsonUtility.FromJson<AssetUpdateMessage>(message);
                        OnAssetMinted?.Invoke(assetMsg.asset);
                        break;
                        
                    case "balance_update":
                        var balanceMsg = JsonUtility.FromJson<BalanceUpdateMessage>(message);
                        OnBalanceUpdated?.Invoke(balanceMsg.data.balance);
                        break;
                        
                    case "transfer_complete":
                        var transferMsg = JsonUtility.FromJson<TransferCompleteMessage>(message);
                        OnTransferComplete?.Invoke(
                            transferMsg.data.asset_id,
                            transferMsg.data.recipient,
                            transferMsg.data.success
                        );
                        break;
                }
            }
            catch (Exception e) {
                Debug.LogError($"Error processing WebSocket message: {e.Message}");
            }
        }
        #endregion

        #region Blockchain Operations
        public void CreateWallet(Action<WalletResponse> callback) {
            StartCoroutine(CreateWalletCoroutine(callback));
        }

        private IEnumerator CreateWalletCoroutine(Action<WalletResponse> callback) {
            string url = $"{_nodeUrl}/verse/wallet/create";
            
            using (UnityWebRequest request = UnityWebRequest.Post(url, "")) {
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("X-API-Key", _apiKey);
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success) {
                    string response = request.downloadHandler.text;
                    var walletResponse = JsonUtility.FromJson<WalletResponse>(response);
                    callback?.Invoke(walletResponse);
                }
                else {
                    Debug.LogError($"Error creating wallet: {request.error}");
                    callback?.Invoke(null);
                }
            }
        }

        public void GetBalance(string address, Action<float> callback) {
            StartCoroutine(GetBalanceCoroutine(address, callback));
        }

        private IEnumerator GetBalanceCoroutine(string address, Action<float> callback) {
            string url = $"{_nodeUrl}/verse/wallet/{address}/balance";
            
            using (UnityWebRequest request = UnityWebRequest.Get(url)) {
                request.SetRequestHeader("X-API-Key", _apiKey);
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success) {
                    string response = request.downloadHandler.text;
                    var balanceResponse = JsonUtility.FromJson<BalanceResponse>(response);
                    
                    float balance = 0f;
                    if (balanceResponse.success && balanceResponse.data != null) {
                        balance = balanceResponse.data.balance;
                        OnBalanceUpdated?.Invoke(balance);
                    }
                    
                    callback?.Invoke(balance);
                }
                else {
                    Debug.LogError($"Error getting balance: {request.error}");
                    callback?.Invoke(0f);
                }
            }
        }

        public void MintAsset(string ownerAddress, InterverseAssetProperties properties, 
                             Action<InterverseAsset> callback) {
            StartCoroutine(MintAssetCoroutine(ownerAddress, properties, callback));
        }

        private IEnumerator MintAssetCoroutine(string ownerAddress, InterverseAssetProperties properties, 
                                              Action<InterverseAsset> callback) {
            string url = $"{_nodeUrl}/verse/assets/mint";
            
            // Create payload
            var payload = new Dictionary<string, object> {
                { "owner", ownerAddress },
                { "game_id", _gameId },
                { "asset_type", properties.category.ToString() },
                { "metadata", properties }
            };
            
            string json = JsonConvert.SerializeObject(payload);
            
            using (UnityWebRequest request = new UnityWebRequest(url, "POST")) {
                byte[] bodyRaw = Encoding.UTF8.GetBytes(json);
                request.uploadHandler = new UploadHandlerRaw(bodyRaw);
                request.downloadHandler = new DownloadHandlerBuffer();
                request.SetRequestHeader("Content-Type", "application/json");
                request.SetRequestHeader("X-API-Key", _apiKey);
                
                yield return request.SendWebRequest();
                
                if (request.result == UnityWebRequest.Result.Success) {
                    string response = request.downloadHandler.text;
                    var assetResponse = JsonUtility.FromJson<AssetResponse>(response);
                    
                    if (assetResponse.success && assetResponse.data != null) {
                        OnAssetMinted?.Invoke(assetResponse.data);
                        callback?.Invoke(assetResponse.data);
                    }
                    else {
                        callback?.Invoke(null);
                    }
                }
                else {
                    Debug.LogError($"Error minting asset: {request.error}");
                    callback?.Invoke(null);
                }
            }
        }

        // Additional blockchain operations...
        #endregion
    }

    #region Response Classes
    [Serializable]
    public class WebSocketMessage {
        public string type;
    }

    [Serializable]
    public class AssetUpdateMessage {
        public string type;
        public InterverseAsset asset;
    }

    [Serializable]
    public class BalanceUpdateMessage {
        public string type;
        public BalanceData data;
    }

    [Serializable]
    public class BalanceData {
        public float balance;
        public string address;
    }

    [Serializable]
    public class TransferCompleteMessage {
        public string type;
        public TransferData data;
    }

    [Serializable]
    public class TransferData {
        public string asset_id;
        public string sender;
        public string recipient;
        public bool success;
    }

    [Serializable]
    public class WalletResponse {
        public bool success;
        public string message;
        public WalletData data;
    }

    [Serializable]
    public class WalletData {
        public string address;
        public string public_key;
        public float balance;
    }

    [Serializable]
    public class BalanceResponse {
        public bool success;
        public string message;
        public BalanceData data;
    }

    [Serializable]
    public class AssetResponse {
        public bool success;
        public string message;
        public InterverseAsset data;
    }
    #endregion
}