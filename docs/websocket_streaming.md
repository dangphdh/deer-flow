# WebSocket Streaming for DeerFlow

Tài liệu này mô tả cách sử dụng WebSocket streaming để có trải nghiệm real-time với DeerFlow.

## Tính năng

- **Real-time Communication**: Giao tiếp hai chiều giữa client và server
- **Room-based Chat**: Hỗ trợ nhiều phòng chat riêng biệt
- **Progress Streaming**: Theo dõi tiến trình research real-time
- **Auto-reconnect**: Tự động kết nối lại khi mất kết nối
- **Message Queuing**: Lưu trữ message khi offline
- **Heartbeat**: Maintain connection stability

## Cài đặt

Cài đặt dependencies:

```bash
pip install websockets
```

Hoặc nếu dùng uv:

```bash
uv add websockets
```

## Khởi chạy Server

```bash
python server.py --host 0.0.0.0 --port 8000
```

Server sẽ khởi chạy với WebSocket endpoints:

- `ws://localhost:8000/ws/{room_id}` - Kết nối đến room cụ thể
- `ws://localhost:8000/ws` - Kết nối đến room mặc định

## API Endpoints

### WebSocket Endpoints

- `GET /ws/test` - Trang test WebSocket
- `GET /ws/rooms` - Danh sách tất cả rooms
- `GET /ws/rooms/{room_id}` - Thông tin room cụ thể
- `POST /ws/rooms/{room_id}/broadcast` - Broadcast message đến room
- `POST /ws/broadcast` - Broadcast đến tất cả clients

### Test WebSocket

Truy cập `http://localhost:8000/ws/test` để test WebSocket functionality.

## Message Types

### Client → Server

#### Chat Message
```json
{
    "type": "chat_message",
    "content": "Hello world!"
}
```

#### Research Request
```json
{
    "type": "research_request",
    "query": "AI trends 2024",
    "request_id": "req_123"
}
```

#### Typing Indicator
```json
{
    "type": "typing_indicator",
    "is_typing": true
}
```

#### Room Info Request
```json
{
    "type": "room_info_request"
}
```

#### Heartbeat
```json
{
    "type": "heartbeat"
}
```

### Server → Client

#### Progress Update
```json
{
    "type": "progress_update",
    "request_id": "req_123",
    "stage": "searching",
    "progress": 30,
    "message": "Found: Example Article",
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### Research Result
```json
{
    "type": "research_result",
    "request_id": "req_123",
    "content": "Research content here...",
    "section": "Introduction",
    "is_final": false,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

#### User Joined/Left
```json
{
    "type": "user_joined",
    "client_id": "user_123",
    "room_participants": 3,
    "timestamp": "2024-01-15T10:30:00Z"
}
```

## Sử dụng Client-side

### JavaScript (Browser)

```javascript
// Tạo connection
const ws = new WebSocket('ws://localhost:8000/ws/my-room?client_id=user123');

// Lắng nghe events
ws.onopen = () => {
    console.log('Connected to WebSocket');
    
    // Gửi research request
    ws.send(JSON.stringify({
        type: 'research_request',
        query: 'AI trends 2024',
        request_id: 'req_' + Date.now()
    }));
};

ws.onmessage = (event) => {
    const data = JSON.parse(event.data);
    
    switch(data.type) {
        case 'progress_update':
            console.log(`Progress: ${data.progress}% - ${data.message}`);
            break;
        case 'research_result':
            console.log(`Result: ${data.content}`);
            if (data.is_final) {
                console.log('Research completed!');
            }
            break;
        case 'chat_message':
            console.log(`Message from ${data.sender}: ${data.content}`);
            break;
    }
};

ws.onclose = () => {
    console.log('Disconnected from WebSocket');
};
```

### Python Client

```python
import asyncio
import json
import websockets

async def client():
    uri = "ws://localhost:8000/ws/my-room?client_id=user123"
    
    async with websockets.connect(uri) as websocket:
        # Gửi research request
        await websocket.send(json.dumps({
            "type": "research_request",
            "query": "AI trends 2024",
            "request_id": "req_123"
        }))
        
        # Lắng nghe responses
        async for message in websocket:
            data = json.loads(message)
            print(f"Received: {data}")
            
            if data.get("type") == "research_result" and data.get("is_final"):
                print("Research completed!")
                break

# Chạy client
asyncio.run(client())
```

### React Hook

```javascript
import { useEffect, useState, useRef } from 'react';

export function useWebSocket(url, clientId, roomId) {
    const [isConnected, setIsConnected] = useState(false);
    const [messages, setMessages] = useState([]);
    const [progress, setProgress] = useState(null);
    const ws = useRef(null);

    useEffect(() => {
        const wsUrl = `${url}/${roomId}?client_id=${clientId}`;
        ws.current = new WebSocket(wsUrl);

        ws.current.onopen = () => {
            setIsConnected(true);
        };

        ws.current.onmessage = (event) => {
            const data = JSON.parse(event.data);
            
            if (data.type === 'progress_update') {
                setProgress(data);
            } else {
                setMessages(prev => [...prev, data]);
            }
        };

        ws.current.onclose = () => {
            setIsConnected(false);
        };

        return () => {
            ws.current?.close();
        };
    }, [url, clientId, roomId]);

    const sendMessage = (message) => {
        if (ws.current?.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify(message));
        }
    };

    const sendResearchRequest = (query) => {
        sendMessage({
            type: 'research_request',
            query,
            request_id: `req_${Date.now()}`
        });
    };

    return {
        isConnected,
        messages,
        progress,
        sendMessage,
        sendResearchRequest
    };
}
```

## Workflow Integration

WebSocket streaming được tích hợp với main workflow thông qua callbacks:

```python
from src.streaming import StreamingCallbacks

# Trong workflow nodes
async def search_node(state):
    # Notify start
    await StreamingCallbacks.on_search_start(
        request_id, search_query
    )
    
    # Perform search
    results = await search_function(query)
    
    # Notify results
    for result in results:
        await StreamingCallbacks.on_search_result(
            request_id, result.url, result.title
        )
    
    return {"search_results": results}
```

## Performance Tips

1. **Message Batching**: Gom nhiều message thành batch để giảm overhead
2. **Compression**: Sử dụng compression cho message lớn
3. **Room Management**: Giới hạn số lượng users per room
4. **Rate Limiting**: Implement rate limiting để tránh spam
5. **Heartbeat Tuning**: Điều chỉnh heartbeat interval phù hợp

## Troubleshooting

### Connection Issues

```bash
# Kiểm tra server đang chạy
curl http://localhost:8000/ws/rooms

# Test WebSocket connection
wscat -c ws://localhost:8000/ws/test-room
```

### Debug Logging

```python
import logging

# Enable WebSocket debug logging
logging.getLogger("src.streaming").setLevel(logging.DEBUG)
```

### Common Errors

1. **Connection Refused**: Kiểm tra server đang chạy và port
2. **JSON Parse Error**: Đảm bảo message format đúng
3. **Room Not Found**: Room sẽ được tạo tự động khi user join
4. **Heartbeat Timeout**: Kiểm tra network stability

## Security Considerations

1. **Authentication**: Implement proper authentication middleware
2. **Rate Limiting**: Prevent message flooding
3. **Input Validation**: Validate all incoming messages
4. **CORS**: Configure CORS settings properly
5. **WSS**: Sử dụng WSS (WebSocket Secure) trong production

## Production Deployment

```bash
# Sử dụng gunicorn với uvicorn workers
gunicorn src.server:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000

# Hoặc với uvicorn
uvicorn src.server:app --host 0.0.0.0 --port 8000 --workers 4
```

## Load Balancing

Khi deploy với multiple instances, cần sticky sessions hoặc shared state:

```nginx
upstream websocket {
    ip_hash;  # Sticky sessions
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /ws {
        proxy_pass http://websocket;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
    }
}
```

## Monitoring

```python
# Metrics collection
from src.streaming.websocket_manager import websocket_manager

# Get connection stats
stats = {
    "active_connections": len(websocket_manager.connection_manager.active_connections),
    "active_rooms": len(websocket_manager.connection_manager.rooms),
    "total_messages": websocket_manager.message_count
}
```
