"""
WebSocket Manager for handling WebSocket connections and rooms
"""

import asyncio
import json
import logging
from typing import Dict, Set, Optional, Any
from fastapi import WebSocket, WebSocketDisconnect
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and rooms"""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.rooms: Dict[str, Set[str]] = {}
        self.user_rooms: Dict[str, str] = {}
        
    async def connect(self, websocket: WebSocket, client_id: str, room_id: str = "default"):
        """Connect a client to a room"""
        await websocket.accept()
        
        # Store connection
        self.active_connections[client_id] = websocket
        self.user_rooms[client_id] = room_id
        
        # Add to room
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        self.rooms[room_id].add(client_id)
        
        logger.info(f"Client {client_id} connected to room {room_id}")
        
        # Notify room about new connection
        await self.broadcast_to_room(room_id, {
            "type": "user_joined",
            "client_id": client_id,
            "timestamp": datetime.now().isoformat(),
            "room_participants": len(self.rooms[room_id])
        }, exclude_client=client_id)
        
    def disconnect(self, client_id: str):
        """Disconnect a client"""
        if client_id in self.active_connections:
            room_id = self.user_rooms.get(client_id)
            
            # Remove from connection tracking
            del self.active_connections[client_id]
            del self.user_rooms[client_id]
            
            # Remove from room
            if room_id and room_id in self.rooms:
                self.rooms[room_id].discard(client_id)
                if not self.rooms[room_id]:  # Remove empty room
                    del self.rooms[room_id]
                else:
                    # Notify remaining users
                    asyncio.create_task(self.broadcast_to_room(room_id, {
                        "type": "user_left",
                        "client_id": client_id,
                        "timestamp": datetime.now().isoformat(),
                        "room_participants": len(self.rooms[room_id])
                    }))
            
            logger.info(f"Client {client_id} disconnected from room {room_id}")
    
    async def send_personal_message(self, message: dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            try:
                await websocket.send_text(json.dumps(message))
                return True
            except Exception as e:
                logger.error(f"Error sending message to {client_id}: {e}")
                self.disconnect(client_id)
                return False
        return False
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_client: str = None):
        """Broadcast message to all clients in a room"""
        if room_id not in self.rooms:
            return
        
        message["room_id"] = room_id
        message["timestamp"] = datetime.now().isoformat()
        
        disconnected_clients = []
        
        for client_id in self.rooms[room_id]:
            if exclude_client and client_id == exclude_client:
                continue
                
            success = await self.send_personal_message(message, client_id)
            if not success:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all connected clients"""
        message["timestamp"] = datetime.now().isoformat()
        
        disconnected_clients = []
        
        for client_id in list(self.active_connections.keys()):
            success = await self.send_personal_message(message, client_id)
            if not success:
                disconnected_clients.append(client_id)
        
        # Clean up disconnected clients
        for client_id in disconnected_clients:
            self.disconnect(client_id)
    
    def get_room_info(self, room_id: str) -> dict:
        """Get information about a room"""
        if room_id not in self.rooms:
            return {"room_id": room_id, "participants": 0, "clients": []}
        
        return {
            "room_id": room_id,
            "participants": len(self.rooms[room_id]),
            "clients": list(self.rooms[room_id])
        }
    
    def get_all_rooms(self) -> Dict[str, dict]:
        """Get information about all rooms"""
        return {
            room_id: self.get_room_info(room_id)
            for room_id in self.rooms.keys()
        }


class WebSocketManager:
    """Main WebSocket manager with advanced features"""
    
    def __init__(self):
        self.connection_manager = ConnectionManager()
        self.message_handlers = {}
        self.middleware = []
        
    def add_message_handler(self, message_type: str, handler):
        """Add a handler for specific message type"""
        self.message_handlers[message_type] = handler
    
    def add_middleware(self, middleware_func):
        """Add middleware for message processing"""
        self.middleware.append(middleware_func)
    
    async def handle_websocket(self, websocket: WebSocket, client_id: str, room_id: str = "default"):
        """Main WebSocket handler"""
        try:
            await self.connection_manager.connect(websocket, client_id, room_id)
            
            while True:
                try:
                    # Receive message
                    data = await websocket.receive_text()
                    message = json.loads(data)
                    
                    # Add metadata
                    message["client_id"] = client_id
                    message["room_id"] = room_id
                    message["received_at"] = datetime.now().isoformat()
                    
                    # Process through middleware
                    for middleware in self.middleware:
                        message = await middleware(message)
                        if message is None:  # Middleware can block message
                            break
                    
                    if message is None:
                        continue
                    
                    # Handle message based on type
                    message_type = message.get("type", "unknown")
                    
                    if message_type in self.message_handlers:
                        await self.message_handlers[message_type](message, self.connection_manager)
                    else:
                        # Default: broadcast to room
                        await self.connection_manager.broadcast_to_room(
                            room_id, message, exclude_client=client_id
                        )
                        
                except WebSocketDisconnect:
                    break
                except json.JSONDecodeError:
                    await self.connection_manager.send_personal_message({
                        "type": "error",
                        "message": "Invalid JSON format"
                    }, client_id)
                except Exception as e:
                    logger.error(f"Error handling message from {client_id}: {e}")
                    await self.connection_manager.send_personal_message({
                        "type": "error",
                        "message": "Internal server error"
                    }, client_id)
                    
        except Exception as e:
            logger.error(f"WebSocket connection error for {client_id}: {e}")
        finally:
            self.connection_manager.disconnect(client_id)


# Global instance
websocket_manager = WebSocketManager()
