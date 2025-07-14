"""
FastAPI WebSocket Integration
Provides WebSocket endpoints for real-time streaming
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import json
import asyncio
import logging
from typing import Dict, Set
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Deer Flow WebSocket API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ConnectionManager:
    """Manages WebSocket connections"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        self.connection_info: Dict[WebSocket, Dict] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str = "default"):
        """Accept a new WebSocket connection"""
        await websocket.accept()
        
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        self.active_connections[room_id].add(websocket)
        self.connection_info[websocket] = {
            "room_id": room_id,
            "connected_at": datetime.now(),
            "message_count": 0
        }
        
        logger.info(f"Client connected to room: {room_id}")
        
        # Send welcome message
        await self.send_personal_message({
            "type": "connection",
            "status": "connected",
            "room_id": room_id,
            "timestamp": datetime.now().isoformat()
        }, websocket)
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection"""
        if websocket in self.connection_info:
            room_id = self.connection_info[websocket]["room_id"]
            
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)
                
                # Clean up empty rooms
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
            
            del self.connection_info[websocket]
            logger.info(f"Client disconnected from room: {room_id}")
    
    async def send_personal_message(self, message: dict, websocket: WebSocket):
        """Send message to a specific WebSocket"""
        try:
            await websocket.send_text(json.dumps(message))
            if websocket in self.connection_info:
                self.connection_info[websocket]["message_count"] += 1
        except Exception as e:
            logger.error(f"Error sending message: {e}")
    
    async def broadcast_to_room(self, message: dict, room_id: str):
        """Broadcast message to all connections in a room"""
        if room_id not in self.active_connections:
            return
        
        message["timestamp"] = datetime.now().isoformat()
        disconnected = []
        
        for connection in self.active_connections[room_id].copy():
            try:
                await connection.send_text(json.dumps(message))
                if connection in self.connection_info:
                    self.connection_info[connection]["message_count"] += 1
            except Exception as e:
                logger.error(f"Error broadcasting to connection: {e}")
                disconnected.append(connection)
        
        # Clean up disconnected connections
        for connection in disconnected:
            self.disconnect(connection)
    
    async def broadcast_to_all(self, message: dict):
        """Broadcast message to all active connections"""
        for room_id in self.active_connections:
            await self.broadcast_to_room(message, room_id)
    
    def get_room_stats(self, room_id: str) -> dict:
        """Get statistics for a room"""
        if room_id not in self.active_connections:
            return {"error": "Room not found"}
        
        connections = self.active_connections[room_id]
        total_messages = sum(
            self.connection_info.get(conn, {}).get("message_count", 0)
            for conn in connections
        )
        
        return {
            "room_id": room_id,
            "active_connections": len(connections),
            "total_messages": total_messages
        }

# Global connection manager
manager = ConnectionManager()

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "message": "Deer Flow WebSocket API",
        "status": "running",
        "active_rooms": len(manager.active_connections),
        "total_connections": sum(len(conns) for conns in manager.active_connections.values())
    }

@app.get("/rooms")
async def get_rooms():
    """Get all active rooms and their stats"""
    rooms = {}
    for room_id in manager.active_connections:
        rooms[room_id] = manager.get_room_stats(room_id)
    return {"rooms": rooms}

@app.get("/rooms/{room_id}/stats")
async def get_room_stats(room_id: str):
    """Get statistics for a specific room"""
    return manager.get_room_stats(room_id)

@app.websocket("/ws/{room_id}")
async def websocket_endpoint(websocket: WebSocket, room_id: str):
    """Main WebSocket endpoint for room-based communication"""
    await manager.connect(websocket, room_id)
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
                message_type = message.get("type", "message")
                
                # Handle different message types
                if message_type == "ping":
                    await manager.send_personal_message({
                        "type": "pong",
                        "timestamp": datetime.now().isoformat()
                    }, websocket)
                
                elif message_type == "broadcast":
                    # Broadcast to all clients in the room
                    await manager.broadcast_to_room({
                        "type": "broadcast",
                        "content": message.get("content", ""),
                        "sender": message.get("sender", "unknown"),
                        "room_id": room_id
                    }, room_id)
                
                elif message_type == "streaming":
                    # Handle streaming data
                    await manager.broadcast_to_room({
                        "type": "streaming",
                        "data": message.get("data", {}),
                        "chunk_id": message.get("chunk_id", 0),
                        "is_final": message.get("is_final", False),
                        "room_id": room_id
                    }, room_id)
                
                else:
                    # Default message handling
                    await manager.broadcast_to_room({
                        "type": "message",
                        "content": message,
                        "room_id": room_id
                    }, room_id)
                    
            except json.JSONDecodeError:
                await manager.send_personal_message({
                    "type": "error",
                    "message": "Invalid JSON format"
                }, websocket)
                
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)

@app.websocket("/ws")
async def websocket_default(websocket: WebSocket):
    """Default WebSocket endpoint (uses 'default' room)"""
    await websocket_endpoint(websocket, "default")

# Streaming simulation endpoint for testing
@app.post("/simulate_stream/{room_id}")
async def simulate_stream(room_id: str, data: dict):
    """Simulate streaming data to test WebSocket functionality"""
    
    # Simulate chunk-based streaming
    content = data.get("content", "This is a test streaming message")
    chunk_size = data.get("chunk_size", 10)
    
    chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size)]
    
    for i, chunk in enumerate(chunks):
        await manager.broadcast_to_room({
            "type": "streaming",
            "data": {"chunk": chunk},
            "chunk_id": i,
            "total_chunks": len(chunks),
            "is_final": i == len(chunks) - 1,
            "room_id": room_id
        }, room_id)
        
        # Small delay to simulate real streaming
        await asyncio.sleep(0.1)
    
    return {"message": f"Streamed {len(chunks)} chunks to room {room_id}"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
