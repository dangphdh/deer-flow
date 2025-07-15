/**
 * WebSocket hook for real-time communication
 */

import { useCallback, useEffect, useRef, useState } from 'react';

export interface WebSocketMessage {
  type: string;
  content?: string;
  timestamp?: string;
  client_id?: string;
  room_id?: string;
  query?: string;
  request_id?: string;
  stage?: string;
  progress?: number;
  message?: string;
  section?: string;
  is_final?: boolean;
  [key: string]: unknown;
}

export interface ProgressUpdate {
  type: 'progress_update';
  request_id: string;
  stage: string;
  progress: number;
  message: string;
  timestamp: string;
}

export interface ResearchResult {
  type: 'research_result';
  request_id: string;
  content: string;
  section: string;
  is_final: boolean;
  timestamp: string;
}

export interface WebSocketOptions {
  url: string;
  clientId: string;
  roomId: string;
  autoConnect?: boolean;
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  isReconnecting: boolean;
  reconnectAttempts: number;
  lastError: Error | null;
  messages: WebSocketMessage[];
  progress: ProgressUpdate | null;
}

export function useWebSocket(options: WebSocketOptions) {
  const {
    url,
    clientId,
    roomId,
    autoConnect = true,
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    isReconnecting: false,
    reconnectAttempts: 0,
    lastError: null,
    messages: [],
    progress: null,
  });

  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const heartbeatTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueueRef = useRef<WebSocketMessage[]>([]);

  const updateState = useCallback((updates: Partial<WebSocketState>) => {
    setState(prev => ({ ...prev, ...updates }));
  }, []);

  const addMessage = useCallback((message: WebSocketMessage) => {
    setState(prev => ({
      ...prev,
      messages: [...prev.messages.slice(-99), message], // Keep last 100 messages
    }));
  }, []);

  const updateProgress = useCallback((progress: ProgressUpdate) => {
    setState(prev => ({ ...prev, progress }));
  }, []);

  const clearMessages = useCallback(() => {
    setState(prev => ({ ...prev, messages: [] }));
  }, []);

  const sendMessage = useCallback((message: Omit<WebSocketMessage, 'client_id' | 'room_id' | 'timestamp'> & { type: string }) => {
    const fullMessage: WebSocketMessage = {
      ...message,
      client_id: clientId,
      room_id: roomId,
      timestamp: new Date().toISOString(),
    };

    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(fullMessage));
      return true;
    } else {
      // Queue message for later
      messageQueueRef.current.push(fullMessage);
      return false;
    }
  }, [clientId, roomId]);

  const sendQueuedMessages = useCallback(() => {
    while (messageQueueRef.current.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
      const message = messageQueueRef.current.shift();
      if (message) {
        wsRef.current.send(JSON.stringify(message));
      }
    }
  }, []);

  const startHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
    }

    const sendHeartbeat = () => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        sendMessage({ type: 'heartbeat' });
        heartbeatTimeoutRef.current = setTimeout(sendHeartbeat, heartbeatInterval);
      }
    };

    heartbeatTimeoutRef.current = setTimeout(sendHeartbeat, heartbeatInterval);
  }, [sendMessage, heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatTimeoutRef.current) {
      clearTimeout(heartbeatTimeoutRef.current);
      heartbeatTimeoutRef.current = null;
    }
  }, []);

  const handleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    setState(prev => ({
      ...prev,
      isReconnecting: true,
      reconnectAttempts: prev.reconnectAttempts + 1,
    }));

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, reconnectInterval);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [reconnectInterval]); // Remove connect dependency to avoid circular dependency

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    updateState({ isConnecting: true, lastError: null });

    try {
      const wsUrl = `${url}/${roomId}?client_id=${clientId}`;
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        updateState({
          isConnected: true,
          isConnecting: false,
          isReconnecting: false,
          reconnectAttempts: 0,
          lastError: null,
        });
        
        startHeartbeat();
        sendQueuedMessages();
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          if (message.type === 'progress_update') {
            updateProgress(message as unknown as ProgressUpdate);
          } else if (message.type === 'heartbeat_response') {
            // Handle heartbeat response
            console.log('Heartbeat received');
          } else {
            addMessage(message);
          }
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        updateState({ isConnected: false, isConnecting: false });
        stopHeartbeat();

        if (state.reconnectAttempts < maxReconnectAttempts && !event.wasClean) {
          handleReconnect();
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        updateState({ 
          lastError: new Error('WebSocket connection error'),
          isConnecting: false 
        });
      };

    } catch (error) {
      console.error('Failed to create WebSocket:', error);
      updateState({ 
        isConnecting: false,
        lastError: error instanceof Error ? error : new Error('Failed to create WebSocket')
      });
    }
  }, [url, clientId, roomId, state.reconnectAttempts, maxReconnectAttempts, updateState, startHeartbeat, sendQueuedMessages, addMessage, updateProgress, stopHeartbeat, handleReconnect]);

  const disconnect = useCallback(() => {
    stopHeartbeat();
    
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    updateState({
      isConnected: false,
      isConnecting: false,
      isReconnecting: false,
      reconnectAttempts: 0,
    });
  }, [updateState, stopHeartbeat]);

  // Auto-connect on mount
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  // Convenience methods
  const sendChatMessage = useCallback((content: string) => {
    return sendMessage({
      type: 'chat_message',
      content,
    });
  }, [sendMessage]);

  const sendResearchRequest = useCallback((query: string, requestId?: string) => {
    return sendMessage({
      type: 'research_request',
      query,
      request_id: requestId ?? `req_${Date.now()}`,
    });
  }, [sendMessage]);

  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    return sendMessage({
      type: 'typing_indicator',
      is_typing: isTyping,
    });
  }, [sendMessage]);

  const requestRoomInfo = useCallback(() => {
    return sendMessage({
      type: 'room_info_request',
    });
  }, [sendMessage]);

  return {
    // State
    ...state,
    
    // Actions
    connect,
    disconnect,
    sendMessage,
    clearMessages,
    
    // Convenience methods
    sendChatMessage,
    sendResearchRequest,
    sendTypingIndicator,
    requestRoomInfo,
  };
}
