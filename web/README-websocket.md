# Frontend WebSocket Integration

This document describes how to integrate WebSocket streaming into the DeerFlow frontend.

## Overview

The frontend WebSocket integration provides:

- **Real-time Communication**: Bidirectional communication between client and server
- **Research Streaming**: Live progress updates and results streaming  
- **Chat Functionality**: Multi-user chat with room support
- **Auto-reconnection**: Robust connection handling with automatic reconnection
- **Type Safety**: Full TypeScript support with proper typing

## Components Structure

```
web/src/
├── hooks/
│   └── useWebSocket.ts          # Core WebSocket hook
├── contexts/
│   └── WebSocketContext.tsx    # React context provider
├── components/
│   ├── ChatComponent.tsx       # Real-time chat component
│   └── ResearchComponent.tsx   # Research streaming component
└── app/
    └── websocket-test/
        └── page.tsx            # Test page demonstrating functionality
```

## Installation

The frontend already includes all necessary dependencies. WebSocket is a built-in browser API.

## Quick Start

### 1. Wrap your app with WebSocketProvider

```tsx
import { WebSocketProvider } from '@/contexts/WebSocketContext';

export default function App() {
  return (
    <WebSocketProvider
      defaultRoomId="main-room"
      wsUrl="ws://localhost:8001/ws"
      autoConnect={true}
    >
      <YourAppContent />
    </WebSocketProvider>
  );
}
```

### 2. Use WebSocket in components

```tsx
import { useWebSocketContext } from '@/contexts/WebSocketContext';

export function MyComponent() {
  const {
    isConnected,
    messages,
    sendChatMessage,
    sendResearchRequest
  } = useWebSocketContext();

  const handleSendMessage = () => {
    sendChatMessage("Hello, world!");
  };

  const handleStartResearch = () => {
    sendResearchRequest("AI trends 2024");
  };

  return (
    <div>
      <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>
      <button onClick={handleSendMessage}>Send Message</button>
      <button onClick={handleStartResearch}>Start Research</button>
      
      {messages.map((msg, i) => (
        <div key={i}>{msg.content}</div>
      ))}
    </div>
  );
}
```

## API Reference

### useWebSocket Hook

```tsx
const webSocket = useWebSocket({
  url: 'ws://localhost:8001/ws',
  clientId: 'user123',
  roomId: 'room1',
  autoConnect: true,
  reconnectInterval: 3000,
  maxReconnectAttempts: 5,
  heartbeatInterval: 30000
});
```

#### Returns:
- `isConnected: boolean` - Connection status
- `isConnecting: boolean` - Connecting state
- `isReconnecting: boolean` - Reconnecting state
- `messages: WebSocketMessage[]` - All received messages
- `progress: ProgressUpdate | null` - Current research progress
- `sendMessage(message)` - Send custom message
- `sendChatMessage(content)` - Send chat message
- `sendResearchRequest(query, requestId?)` - Start research
- `connect()` - Manual connect
- `disconnect()` - Manual disconnect

### WebSocketProvider Props

```tsx
interface WebSocketProviderProps {
  children: React.ReactNode;
  defaultRoomId?: string;      // Default: 'default'
  defaultClientId?: string;    // Auto-generated if not provided
  wsUrl?: string;             // Default: 'ws://localhost:8001/ws'
  autoConnect?: boolean;      // Default: true
}
```

### Message Types

#### Chat Message
```tsx
{
  type: 'chat_message',
  content: string,
  client_id: string,
  room_id: string,
  timestamp: string
}
```

#### Research Request
```tsx
{
  type: 'research_request',
  query: string,
  request_id: string
}
```

#### Progress Update
```tsx
{
  type: 'progress_update',
  request_id: string,
  stage: string,
  progress: number,      // 0-100
  message: string,
  timestamp: string
}
```

#### Research Result
```tsx
{
  type: 'research_result',
  request_id: string,
  content: string,
  section: string,
  is_final: boolean,
  timestamp: string
}
```

## Components

### ChatComponent

Full-featured chat component with:
- Real-time messaging
- Room switching
- Message history
- Connection status
- Typing indicators

```tsx
import { ChatComponent } from '@/components/ChatComponent';

<ChatComponent className="h-96" />
```

### ResearchComponent

AI research interface with:
- Query input
- Progress tracking
- Streaming results
- Report download
- Status indicators

```tsx
import { ResearchComponent } from '@/components/ResearchComponent';

<ResearchComponent className="h-96" />
```

## Testing

### Development Testing

1. Start the backend server:
```bash
cd deer-flow
python server.py --host 0.0.0.0 --port 8001
```

2. Start the frontend:
```bash
cd web
npm run dev
```

3. Visit the test page:
```
http://localhost:3000/websocket-test
```

### Test Page Features

The test page (`/websocket-test`) includes:
- Side-by-side chat and research components
- Multiple tabs simulation for multi-user testing
- Real-time connection status
- Complete message history
- Download functionality

### Manual Testing Steps

1. **Connection Testing**:
   - Open test page
   - Verify "Connected" status appears
   - Refresh page and check auto-reconnection

2. **Chat Testing**:
   - Open multiple browser tabs
   - Send messages between tabs
   - Switch rooms and verify isolation
   - Test with network disconnection

3. **Research Testing**:
   - Enter research query
   - Watch progress updates in real-time
   - Verify streaming results appear
   - Download final report

## Error Handling

The WebSocket implementation includes comprehensive error handling:

### Connection Errors
```tsx
const { lastError, isReconnecting, reconnectAttempts } = useWebSocketContext();

if (lastError) {
  console.error('WebSocket error:', lastError.message);
}
```

### Message Validation
All incoming messages are validated and parsed safely. Invalid messages are logged but don't crash the application.

### Automatic Recovery
- Auto-reconnection with exponential backoff
- Message queuing during disconnection
- Heartbeat mechanism for connection health
- State restoration after reconnection

## Performance Optimization

### Message Batching
```tsx
// Messages are automatically batched for performance
const messages = useWebSocketContext().messages; // Last 100 messages only
```

### Memory Management
- Message history is limited to prevent memory leaks
- Event listeners are properly cleaned up
- Timeouts and intervals are cleared on unmount

### Rendering Optimization
- Components use React.memo where appropriate
- Virtual scrolling for large message lists
- Debounced input handling

## Production Considerations

### Security
```tsx
// Use WSS in production
<WebSocketProvider wsUrl="wss://yourapp.com/ws">
```

### Load Balancing
When using multiple backend instances, ensure:
- Sticky sessions are configured
- Shared state for room management
- Proper WebSocket proxy configuration

### Monitoring
```tsx
// Track connection metrics
const { reconnectAttempts, lastError } = useWebSocketContext();

// Send to analytics
analytics.track('websocket_reconnect', { attempts: reconnectAttempts });
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Verify backend server is running
   - Check WebSocket URL and port
   - Ensure firewall allows WebSocket connections

2. **CORS Issues**
   - Backend CORS configuration includes WebSocket origin
   - Check browser console for CORS errors

3. **Auto-reconnection Not Working**
   - Check `maxReconnectAttempts` setting
   - Verify network connectivity
   - Check browser console for errors

4. **Messages Not Appearing**
   - Verify message format matches expected types
   - Check WebSocket connection status
   - Look for JSON parsing errors in console

### Debug Mode

Enable detailed logging:
```tsx
// Add to your component
useEffect(() => {
  const originalLog = console.log;
  console.log = (...args) => {
    if (args[0]?.includes?.('WebSocket')) {
      originalLog('[WS Debug]', ...args);
    }
    originalLog(...args);
  };
}, []);
```

## Integration with Existing Code

### Adding to Existing Pages

1. Wrap page with provider:
```tsx
// pages/research.tsx
import { WebSocketProvider } from '@/contexts/WebSocketContext';

export default function ResearchPage() {
  return (
    <WebSocketProvider>
      <ExistingResearchComponent />
    </WebSocketProvider>
  );
}
```

2. Enhance existing components:
```tsx
// Add WebSocket to existing component
function ExistingComponent() {
  const ws = useWebSocketOptional(); // Returns null if no provider
  
  if (ws?.isConnected) {
    // Use WebSocket features
  }
  
  // Existing functionality remains unchanged
}
```

### Migration Strategy

1. **Phase 1**: Add WebSocketProvider to app root
2. **Phase 2**: Gradually enhance existing components
3. **Phase 3**: Add new real-time features
4. **Phase 4**: Replace polling with WebSocket where appropriate

This approach ensures backward compatibility while progressively enhancing the application with real-time features.
