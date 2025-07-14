#!/usr/bin/env python3
"""
WebSocket Test Client
Tests the WebSocket streaming functionality
"""

import asyncio
import websockets
import json
import sys
from datetime import datetime

class WebSocketTestClient:
    def __init__(self, uri="ws://localhost:8001/ws/test"):
        self.uri = uri
        self.websocket = None
        self.running = False
    
    async def connect(self):
        """Connect to WebSocket server"""
        try:
            self.websocket = await websockets.connect(self.uri)
            print(f"✅ Connected to {self.uri}")
            return True
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            return False
    
    async def disconnect(self):
        """Disconnect from WebSocket server"""
        if self.websocket:
            await self.websocket.close()
            print("📡 Disconnected")
    
    async def send_message(self, message):
        """Send a message to the server"""
        if not self.websocket:
            print("❌ Not connected")
            return
        
        try:
            await self.websocket.send(json.dumps(message))
            print(f"📤 Sent: {message}")
        except Exception as e:
            print(f"❌ Send failed: {e}")
    
    async def listen(self):
        """Listen for messages from server"""
        if not self.websocket:
            print("❌ Not connected")
            return
        
        try:
            async for message in self.websocket:
                data = json.loads(message)
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"📥 [{timestamp}] Received: {data}")
                
                # Handle different message types
                if data.get("type") == "connection":
                    print(f"🔗 Connection established in room: {data.get('room_id')}")
                elif data.get("type") == "streaming":
                    chunk_id = data.get("chunk_id", 0)
                    is_final = data.get("is_final", False)
                    chunk = data.get("data", {}).get("chunk", "")
                    print(f"🌊 Stream chunk {chunk_id}: '{chunk}' {'(FINAL)' if is_final else ''}")
                
        except websockets.exceptions.ConnectionClosed:
            print("🔌 Connection closed by server")
        except Exception as e:
            print(f"❌ Listen error: {e}")
    
    async def send_ping(self):
        """Send ping message"""
        await self.send_message({"type": "ping"})
    
    async def send_broadcast(self, content):
        """Send broadcast message"""
        await self.send_message({
            "type": "broadcast",
            "content": content,
            "sender": "test_client"
        })
    
    async def send_streaming_data(self, data):
        """Send streaming data"""
        await self.send_message({
            "type": "streaming",
            "data": data,
            "chunk_id": 0,
            "is_final": True
        })

async def test_basic_connection():
    """Test basic WebSocket connection"""
    print("\n🧪 Testing basic connection...")
    
    client = WebSocketTestClient()
    
    if await client.connect():
        # Start listening in background
        listen_task = asyncio.create_task(client.listen())
        
        # Wait a bit for connection message
        await asyncio.sleep(1)
        
        # Send ping
        await client.send_ping()
        await asyncio.sleep(0.5)
        
        # Send broadcast message
        await client.send_broadcast("Hello from test client!")
        await asyncio.sleep(0.5)
        
        # Send streaming data
        await client.send_streaming_data({"test": "streaming data"})
        await asyncio.sleep(0.5)
        
        # Cancel listening and disconnect
        listen_task.cancel()
        await client.disconnect()
        
        print("✅ Basic connection test completed")
    else:
        print("❌ Basic connection test failed")

async def test_multiple_clients():
    """Test multiple WebSocket clients"""
    print("\n🧪 Testing multiple clients...")
    
    clients = []
    tasks = []
    
    # Create multiple clients
    for i in range(3):
        client = WebSocketTestClient(f"ws://localhost:8001/ws/test_room_{i}")
        clients.append(client)
    
    try:
        # Connect all clients
        for i, client in enumerate(clients):
            if await client.connect():
                print(f"Client {i+1} connected")
                # Start listening for each client
                task = asyncio.create_task(client.listen())
                tasks.append(task)
            else:
                print(f"Client {i+1} failed to connect")
        
        await asyncio.sleep(1)
        
        # Send messages from each client
        for i, client in enumerate(clients):
            await client.send_broadcast(f"Message from client {i+1}")
            await asyncio.sleep(0.3)
        
        await asyncio.sleep(2)
        
    finally:
        # Cleanup
        for task in tasks:
            task.cancel()
        
        for client in clients:
            await client.disconnect()
        
        print("✅ Multiple clients test completed")

async def test_streaming_simulation():
    """Test streaming simulation endpoint"""
    print("\n🧪 Testing streaming simulation...")
    
    import aiohttp
    
    try:
        async with aiohttp.ClientSession() as session:
            # First, connect a WebSocket client to receive the stream
            client = WebSocketTestClient("ws://localhost:8001/ws/stream_test")
            
            if await client.connect():
                # Start listening
                listen_task = asyncio.create_task(client.listen())
                
                await asyncio.sleep(1)
                
                # Trigger streaming simulation via HTTP
                async with session.post(
                    "http://localhost:8001/simulate_stream/stream_test",
                    json={
                        "content": "This is a long message that will be chunked into smaller pieces for streaming",
                        "chunk_size": 15
                    }
                ) as response:
                    result = await response.json()
                    print(f"📡 Simulation response: {result}")
                
                # Wait for streaming to complete
                await asyncio.sleep(3)
                
                # Cleanup
                listen_task.cancel()
                await client.disconnect()
                
                print("✅ Streaming simulation test completed")
            else:
                print("❌ Failed to connect for streaming test")
                
    except Exception as e:
        print(f"❌ Streaming simulation test failed: {e}")

async def main():
    """Run all tests"""
    print("🚀 Starting WebSocket Tests")
    print("=" * 50)
    
    try:
        # Test basic connection
        await test_basic_connection()
        
        # Test multiple clients
        await test_multiple_clients()
        
        # Test streaming simulation
        await test_streaming_simulation()
        
        print("\n🎉 All tests completed!")
        
    except KeyboardInterrupt:
        print("\n⏹️ Tests interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")

if __name__ == "__main__":
    print("WebSocket Test Client")
    print("Make sure the WebSocket server is running on localhost:8001")
    print("Press Ctrl+C to stop\n")
    
    # Check if server should be started
    if len(sys.argv) > 1 and sys.argv[1] == "--help":
        print("Usage:")
        print("  python test_websocket.py          # Run tests")
        print("  python test_websocket.py --help   # Show this help")
        sys.exit(0)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
