import websockets
import aiohttp
import json
import asyncio
import logging
import time
from typing import Dict, Any, Optional, List, Callable, Union

logger = logging.getLogger("interverse.chain")

class InterverseChain:
    """Core blockchain connectivity and operations"""
    
    def __init__(self, node_url: str = "https://verse-coin-7b67e4d49b53.herokuapp.com", 
                game_id: str = "", api_key: str = ""):
        self.node_url = node_url.rstrip('/')  # Remove trailing slash if present
        self.game_id = game_id
        self.api_key = api_key
        self.websocket = None
        self.http_session = None
        self.is_connected = False
        self.event_handlers = {
            "asset_minted": [],
            "transfer_complete": [],
            "balance_updated": [],
            "websocket_connected": [],
            "websocket_message": [],
            "error": []
        }
        self.reconnect_attempts = 0
        self.max_reconnect_attempts = 5
        self.reconnect_delay = 5  # Initial delay in seconds
    
    async def initialize(self) -> bool:
        """Initialize the SDK and establish HTTP session"""
        try:
            if self.http_session is None or self.http_session.closed:
                self.http_session = aiohttp.ClientSession(
                    headers={"X-API-Key": self.api_key, "Content-Type": "application/json"}
                )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize HTTP session: {e}")
            self._trigger_event("error", {"message": f"Initialization failed: {e}"})
            return False
        
    async def connect(self) -> bool:
        """Connect to the Interverse blockchain network via WebSocket"""
        if not await self.initialize():
            return False
            
        try:
            # Close existing connection if any
            await self.disconnect()
            
            # Connect WebSocket for real-time updates
            ws_url = f"{self.node_url.replace('http', 'ws')}/ws?api_key={self.api_key}"
            logger.info(f"Connecting to WebSocket: {ws_url}")
            
            self.websocket = await websockets.connect(
                ws_url,
                extra_headers={"X-API-Key": self.api_key}
            )
            
            # Send handshake message
            handshake_msg = json.dumps({
                "type": "handshake",
                "game_id": self.game_id
            })
            await self.websocket.send(handshake_msg)
            logger.debug(f"Sent handshake: {handshake_msg}")
            
            # Start message handling
            asyncio.create_task(self._handle_messages())
            
            self.is_connected = True
            self.reconnect_attempts = 0
            
            # Trigger connected event
            self._trigger_event("websocket_connected", {"success": True})
            return True
            
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
            self._trigger_event("websocket_connected", {"success": False, "error": str(e)})
            self._trigger_event("error", {"message": f"Connection failed: {e}"})
            return False
    
    async def disconnect(self) -> None:
        """Disconnect from the WebSocket"""
        if self.websocket is not None:
            try:
                await self.websocket.close()
                logger.info("WebSocket disconnected")
            except Exception as e:
                logger.error(f"Error during WebSocket disconnect: {e}")
            finally:
                self.websocket = None
                self.is_connected = False
    
    async def create_wallet(self) -> Dict[str, Any]:
        """Create a new blockchain wallet"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        try:
            async with self.http_session.post(
                f"{self.node_url}/wallet/create"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Wallet creation failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    wallet_data = data.get("data", {})
                    logger.info(f"Wallet created: {wallet_data.get('address', 'unknown')}")
                    return {"success": True, "wallet": wallet_data}
                else:
                    logger.error(f"Wallet creation failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Wallet creation error: {e}")
            self._trigger_event("error", {"message": f"Wallet creation failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def get_balance(self, address: str) -> Dict[str, Any]:
        """Get wallet balance"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not address or not isinstance(address, str):
            return {"success": False, "error": "Invalid address"}
            
        try:
            async with self.http_session.get(
                f"{self.node_url}/wallet/{address}/balance"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Balance check failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    balance_data = data.get("data", {})
                    balance = balance_data.get("balance", 0.0)
                    logger.debug(f"Balance for {address}: {balance}")
                    
                    self._trigger_event("balance_updated", {
                        "address": address,
                        "balance": balance
                    })
                    
                    return {
                        "success": True,
                        "address": address,
                        "balance": balance
                    }
                else:
                    logger.error(f"Balance check failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Balance check error: {e}")
            self._trigger_event("error", {"message": f"Balance check failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def get_player_assets(self, address: str) -> Dict[str, Any]:
        """Get assets owned by a player"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not address or not isinstance(address, str):
            return {"success": False, "error": "Invalid address"}
            
        try:
            async with self.http_session.get(
                f"{self.node_url}/wallet/{address}/assets"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Asset fetch failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    assets = data.get("data", {}).get("assets", [])
                    logger.debug(f"Retrieved {len(assets)} assets for {address}")
                    return {
                        "success": True,
                        "address": address,
                        "assets": assets
                    }
                else:
                    logger.error(f"Asset fetch failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Asset fetch error: {e}")
            self._trigger_event("error", {"message": f"Asset fetch failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def mint_asset(self, owner_address: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Mint a new game asset on the blockchain"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not owner_address or not isinstance(owner_address, str):
            return {"success": False, "error": "Invalid owner address"}
            
        try:
            # Build payload based on the expected format of your Heroku API
            payload = {
                "owner": owner_address,
                "game_id": self.game_id
            }
            
            # Handle different property format options
            if "asset_type" in properties:
                payload["asset_type"] = properties["asset_type"]
            elif "category" in properties:
                payload["asset_type"] = properties["category"]
            else:
                payload["asset_type"] = "COSMETIC"  # Default type
                
            # Add metadata
            payload["metadata"] = properties
            
            logger.debug(f"Minting asset payload: {json.dumps(payload)}")
            
            async with self.http_session.post(
                f"{self.node_url}/assets/mint",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Asset minting failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    asset_data = data.get("data", {})
                    asset_id = asset_data.get("asset_id", "")
                    logger.info(f"Asset minted: {asset_id} for {owner_address}")
                    
                    self._trigger_event("asset_minted", {
                        "asset": asset_data,
                        "owner": owner_address
                    })
                    
                    return {
                        "success": True,
                        "asset": asset_data
                    }
                else:
                    logger.error(f"Asset minting failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Asset minting error: {e}")
            self._trigger_event("error", {"message": f"Asset minting failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def transfer_asset(self, asset_id: str, from_address: str, to_address: str) -> Dict[str, Any]:
        """Transfer an asset between addresses"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not asset_id or not from_address or not to_address:
            return {"success": False, "error": "Missing required parameters"}
            
        try:
            payload = {
                "asset_id": asset_id,
                "from_address": from_address,
                "to_address": to_address
            }
            
            logger.debug(f"Transferring asset: {asset_id} from {from_address} to {to_address}")
            
            async with self.http_session.post(
                f"{self.node_url}/assets/transfer",
                json=payload
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Asset transfer failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                transfer_success = data.get("success", False)
                
                if transfer_success:
                    transfer_data = data.get("data", {})
                    logger.info(f"Asset transferred: {asset_id} to {to_address}")
                    
                    self._trigger_event("transfer_complete", {
                        "asset_id": asset_id,
                        "from_address": from_address,
                        "to_address": to_address,
                        "success": True
                    })
                    
                    return {
                        "success": True,
                        "asset_id": asset_id,
                        "transaction_id": transfer_data.get("transaction_id", ""),
                        "from_address": from_address,
                        "to_address": to_address
                    }
                else:
                    error_msg = data.get("message", "Unknown error")
                    logger.error(f"Asset transfer failed: {error_msg}")
                    
                    self._trigger_event("transfer_complete", {
                        "asset_id": asset_id,
                        "from_address": from_address,
                        "to_address": to_address,
                        "success": False,
                        "error": error_msg
                    })
                    
                    return {"success": False, "error": error_msg}
                    
        except Exception as e:
            logger.error(f"Asset transfer error: {e}")
            self._trigger_event("error", {"message": f"Asset transfer failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def get_asset(self, asset_id: str) -> Dict[str, Any]:
        """Get details of a specific asset"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not asset_id or not isinstance(asset_id, str):
            return {"success": False, "error": "Invalid asset ID"}
            
        try:
            async with self.http_session.get(
                f"{self.node_url}/assets/{asset_id}"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Asset fetch failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    asset_data = data.get("data", {})
                    logger.debug(f"Retrieved asset: {asset_id}")
                    return {
                        "success": True,
                        "asset": asset_data
                    }
                else:
                    logger.error(f"Asset fetch failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Asset fetch error: {e}")
            self._trigger_event("error", {"message": f"Asset fetch failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def get_transaction_history(self, address: str) -> Dict[str, Any]:
        """Get transaction history for an address"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not address or not isinstance(address, str):
            return {"success": False, "error": "Invalid address"}
            
        try:
            async with self.http_session.get(
                f"{self.node_url}/transactions/{address}"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Transaction history failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    tx_data = data.get("data", {})
                    transactions = tx_data.get("transactions", [])
                    logger.debug(f"Retrieved {len(transactions)} transactions for {address}")
                    return {
                        "success": True,
                        "address": address,
                        "transactions": transactions
                    }
                else:
                    logger.error(f"Transaction history failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Transaction history error: {e}")
            self._trigger_event("error", {"message": f"Transaction history failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def verify_game(self) -> Dict[str, Any]:
        """Verify game registration with the blockchain"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        try:
            async with self.http_session.get(
                f"{self.node_url}/games/verify"
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    logger.error(f"Game verification failed: HTTP {response.status} - {error_text}")
                    return {"success": False, "error": f"HTTP {response.status}: {error_text}"}
                    
                data = await response.json()
                if data.get("success", False):
                    game_data = data.get("data", {})
                    logger.info(f"Game verified: {game_data.get('game_id', 'unknown')}")
                    return {
                        "success": True,
                        "game": game_data
                    }
                else:
                    logger.error(f"Game verification failed: {data.get('message', 'Unknown error')}")
                    return {"success": False, "error": data.get("message", "Unknown error")}
                    
        except Exception as e:
            logger.error(f"Game verification error: {e}")
            self._trigger_event("error", {"message": f"Game verification failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def update_asset(self, asset_id: str, properties: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing asset's properties"""
        if not await self.ensure_initialized():
            return {"success": False, "error": "Not initialized"}
            
        if not asset_id or not isinstance(asset_id, str):
            return {"success": False, "error": "Invalid asset ID"}
            
        try:
            # Get existing asset first
            asset_result = await self.get_asset(asset_id)
            if not asset_result.get("success", False):
                return asset_result
                
            existing_asset = asset_result.get("asset", {})
            
            # Update metadata with new properties
            metadata = existing_asset.get("metadata", {})
            for key, value in properties.items():
                metadata[key] = value
                
            # Prepare update payload
            payload = {
                "asset_id": asset_id,
                "metadata": metadata
            }
            
            # Check if backend supports asset updates
            try:
                async with self.http_session.put(
                    f"{self.node_url}/assets/{asset_id}",
                    json=payload
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        if data.get("success", False):
                            updated_asset = data.get("data", {})
                            logger.info(f"Asset updated: {asset_id}")
                            return {
                                "success": True,
                                "asset": updated_asset
                            }
                    # If HTTP 404 or other error, backend might not support direct updates
            except:
                pass
                
            # Fallback to transfer workaround if update endpoint not available
            # This simulates an update by transferring to self
            owner_address = existing_asset.get("owner", "")
            if not owner_address:
                return {"success": False, "error": "Cannot determine asset owner"}
                
            return await self.transfer_asset(asset_id, owner_address, owner_address)
            
        except Exception as e:
            logger.error(f"Asset update error: {e}")
            self._trigger_event("error", {"message": f"Asset update failed: {e}"})
            return {"success": False, "error": str(e)}
    
    async def _handle_messages(self):
        """Handle incoming WebSocket messages"""
        if self.websocket is None:
            return
            
        try:
            async for message in self.websocket:
                try:
                    data = json.loads(message)
                    logger.debug(f"WebSocket message received: {message[:100]}...")
                    
                    # Broadcast raw message event
                    self._trigger_event("websocket_message", {"raw": message, "data": data})
                    
                    # Handle specific message types
                    message_type = data.get("type")
                    if message_type == "welcome":
                        logger.info(f"Welcome message received for game: {data.get('game_id', 'unknown')}")
                        
                    elif message_type == "asset_update" or message_type == "new_asset":
                        asset_data = data.get("asset", {})
                        owner = asset_data.get("owner", "")
                        self._trigger_event("asset_minted", {
                            "asset": asset_data,
                            "owner": owner
                        })
                        
                    elif message_type == "balance_update":
                        balance_data = data.get("data", {})
                        address = balance_data.get("address", "")
                        balance = balance_data.get("balance", 0.0)
                        self._trigger_event("balance_updated", {
                            "address": address,
                            "balance": balance
                        })
                        
                    elif message_type == "transfer_complete":
                        transfer_data = data.get("data", {})
                        self._trigger_event("transfer_complete", {
                            "asset_id": transfer_data.get("asset_id", ""),
                            "from_address": transfer_data.get("sender", ""),
                            "to_address": transfer_data.get("recipient", ""),
                            "success": transfer_data.get("success", False)
                        })
                        
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON in WebSocket message: {message[:100]}...")
                    
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed")
            self.is_connected = False
            await self._attempt_reconnect()
            
        except Exception as e:
            logger.error(f"Error in WebSocket message handler: {e}")
            self._trigger_event("error", {"message": f"WebSocket handler error: {e}"})
            self.is_connected = False
            await self._attempt_reconnect()
    
    async def _attempt_reconnect(self):
        """Attempt to reconnect to WebSocket with exponential backoff"""
        if self.reconnect_attempts >= self.max_reconnect_attempts:
            logger.error(f"Maximum reconnection attempts ({self.max_reconnect_attempts}) reached")
            self._trigger_event("error", {"message": "Maximum reconnection attempts reached"})
            return
            
        self.reconnect_attempts += 1
        backoff = self.reconnect_delay * (2 ** (self.reconnect_attempts - 1))
        
        logger.info(f"Attempting reconnect in {backoff} seconds (attempt {self.reconnect_attempts})")
        await asyncio.sleep(backoff)
        await self.connect()
    
    async def ensure_initialized(self) -> bool:
        """Ensure HTTP session is initialized"""
        if self.http_session is None or self.http_session.closed:
            return await self.initialize()
        return True
    
    def on(self, event_name: str, callback: Callable) -> None:
        """Register event handler"""
        if event_name in self.event_handlers:
            self.event_handlers[event_name].append(callback)
    
    def off(self, event_name: str, callback: Callable) -> None:
        """Remove event handler"""
        if event_name in self.event_handlers:
            if callback in self.event_handlers[event_name]:
                self.event_handlers[event_name].remove(callback)
    
    def _trigger_event(self, event_name: str, data: Any) -> None:
        """Trigger event handlers"""
        if event_name in self.event_handlers:
            for handler in self.event_handlers[event_name]:
                try:
                    handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event_name}: {e}")
    
    async def close(self) -> None:
        """Close all connections and clean up resources"""
        await self.disconnect()
        
        if self.http_session is not None and not self.http_session.closed:
            await self.http_session.close()
            self.http_session = None
            
        logger.info("InterverseChain instance closed")