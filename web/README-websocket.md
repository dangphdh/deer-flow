# WebSocket Frontend Integration

## Overview

Frontend đã được tích hợp WebSocket streaming để enhance trải nghiệm real-time kết hợp với SSE streaming hiện tại.

## Architecture

### Current State
- **SSE (Server-Sent Events)**: Đang được sử dụng cho research streaming chính 
- **Frontend Implementation**: React hooks và components

### Added WebSocket Features
- **Real-time Communication**: Chat, notifications, progress updates
- **Hybrid Streaming**: Kết hợp SSE và WebSocket
- **Auto-reconnect**: Tự động kết nối lại khi mất connection
- **Fallback**: Fallback từ WebSocket về SSE khi cần

## Files Added

### 1. WebSocket Hook (`useWebSocket.ts`)
```typescript
import { useWebSocket } from '~/hooks/useWebSocket';

const webSocket = useWebSocket(
  'ws://localhost:8000/ws',
  'client_id',
  'room_id'
);
```

### 2. Hybrid Streaming Hook (`useHybridStreaming.ts`)
```typescript
import { useHybridStreaming } from '~/hooks/useHybridStreaming';

const {
  startResearchStream,
  sendChatMessage,
  progress,
  isWebSocketConnected
} = useHybridStreaming();
```

### 3. Demo Component (`websocket-demo.tsx`)
```typescript
import { WebSocketDemo } from '~/components/websocket-demo';
```

### 4. Test Page (`/websocket-test`)
Truy cập `/websocket-test` để test functionality

## Usage Examples

### Basic WebSocket Connection
```typescript
const {
  isConnected,
  sendMessage,
  messages,
  on: addEventListener
} = useWebSocket('ws://localhost:8000/ws', 'my-client', 'my-room');

// Listen for events
addEventListener('progress', (data) => {
  console.log('Progress:', data);
});

// Send message
sendMessage({
  type: 'chat_message',
  data: { content: 'Hello!' }
});
```

### Hybrid Streaming for Research
```typescript
const {
  startResearchStream,
  progress,
  messages,
  isWebSocketConnected,
  streamingMethod
} = useHybridStreaming({
  enableWebSocket: true,
  enableSSE: true,
  fallbackToSSE: true
});

// Start research with WebSocket progress updates
await startResearchStream('AI trends 2024', {
  thread_id: 'my-thread',
  auto_accepted_plan: true,
  max_plan_iterations: 3
});
```

## Integration Strategy

### 1. Keep Existing SSE for Main Research
- Existing `chatStream` function continues to work
- SSE handles main research content streaming
- No breaking changes to existing functionality

### 2. Add WebSocket for Real-time Features
- Progress updates during research
- Real-time chat between users
- Room-based collaboration
- Live notifications

### 3. Hybrid Approach Benefits
- **Reliability**: Fallback to SSE if WebSocket fails
- **Performance**: Use best tool for each use case
- **Backwards Compatibility**: Existing code continues to work
- **Progressive Enhancement**: Add real-time features incrementally

## Current Frontend Streaming

### Existing SSE Implementation
```typescript
// Located in: src/core/sse/fetch-stream.ts
export async function* fetchStream(
  url: string,
  init: RequestInit,
): AsyncIterable<StreamEvent>

// Used in: src/core/api/chat.ts
export async function* chatStream(
  userMessage: string,
  params: {...}
)
```

### How SSE is Used
```typescript
// In store.ts
const stream = chatStream(content, {
  thread_id: THREAD_ID,
  interrupt_feedback: interruptFeedback,
  resources,
  // ... other params
});

// Process stream
for await (const event of stream) {
  // Handle streaming events
}
```

## Migration Plan

### Phase 1: Add WebSocket Infrastructure ✅
- [x] Create WebSocket hooks
- [x] Create hybrid streaming
- [x] Add demo components
- [x] Test basic functionality

### Phase 2: Integrate with Existing UI
- [ ] Add WebSocket toggle to settings
- [ ] Integrate progress display in main chat UI
- [ ] Add real-time user indicators
- [ ] Connect to existing message components

### Phase 3: Enhanced Features
- [ ] Multi-user collaboration
- [ ] Real-time typing indicators
- [ ] Live result sharing
- [ ] Push notifications

## Testing

### 1. Backend Setup
```bash
# Make sure backend supports WebSocket
python server.py --host 0.0.0.0 --port 8000
```

### 2. Frontend Testing
```bash
# Start frontend
npm run dev

# Visit test page
http://localhost:3000/websocket-test
```

### 3. Test Scenarios
1. **Connection Test**: Connect/disconnect WebSocket
2. **Research Streaming**: Start research and watch progress
3. **Chat Messages**: Send real-time chat messages
4. **Fallback Test**: Disable WebSocket, ensure SSE works
5. **Multi-tab Test**: Open multiple tabs, test room communication

## Configuration

### Environment Variables
```env
# Backend WebSocket URL
NEXT_PUBLIC_WEBSOCKET_URL=ws://localhost:8000/ws

# Enable/disable WebSocket
NEXT_PUBLIC_ENABLE_WEBSOCKET=true

# Fallback to SSE
NEXT_PUBLIC_WEBSOCKET_FALLBACK=true
```

### Hook Options
```typescript
const options = {
  reconnectInterval: 3000,        // ms between reconnect attempts
  maxReconnectAttempts: 5,        // max reconnection tries
  heartbeatInterval: 30000,       // heartbeat frequency
  autoConnect: true,              // auto-connect on mount
  enableWebSocket: true,          // enable WebSocket features
  enableSSE: true,                // enable SSE fallback
  fallbackToSSE: true,           // auto-fallback on WS failure
};
```

## Benefits of This Approach

### 1. Non-Breaking Integration
- Existing SSE streaming continues to work
- New WebSocket features are additive
- Gradual migration possible

### 2. Best of Both Worlds
- **SSE**: Reliable for one-way streaming (research results)
- **WebSocket**: Better for real-time, bi-directional features
- **Hybrid**: Combines reliability with real-time capabilities

### 3. Production Ready
- Auto-reconnection for reliability
- Fallback mechanisms for robustness
- Error handling and recovery
- Performance optimizations

### 4. Developer Experience
- Simple hooks for easy integration
- TypeScript support
- Comprehensive testing tools
- Good separation of concerns

## Next Steps

1. **Test the Implementation**
   - Start backend with WebSocket support
   - Test `/websocket-test` page
   - Verify SSE still works

2. **Integrate with Main UI**
   - Add WebSocket toggle to settings
   - Show connection status
   - Display real-time progress

3. **Add Collaborative Features**
   - Multi-user research sessions
   - Shared progress viewing
   - Real-time result sharing

4. **Optimize Performance**
   - Message batching
   - Connection pooling
   - Bandwidth optimization