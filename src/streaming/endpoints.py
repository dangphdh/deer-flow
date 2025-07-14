"""
FastAPI WebSocket endpoints for streaming
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import HTMLResponse
import json
import uuid
from typing import Optional

from .websocket_manager import websocket_manager, ConnectionManager
from .message_handler import MESSAGE_HANDLERS, MIDDLEWARE_STACK

# Initialize WebSocket manager with handlers and middleware
for message_type, handler in MESSAGE_HANDLERS.items():
    websocket_manager.add_message_handler(message_type, handler)

for middleware in MIDDLEWARE_STACK:
    websocket_manager.add_middleware(middleware)


def setup_websocket_routes(app: FastAPI):
    """Setup WebSocket routes for FastAPI app"""
    
    @app.websocket("/ws/{room_id}")
    async def websocket_endpoint(websocket: WebSocket, room_id: str, client_id: Optional[str] = None):
        """Main WebSocket endpoint"""
        if not client_id:
            client_id = str(uuid.uuid4())
        
        await websocket_manager.handle_websocket(websocket, client_id, room_id)
    
    @app.websocket("/ws")
    async def websocket_endpoint_default(websocket: WebSocket, client_id: Optional[str] = None):
        """Default WebSocket endpoint (default room)"""
        if not client_id:
            client_id = str(uuid.uuid4())
        
        await websocket_manager.handle_websocket(websocket, client_id, "default")
    
    @app.get("/ws/rooms")
    async def get_rooms():
        """Get all active rooms"""
        return websocket_manager.connection_manager.get_all_rooms()
    
    @app.get("/ws/rooms/{room_id}")
    async def get_room_info(room_id: str):
        """Get information about a specific room"""
        room_info = websocket_manager.connection_manager.get_room_info(room_id)
        if room_info["participants"] == 0 and room_id not in websocket_manager.connection_manager.rooms:
            raise HTTPException(status_code=404, detail="Room not found")
        return room_info
    
    @app.post("/ws/rooms/{room_id}/broadcast")
    async def broadcast_to_room(room_id: str, message: dict):
        """Broadcast message to all clients in a room"""
        await websocket_manager.connection_manager.broadcast_to_room(room_id, message)
        return {"status": "message broadcasted", "room_id": room_id}
    
    @app.post("/ws/broadcast")
    async def broadcast_to_all(message: dict):
        """Broadcast message to all connected clients"""
        await websocket_manager.connection_manager.broadcast_to_all(message)
        return {"status": "message broadcasted to all"}
    
    @app.get("/ws/test")
    async def websocket_test_page():
        """Test page for WebSocket functionality"""
        return HTMLResponse("""
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket Test</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .container { max-width: 800px; margin: 0 auto; }
        .messages { border: 1px solid #ccc; height: 300px; overflow-y: scroll; padding: 10px; margin: 10px 0; }
        .message { margin: 5px 0; padding: 5px; background: #f5f5f5; border-radius: 3px; }
        .input-group { margin: 10px 0; }
        .input-group input, .input-group button { padding: 8px; margin: 5px; }
        .status { padding: 10px; margin: 10px 0; border-radius: 3px; }
        .connected { background: #d4edda; color: #155724; }
        .disconnected { background: #f8d7da; color: #721c24; }
        .reconnecting { background: #fff3cd; color: #856404; }
    </style>
</head>
<body>
    <div class="container">
        <h1>WebSocket Test</h1>
        
        <div class="input-group">
            <input type="text" id="roomId" placeholder="Room ID" value="test-room">
            <input type="text" id="clientId" placeholder="Client ID" value="">
            <button onclick="connect()">Connect</button>
            <button onclick="disconnect()">Disconnect</button>
        </div>
        
        <div id="status" class="status disconnected">Disconnected</div>
        
        <div class="input-group">
            <input type="text" id="messageInput" placeholder="Type a message..." disabled>
            <button onclick="sendMessage()" disabled id="sendBtn">Send</button>
            <button onclick="sendResearchRequest()" disabled id="researchBtn">Research</button>
        </div>
        
        <div id="messages" class="messages"></div>
    </div>

    <script>
        let ws = null;
        let clientId = Math.random().toString(36).substr(2, 9);
        
        document.getElementById('clientId').value = clientId;
        
        function updateStatus(status, className) {
            const statusEl = document.getElementById('status');
            statusEl.textContent = status;
            statusEl.className = 'status ' + className;
        }
        
        function addMessage(message) {
            const messagesEl = document.getElementById('messages');
            const messageEl = document.createElement('div');
            messageEl.className = 'message';
            messageEl.innerHTML = '<strong>' + new Date().toLocaleTimeString() + '</strong>: ' + JSON.stringify(message, null, 2);
            messagesEl.appendChild(messageEl);
            messagesEl.scrollTop = messagesEl.scrollHeight;
        }
        
        function connect() {
            const roomId = document.getElementById('roomId').value;
            clientId = document.getElementById('clientId').value || clientId;
            
            const wsUrl = `ws://localhost:8000/ws/${roomId}?client_id=${clientId}`;
            
            updateStatus('Connecting...', 'reconnecting');
            
            ws = new WebSocket(wsUrl);
            
            ws.onopen = function() {
                updateStatus('Connected', 'connected');
                document.getElementById('messageInput').disabled = false;
                document.getElementById('sendBtn').disabled = false;
                document.getElementById('researchBtn').disabled = false;
                addMessage({type: 'system', message: 'Connected to room: ' + roomId});
            };
            
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data);
                addMessage(data);
            };
            
            ws.onclose = function() {
                updateStatus('Disconnected', 'disconnected');
                document.getElementById('messageInput').disabled = true;
                document.getElementById('sendBtn').disabled = true;
                document.getElementById('researchBtn').disabled = true;
                addMessage({type: 'system', message: 'Disconnected'});
            };
            
            ws.onerror = function(error) {
                updateStatus('Error', 'disconnected');
                addMessage({type: 'error', message: 'WebSocket error: ' + error});
            };
        }
        
        function disconnect() {
            if (ws) {
                ws.close();
            }
        }
        
        function sendMessage() {
            const input = document.getElementById('messageInput');
            if (ws && input.value.trim()) {
                const message = {
                    type: 'chat_message',
                    content: input.value.trim()
                };
                ws.send(JSON.stringify(message));
                input.value = '';
            }
        }
        
        function sendResearchRequest() {
            const query = prompt('Enter research query:');
            if (ws && query) {
                const message = {
                    type: 'research_request',
                    query: query,
                    request_id: 'req_' + Date.now()
                };
                ws.send(JSON.stringify(message));
            }
        }
        
        // Send message on Enter key
        document.getElementById('messageInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendMessage();
            }
        });
    </script>
</body>
</html>
        """)


# Export the setup function
__all__ = ['setup_websocket_routes']
