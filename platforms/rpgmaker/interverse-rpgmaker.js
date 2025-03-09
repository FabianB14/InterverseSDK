3//=============================================================================
// Interverse SDK - RPG Maker MV/MZ Plugin
// interverse-rpgmaker.js
//=============================================================================

/*:
 * @plugindesc Interverse SDK integration for RPG Maker MV/MZ
 * @author Interverse Team
 *
 * @param nodeUrl
 * @text Blockchain Node URL
 * @desc URL of the Interverse blockchain node
 * @default https://verse-coin-7b67e4d49b53.herokuapp.com
 *
 * @param gameId
 * @text Game ID
 * @desc Your game's unique identifier
 * @default your_game_id
 *
 * @param apiKey
 * @text API Key
 * @desc Your Interverse API key
 * @default your_api_key
 *
 * @help
 * =============================================================================
 * Introduction
 * =============================================================================
 * 
 * This plugin integrates your RPG Maker game with the Interverse blockchain,
 * allowing players to own and transfer in-game items as blockchain assets.
 * 
 * =============================================================================
 * Script Calls
 * =============================================================================
 * 
 * Interverse.connect() - Connect to the blockchain
 * Interverse.createWallet() - Create a new wallet
 * Interverse.getBalance(address) - Get wallet balance
 * Interverse.mintAsset(address, properties) - Mint a new asset
 * Interverse.transferAsset(assetId, fromAddress, toAddress) - Transfer asset
 * Interverse.getPlayerAssets(address) - Get all player assets
 */

(function() {
    'use strict';
    
    const pluginName = 'InterverseRPGMaker';
    const parameters = PluginManager.parameters(pluginName);
    
    // Configuration
    const config = {
        nodeUrl: parameters.nodeUrl || 'https://verse-coin-7b67e4d49b53.herokuapp.com',
        gameId: parameters.gameId || '',
        apiKey: parameters.apiKey || ''
    };
    
    // Interverse SDK Class
    class InterverseSDK {
        constructor() {
            this.nodeUrl = config.nodeUrl;
            this.gameId = config.gameId;
            this.apiKey = config.apiKey;
            this.isConnected = false;
            this.socket = null;
            this.eventListeners = {
                'connected': [],
                'assetMinted': [],
                'transferComplete': [],
                'balanceUpdated': []
            };
            
            this._debug('Interverse SDK initialized');
        }
        
        // Event handling
        on(event, callback) {
            if (this.eventListeners[event]) {
                this.eventListeners[event].push(callback);
            }
        }
        
        off(event, callback) {
            if (this.eventListeners[event]) {
                this.eventListeners[event] = this.eventListeners[event].filter(
                    cb => cb !== callback
                );
            }
        }
        
        trigger(event, data) {
            if (this.eventListeners[event]) {
                for (const callback of this.eventListeners[event]) {
                    callback(data);
                }
            }
        }
        
        // Connection management
        async connect() {
            try {
                this._debug('Connecting to blockchain...');
                
                // Close existing connection if any
                if (this.socket) {
                    this.socket.close();
                }
                
                // Create WebSocket connection
                const wsUrl = this.nodeUrl.replace('http://', 'ws://').replace('https://', 'wss://');
                const fullWsUrl = `${wsUrl}/ws?api_key=${this.apiKey}`;
                
                return new Promise((resolve, reject) => {
                    this.socket = new WebSocket(fullWsUrl);
                    
                    this.socket.onopen = () => {
                        this._debug('WebSocket connected');
                        this.isConnected = true;
                        
                        // Send handshake
                        const handshake = {
                            type: 'handshake',
                            game_id: this.gameId
                        };
                        this.socket.send(JSON.stringify(handshake));
                        
                        this.trigger('connected', true);
                        resolve(true);
                    };
                    
                    this.socket.onerror = (error) => {
                        this._debug('WebSocket error: ' + JSON.stringify(error));
                        this.isConnected = false;
                        this.trigger('connected', false);
                        reject(error);
                    };
                    
                    this.socket.onclose = () => {
                        this._debug('WebSocket closed');
                        this.isConnected = false;
                    };
                    
                    this.socket.onmessage = (event) => {
                        this._handleSocketMessage(event.data);
                    };
                });
            } catch (error) {
                this._debug('Connection error: ' + error);
                this.isConnected = false;
                this.trigger('connected', false);
                return false;
            }
        }
        
        disconnect() {
            if (this.socket) {
                this.socket.close();
                this.socket = null;
                this.isConnected = false;
            }
        }
        
        // API Methods
        async createWallet() {
            const response = await this._apiRequest('/verse/wallet/create', 'POST');
            return response.data;
        }
        
        async getBalance(address) {
            const response = await this._apiRequest(`/verse/wallet/${address}/balance`, 'GET');
            const balance = response.data?.balance || 0;
            this.trigger('balanceUpdated', balance);
            return balance;
        }
        
        async mintAsset(ownerAddress, properties) {
            const payload = {
                owner: ownerAddress,
                game_id: this.gameId,
                asset_type: properties.category || 'COSMETIC',
                metadata: properties
            };
            
            const response = await this._apiRequest('/verse/assets/mint', 'POST', payload);
            if (response.success && response.data) {
                this.trigger('assetMinted', response.data);
            }
            return response.data;
        }
        
        async transferAsset(assetId, fromAddress, toAddress) {
            const payload = {
                asset_id: assetId,
                from_address: fromAddress,
                to_address: toAddress
            };
            
            const response = await this._apiRequest('/verse/assets/transfer', 'POST', payload);
            this.trigger('transferComplete', {
                asset_id: assetId,
                to_address: toAddress,
                success: response.success
            });
            return response.success;
        }
        
        async getPlayerAssets(address) {
            const response = await this._apiRequest(`/verse/wallet/${address}/assets`, 'GET');
            return response.data?.assets || [];
        }
        
        // Helper methods
        async _apiRequest(endpoint, method, data) {
            const url = this.nodeUrl + endpoint;
            const options = {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-API-Key': this.apiKey
                }
            };
            
            if (data) {
                options.body = JSON.stringify(data);
            }
            
            try {
                this._debug(`API Request: ${method} ${url}`);
                const response = await fetch(url, options);
                const responseData = await response.json();
                return responseData;
            } catch (error) {
                this._debug(`API Error: ${error}`);
                return { success: false, error: String(error) };
            }
        }
        
        _handleSocketMessage(message) {
            try {
                const data = JSON.parse(message);
                this._debug(`WebSocket message: ${data.type}`);
                
                switch (data.type) {
                    case 'asset_update':
                        this.trigger('assetMinted', data.asset);
                        break;
                    case 'balance_update':
                        this.trigger('balanceUpdated', data.data.balance);
                        break;
                    case 'transfer_complete':
                        this.trigger('transferComplete', {
                            asset_id: data.data.asset_id,
                            to_address: data.data.recipient,
                            success: data.data.success
                        });
                        break;
                }
            } catch (error) {
                this._debug(`Error processing message: ${error}`);
            }
        }
        
        _debug(message) {
            console.log(`[Interverse] ${message}`);
        }
    }
    
    // Create global instance
    window.Interverse = new InterverseSDK();
    
    // Integration with RPG Maker save system
    const _DataManager_makeSaveContents = DataManager.makeSaveContents;
    DataManager.makeSaveContents = function() {
        const contents = _DataManager_makeSaveContents.call(this);
        
        // Add Interverse wallet info to save data
        contents.interverseWallet = $gameSystem._interverseWallet || null;
        return contents;
    };
    
    const _DataManager_extractSaveContents = DataManager.extractSaveContents;
    DataManager.extractSaveContents = function(contents) {
        _DataManager_extractSaveContents.call(this, contents);
        
        // Restore Interverse wallet from save data
        if (contents.interverseWallet) {
            $gameSystem._interverseWallet = contents.interverseWallet;
        }
    };
    
    // Add Interverse methods to game system
    const _Game_System_initialize = Game_System.prototype.initialize;
    Game_System.prototype.initialize = function() {
        _Game_System_initialize.call(this);
        this._interverseWallet = null;
        this._interverseAssets = [];
    };
    
    Game_System.prototype.setInterverseWallet = function(wallet) {
        this._interverseWallet = wallet;
    };
    
    Game_System.prototype.getInterverseWallet = function() {
        return this._interverseWallet;
    };
    
    Game_System.prototype.addInterverseAsset = function(asset) {
        if (!this._interverseAssets) {
            this._interverseAssets = [];
        }
        this._interverseAssets.push(asset);
    };
    
    Game_System.prototype.getInterverseAssets = function() {
        return this._interverseAssets || [];
    };
    
    // Create game item from blockchain asset
    function createGameItemFromAsset(asset) {
        // Map asset properties to RPG Maker item
        const itemId = $dataItems.length;
        const newItem = {
            id: itemId,
            name: asset.metadata?.name || `Blockchain Asset ${asset.asset_id.substring(0, 6)}`,
            description: asset.metadata?.description || "An item from the blockchain",
            iconIndex: asset.metadata?.icon_index || 1,
            price: asset.metadata?.price || 0,
            assetId: asset.asset_id,
            ownerAddress: asset.owner
        };
        
        // Add to data items
        $dataItems.push(newItem);
        return newItem;
    }
    
    // Register plugin commands for MZ
    if (Utils.RPGMAKER_NAME === "MZ") {
        PluginManager.registerCommand(pluginName, "ConnectBlockchain", args => {
            window.Interverse.connect().then(success => {
                if (success) {
                    $gameMessage.add("Connected to Interverse blockchain!");
                } else {
                    $gameMessage.add("Failed to connect to blockchain.");
                }
            });
        });
        
        PluginManager.registerCommand(pluginName, "CreateWallet", args => {
            window.Interverse.createWallet().then(wallet => {
                if (wallet) {
                    $gameSystem.setInterverseWallet(wallet);
                    $gameMessage.add(`Wallet created: ${wallet.address}`);
                }
            });
        });
        
        PluginManager.registerCommand(pluginName, "MintAsset", args => {
            const wallet = $gameSystem.getInterverseWallet();
            if (!wallet) {
                $gameMessage.add("No wallet available. Create a wallet first.");
                return;
            }
            
            const itemId = Number(args.itemId);
            const item = $dataItems[itemId];
            if (!item) {
                $gameMessage.add("Item not found!");
                return;
            }
            
            const properties = {
                name: item.name,
                description: item.description,
                icon_index: item.iconIndex,
                price: item.price,
                category: "COSMETIC",
                level: 1,
                rarity: "COMMON"
            };
            
            window.Interverse.mintAsset(wallet.address, properties).then(asset => {
                if (asset) {
                    $gameSystem.addInterverseAsset(asset);
                    $gameMessage.add(`Asset minted: ${asset.asset_id}`);
                }
            });
        });
    }
})();