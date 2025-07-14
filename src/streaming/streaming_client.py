"""
Client-side WebSocket streaming implementation
"""

import asyncio
import json
import logging
from typing import Dict, Any, Callable, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class StreamingClient:
    """Client-side WebSocket manager with auto-reconnect"""
    
    def __init__(self, url: str, client_id: str, room_id: str = "default", options: Dict[str, Any] = None):
        self.url = url
        self.client_id = client_id
        self.room_id = room_id
        self.options = options or {}
        
        # Connection settings
        self.reconnect_interval = self.options.get("reconnect_interval", 3)
        self.max_reconnect_attempts = self.options.get("max_reconnect_attempts", 5)
        self.heartbeat_interval = self.options.get("heartbeat_interval", 30)
        
        # State
        self.websocket = None
        self.is_connected = False
        self.reconnect_attempts = 0
        self.event_handlers = {}
        self.message_queue = []
        self.last_heartbeat = None
        
        # Tasks
        self.heartbeat_task = None
        self.reconnect_task = None
        
    def on(self, event: str, handler: Callable):
        """Register event handler"""
        if event not in self.event_handlers:
            self.event_handlers[event] = []
        self.event_handlers[event].append(handler)
    
    def emit(self, event: str, data: Any = None):
        """Emit event to handlers"""
        if event in self.event_handlers:
            for handler in self.event_handlers[event]:
                try:
                    if asyncio.iscoroutinefunction(handler):
                        asyncio.create_task(handler(data))
                    else:
                        handler(data)
                except Exception as e:
                    logger.error(f"Error in event handler for {event}: {e}")
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            import websockets
            
            full_url = f"{self.url}?client_id={self.client_id}&room_id={self.room_id}"
            self.websocket = await websockets.connect(full_url)
            
            self.is_connected = True
            self.reconnect_attempts = 0
            
            logger.info(f"Connected to WebSocket: {full_url}")
            self.emit("connected")
            
            # Start heartbeat
            self.start_heartbeat()
            
            # Send queued messages
            await self.send_queued_messages()
            
            # Start listening
            await self.listen()
            
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            self.is_connected = False
            self.emit("connection_failed", e)
            await self.handle_reconnect()
    
    async def listen(self):
        """Listen for incoming messages"""
        try:
            while self.is_connected and self.websocket:
                try:
                    message = await self.websocket.recv()
                    data = json.loads(message)
                    
                    # Handle special message types
                    message_type = data.get("type", "message")
                    
                    if message_type == "heartbeat_response":
                        self.last_heartbeat = datetime.now()
                        self.emit("heartbeat_received", data)
                    else:
                        self.emit("message", data)
                        self.emit(message_type, data)
                    
                except Exception as e:
                    if "ConnectionClosed" in str(type(e)):
                        logger.info("WebSocket connection closed")
                        break
                    elif "JSONDecodeError" in str(type(e)):
                        logger.error(f"Failed to parse message: {e}")
                    else:
                        logger.error(f"Error receiving message: {e}")
                    
        except Exception as e:
            logger.error(f"Listen error: {e}")
        finally:
            await self.disconnect()
    
    async def send(self, message: Dict[str, Any]):
        """Send message to server"""
        if not self.is_connected or not self.websocket:
            # Queue message for later
            self.message_queue.append(message)
            logger.warning("WebSocket not connected, message queued")
            return False
        
        try:
            # Add metadata
            message.update({
                "client_id": self.client_id,
                "room_id": self.room_id,
                "timestamp": datetime.now().isoformat()
            })
            
            await self.websocket.send(json.dumps(message))
            self.emit("message_sent", message)
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
            self.message_queue.append(message)
            return False
    
    async def send_queued_messages(self):
        """Send all queued messages"""
        while self.message_queue and self.is_connected:
            message = self.message_queue.pop(0)
            success = await self.send(message)
            if not success:
                # Put message back at front of queue
                self.message_queue.insert(0, message)
                break
    
    def start_heartbeat(self):
        """Start heartbeat task"""
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
        
        self.heartbeat_task = asyncio.create_task(self.heartbeat_loop())
    
    async def heartbeat_loop(self):
        """Send periodic heartbeats"""
        while self.is_connected:
            try:
                await asyncio.sleep(self.heartbeat_interval)
                
                if self.is_connected:
                    await self.send({"type": "heartbeat"})
                    
                    # Check if we received heartbeat response recently
                    if self.last_heartbeat:
                        time_since_heartbeat = (datetime.now() - self.last_heartbeat).total_seconds()
                        if time_since_heartbeat > self.heartbeat_interval * 2:
                            logger.warning("Heartbeat timeout, reconnecting...")
                            await self.disconnect()
                            break
                            
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
                break
    
    async def disconnect(self):
        """Disconnect from WebSocket"""
        self.is_connected = False
        
        # Cancel tasks
        if self.heartbeat_task:
            self.heartbeat_task.cancel()
            self.heartbeat_task = None
        
        # Close WebSocket
        if self.websocket:
            try:
                await self.websocket.close()
            except:
                pass
            self.websocket = None
        
        self.emit("disconnected")
        
        # Auto-reconnect if enabled
        if self.reconnect_attempts < self.max_reconnect_attempts:
            await self.handle_reconnect()
    
    async def handle_reconnect(self):
        """Handle reconnection logic"""
        if self.reconnect_task:
            return  # Already trying to reconnect
        
        self.reconnect_attempts += 1
        
        if self.reconnect_attempts <= self.max_reconnect_attempts:
            logger.info(f"Attempting to reconnect... ({self.reconnect_attempts}/{self.max_reconnect_attempts})")
            self.emit("reconnecting", self.reconnect_attempts)
            
            self.reconnect_task = asyncio.create_task(self.reconnect_delay())
        else:
            logger.error("Max reconnection attempts reached")
            self.emit("max_reconnect_reached")
    
    async def reconnect_delay(self):
        """Wait before reconnecting"""
        try:
            await asyncio.sleep(self.reconnect_interval)
            await self.connect()
        except asyncio.CancelledError:
            pass
        finally:
            self.reconnect_task = None
    
    async def close(self):
        """Manually close connection"""
        self.max_reconnect_attempts = 0  # Disable auto-reconnect
        await self.disconnect()
        
        if self.reconnect_task:
            self.reconnect_task.cancel()
    
    # Convenience methods for common message types
    async def send_chat_message(self, content: str):
        """Send a chat message"""
        return await self.send({
            "type": "chat_message",
            "content": content
        })
    
    async def send_research_request(self, query: str, request_id: str = None):
        """Send a research request"""
        return await self.send({
            "type": "research_request",
            "query": query,
            "request_id": request_id or f"req_{datetime.now().timestamp()}"
        })
    
    async def send_typing_indicator(self, is_typing: bool):
        """Send typing indicator"""
        return await self.send({
            "type": "typing_indicator",
            "is_typing": is_typing
        })
    
    async def request_room_info(self):
        """Request room information"""
        return await self.send({
            "type": "room_info_request"
        })


# Factory function for easier client creation
def create_streaming_client(url: str, client_id: str, room_id: str = "default", **options) -> StreamingClient:
    """Create a new streaming client instance"""
    return StreamingClient(url, client_id, room_id, options)
