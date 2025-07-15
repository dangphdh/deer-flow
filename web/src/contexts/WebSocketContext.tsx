/**
 * WebSocket Context Provider for global WebSocket state management
 */

'use client';

import React, { createContext, useContext, useEffect, useState } from 'react';

import { useWebSocket, type WebSocketOptions, type WebSocketMessage, type ProgressUpdate } from '../hooks/useWebSocket';

interface WebSocketContextValue {
  // Connection state
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  reconnectAttempts: number;
  lastError: Error | null;
  
  // Messages and progress
  messages: WebSocketMessage[];
  progress: ProgressUpdate | null;
  
  // Actions
  connect: () => void;
  disconnect: () => void;
  sendMessage: (message: Omit<WebSocketMessage, 'client_id' | 'room_id' | 'timestamp'> & { type: string }) => boolean;
  clearMessages: () => void;
  
  // Convenience methods
  sendChatMessage: (content: string) => boolean;
  sendResearchRequest: (query: string, requestId?: string) => boolean;
  sendTypingIndicator: (isTyping: boolean) => boolean;
  requestRoomInfo: () => boolean;
  
  // Room management
  roomId: string;
  clientId: string;
  setRoomId: (roomId: string) => void;
}

const WebSocketContext = createContext<WebSocketContextValue | null>(null);

interface WebSocketProviderProps {
  children: React.ReactNode;
  defaultRoomId?: string;
  defaultClientId?: string;
  wsUrl?: string;
  autoConnect?: boolean;
}

export function WebSocketProvider({
  children,
  defaultRoomId = 'default',
  defaultClientId = `client_${Math.random().toString(36).substr(2, 9)}`,
  wsUrl = 'ws://localhost:8001/ws',
  autoConnect = true,
}: WebSocketProviderProps) {
  const [roomId, setRoomId] = useState(defaultRoomId);
  const [clientId] = useState(defaultClientId);

  const wsOptions: WebSocketOptions = {
    url: wsUrl,
    clientId,
    roomId,
    autoConnect,
    reconnectInterval: 3000,
    maxReconnectAttempts: 5,
    heartbeatInterval: 30000,
  };

  const webSocket = useWebSocket(wsOptions);

  // Reconnect when room changes
  useEffect(() => {
    if (webSocket.isConnected) {
      webSocket.disconnect();
      setTimeout(() => {
        webSocket.connect();
      }, 100);
    }
  }, [roomId]); // eslint-disable-line react-hooks/exhaustive-deps

  const contextValue: WebSocketContextValue = {
    ...webSocket,
    roomId,
    clientId,
    setRoomId,
  };

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
}

export function useWebSocketContext() {
  const context = useContext(WebSocketContext);
  if (!context) {
    throw new Error('useWebSocketContext must be used within a WebSocketProvider');
  }
  return context;
}

// Hook for conditional WebSocket usage
export function useWebSocketOptional() {
  return useContext(WebSocketContext);
}
