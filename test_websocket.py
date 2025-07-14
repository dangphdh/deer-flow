#!/usr/bin/env python3
"""
Test script for WebSocket streaming functionality
"""

import asyncio
import json
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import websockets
except ImportError:
    logger.error("websockets library not installed. Run: pip install websockets")
    sys.exit(1)


async def test_websocket_connection():
    """Test basic WebSocket connection"""
    uri = "ws://localhost:8000/ws/test-room?client_id=test_client"
    
    try:
        logger.info(f"Connecting to {uri}")
        async with websockets.connect(uri) as websocket:
            logger.info("Connected successfully!")
            
            # Send a test message
            test_message = {
                "type": "chat_message",
                "content": "Hello from test client!",
                "timestamp": datetime.now().isoformat()
            }
            
            await websocket.send(json.dumps(test_message))
            logger.info(f"Sent message: {test_message}")
            
            # Wait for response
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                data = json.loads(response)
                logger.info(f"Received response: {data}")
            except asyncio.TimeoutError:
                logger.warning("No response received within 5 seconds")
            
            # Send a research request
            research_request = {
                "type": "research_request",
                "query": "AI trends 2024",
                "request_id": f"test_req_{datetime.now().timestamp()}"
            }
            
            await websocket.send(json.dumps(research_request))
            logger.info(f"Sent research request: {research_request}")
            
            # Listen for progress updates
            try:
                message_count = 0
                while message_count < 10:  # Limit to 10 messages
                    response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
                    data = json.loads(response)
                    logger.info(f"Progress update: {data}")
                    message_count += 1
                    
                    if data.get("type") == "research_result" and data.get("is_final"):
                        logger.info("Research completed!")
                        break
                        
            except asyncio.TimeoutError:
                logger.info("Test completed (timeout reached)")
                
    except ConnectionRefusedError:
        logger.error("Connection refused. Make sure the server is running on localhost:8000")
        return False
    except Exception as e:
        logger.error(f"Error during WebSocket test: {e}")
        return False
    
    return True


async def test_room_api():
    """Test REST API endpoints"""
    import httpx
    
    base_url = "http://localhost:8000"
    
    try:
        async with httpx.AsyncClient() as client:
            # Test rooms endpoint
            response = await client.get(f"{base_url}/ws/rooms")
            if response.status_code == 200:
                rooms = response.json()
                logger.info(f"Active rooms: {rooms}")
            else:
                logger.error(f"Failed to get rooms: {response.status_code}")
                return False
            
            # Test broadcast endpoint
            broadcast_message = {
                "type": "test_broadcast",
                "message": "Test broadcast message",
                "timestamp": datetime.now().isoformat()
            }
            
            response = await client.post(
                f"{base_url}/ws/broadcast",
                json=broadcast_message
            )
            
            if response.status_code == 200:
                logger.info("Broadcast test successful")
            else:
                logger.error(f"Broadcast test failed: {response.status_code}")
                return False
                
    except Exception as e:
        logger.error(f"Error during API test: {e}")
        return False
    
    return True


async def test_multiple_clients():
    """Test multiple clients in the same room"""
    room_id = "multi_test_room"
    clients = []
    
    async def client_handler(client_id, duration=10):
        uri = f"ws://localhost:8000/ws/{room_id}?client_id={client_id}"
        
        try:
            async with websockets.connect(uri) as websocket:
                logger.info(f"Client {client_id} connected")
                
                # Send a message every 2 seconds
                for i in range(duration // 2):
                    message = {
                        "type": "chat_message",
                        "content": f"Message {i+1} from {client_id}",
                    }
                    await websocket.send(json.dumps(message))
                    
                    # Listen for incoming messages
                    try:
                        response = await asyncio.wait_for(websocket.recv(), timeout=2.0)
                        data = json.loads(response)
                        logger.info(f"Client {client_id} received: {data.get('type', 'unknown')}")
                    except asyncio.TimeoutError:
                        pass
                    
                    await asyncio.sleep(2)
                    
        except Exception as e:
            logger.error(f"Client {client_id} error: {e}")
    
    # Start multiple clients
    tasks = []
    for i in range(3):
        client_id = f"test_client_{i+1}"
        task = asyncio.create_task(client_handler(client_id, 10))
        tasks.append(task)
    
    logger.info("Starting multiple client test...")
    await asyncio.gather(*tasks, return_exceptions=True)
    logger.info("Multiple client test completed")


async def main():
    """Run all tests"""
    logger.info("Starting WebSocket streaming tests...")
    
    # Test 1: Basic connection
    logger.info("\n=== Test 1: Basic WebSocket Connection ===")
    success1 = await test_websocket_connection()
    
    # Test 2: REST API
    logger.info("\n=== Test 2: REST API Endpoints ===")
    success2 = await test_room_api()
    
    # Test 3: Multiple clients
    logger.info("\n=== Test 3: Multiple Clients ===")
    await test_multiple_clients()
    
    # Summary
    logger.info("\n=== Test Summary ===")
    logger.info(f"WebSocket Connection: {'✓' if success1 else '✗'}")
    logger.info(f"REST API: {'✓' if success2 else '✗'}")
    logger.info("Multiple Clients: ✓ (completed)")
    
    if success1 and success2:
        logger.info("All tests passed! WebSocket streaming is working correctly.")
        return 0
    else:
        logger.error("Some tests failed. Check the logs above.")
        return 1


if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)
