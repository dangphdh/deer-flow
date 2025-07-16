// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useCallback, useEffect, useRef, useState } from 'react';

export interface WebSocketMessage {
  type: string;
  data?: unknown;
  timestamp?: string;
  client_id?: string;
  room_id?: string;
}

export interface ProgressData {
  stage: string;
  progress: number;
  message: string;
  request_id: string;
}

export interface WebSocketOptions {
  reconnectInterval?: number;
  maxReconnectAttempts?: number;
  heartbeatInterval?: number;
  autoConnect?: boolean;
}

export interface WebSocketState {
  isConnected: boolean;
  isConnecting: boolean;
  reconnectAttempts: number;
  lastMessage?: WebSocketMessage;
  error?: Error;
}

export function useWebSocket(
  url: string,
  clientId: string,
  roomId = 'default',
  options: WebSocketOptions = {}
) {
  const {
    reconnectInterval = 3000,
    maxReconnectAttempts = 5,
    heartbeatInterval = 30000,
    autoConnect = true,
  } = options;

  const [state, setState] = useState<WebSocketState>({
    isConnected: false,
    isConnecting: false,
    reconnectAttempts: 0,
  });

  const [messages, setMessages] = useState<WebSocketMessage[]>([]);
  const [progress, setProgress] = useState<ProgressData | null>(null);

  const wsRef = useRef<WebSocket | null>(null);
  const heartbeatRef = useRef<NodeJS.Timeout | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);
  const messageQueue = useRef<WebSocketMessage[]>([]);

  // Event handlers
  const eventHandlers = useRef<Map<string, ((data: unknown) => void)[]>>(new Map());

  const addEventHandler = useCallback((event: string, handler: (data: unknown) => void) => {
    const handlers = eventHandlers.current.get(event) ?? [];
    handlers.push(handler);
    eventHandlers.current.set(event, handlers);

    // Return cleanup function
    return () => {
      const updatedHandlers = eventHandlers.current.get(event) ?? [];
      const index = updatedHandlers.indexOf(handler);
      if (index > -1) {
        updatedHandlers.splice(index, 1);
        eventHandlers.current.set(event, updatedHandlers);
      }
    };
  }, []);

  const emitEvent = useCallback((event: string, data: unknown) => {
    const handlers = eventHandlers.current.get(event) ?? [];
    handlers.forEach(handler => {
      try {
        handler(data);
      } catch (error) {
        console.error(`Error in WebSocket event handler for ${event}:`, error);
      }
    });
  }, []);

  const buildWebSocketUrl = useCallback(() => {
    const baseUrl = url.replace('http://', 'ws://').replace('https://', 'wss://');
    const params = new URLSearchParams({
      client_id: clientId,
      room_id: roomId,
    });
    return `${baseUrl}?${params.toString()}`;
  }, [url, clientId, roomId]);

  const startHeartbeat = useCallback(() => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
    }

    heartbeatRef.current = setInterval(() => {
      if (wsRef.current?.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'heartbeat',
          timestamp: new Date().toISOString(),
        }));
      }
    }, heartbeatInterval);
  }, [heartbeatInterval]);

  const stopHeartbeat = useCallback(() => {
    if (heartbeatRef.current) {
      clearInterval(heartbeatRef.current);
      heartbeatRef.current = null;
    }
  }, []);

  const sendQueuedMessages = useCallback(() => {
    while (messageQueue.current.length > 0 && wsRef.current?.readyState === WebSocket.OPEN) {
      const message = messageQueue.current.shift();
      if (message) {
        wsRef.current.send(JSON.stringify(message));
      }
    }
  }, []);

  const scheduleReconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }

    setState(prev => ({
      ...prev,
      reconnectAttempts: prev.reconnectAttempts + 1,
    }));

    console.log(`Scheduling reconnect attempt ${state.reconnectAttempts + 1}/${maxReconnectAttempts}`);
    emitEvent('reconnecting', { attempt: state.reconnectAttempts + 1, maxAttempts: maxReconnectAttempts });

    reconnectTimeoutRef.current = setTimeout(() => {
      connect();
    }, reconnectInterval);
  }, [reconnectInterval, maxReconnectAttempts, state.reconnectAttempts, emitEvent]);

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.CONNECTING || wsRef.current?.readyState === WebSocket.OPEN) {
      return;
    }

    setState(prev => ({ ...prev, isConnecting: true, error: undefined }));

    try {
      const wsUrl = buildWebSocketUrl();
      wsRef.current = new WebSocket(wsUrl);

      wsRef.current.onopen = () => {
        console.log('WebSocket connected');
        setState(prev => ({
          ...prev,
          isConnected: true,
          isConnecting: false,
          reconnectAttempts: 0,
          error: undefined,
        }));

        startHeartbeat();
        sendQueuedMessages();
        emitEvent('connected', { clientId, roomId });
      };

      wsRef.current.onmessage = (event) => {
        try {
          const message: WebSocketMessage = JSON.parse(event.data);
          
          setState(prev => ({ ...prev, lastMessage: message }));
          setMessages(prev => [...prev, message]);

          // Handle special message types
          switch (message.type) {
            case 'progress_update':
              setProgress(message.data as ProgressData);
              emitEvent('progress', message.data);
              break;
            case 'research_result':
              emitEvent('result', message.data);
              break;
            case 'chat_message':
              emitEvent('chat', message.data);
              break;
            case 'heartbeat_response':
              emitEvent('heartbeat', message.data);
              break;
            case 'user_joined':
            case 'user_left':
              emitEvent('room_update', message.data);
              break;
            case 'error':
              emitEvent('error', message.data);
              break;
            default:
              emitEvent('message', message);
          }

          emitEvent(message.type, message.data);
        } catch (error) {
          console.error('Failed to parse WebSocket message:', error);
        }
      };

      wsRef.current.onclose = (event) => {
        console.log('WebSocket disconnected:', event.code, event.reason);
        setState(prev => ({
          ...prev,
          isConnected: false,
          isConnecting: false,
        }));

        stopHeartbeat();
        emitEvent('disconnected', { code: event.code, reason: event.reason });

        // Auto-reconnect if not manually closed
        if (event.code !== 1000 && state.reconnectAttempts < maxReconnectAttempts) {
          scheduleReconnect();
        }
      };

      wsRef.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setState(prev => ({
          ...prev,
          error: new Error('WebSocket connection error'),
          isConnecting: false,
        }));
        emitEvent('error', error);
      };

    } catch (error) {
      console.error('Failed to create WebSocket connection:', error);
      setState(prev => ({
        ...prev,
        error: error as Error,
        isConnecting: false,
      }));
    }
  }, [buildWebSocketUrl, startHeartbeat, sendQueuedMessages, emitEvent, state.reconnectAttempts, maxReconnectAttempts, clientId, roomId, scheduleReconnect, stopHeartbeat]);

  const disconnect = useCallback(() => {
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
      reconnectTimeoutRef.current = null;
    }

    stopHeartbeat();

    if (wsRef.current) {
      wsRef.current.close(1000, 'Manual disconnect');
      wsRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isConnected: false,
      isConnecting: false,
      reconnectAttempts: 0,
    }));
  }, [stopHeartbeat]);

  const sendMessage = useCallback((message: Omit<WebSocketMessage, 'client_id' | 'room_id' | 'timestamp'>) => {
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
      messageQueue.current.push(fullMessage);
      console.warn('WebSocket not connected, message queued');
      return false;
    }
  }, [clientId, roomId]);

  // Convenience methods
  const sendChatMessage = useCallback((content: string) => {
    return sendMessage({ type: 'chat_message', data: { content } });
  }, [sendMessage]);

  const sendResearchRequest = useCallback((query: string, requestId?: string) => {
    return sendMessage({
      type: 'research_request',
      data: {
        query,
        request_id: requestId ?? `req_${Date.now()}`,
      },
    });
  }, [sendMessage]);

  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    return sendMessage({
      type: 'typing_indicator',
      data: { is_typing: isTyping },
    });
  }, [sendMessage]);

  const requestRoomInfo = useCallback(() => {
    return sendMessage({ type: 'room_info_request' });
  }, [sendMessage]);

  // Effects
  useEffect(() => {
    if (autoConnect) {
      connect();
    }

    return () => {
      disconnect();
    };
  }, [autoConnect, connect, disconnect]);

  return {
    // State
    ...state,
    messages,
    progress,
    
    // Methods
    connect,
    disconnect,
    sendMessage,
    sendChatMessage,
    sendResearchRequest,
    sendTypingIndicator,
    requestRoomInfo,
    
    // Event handling
    on: addEventHandler,
    
    // Utility
    clearMessages: () => setMessages([]),
    clearProgress: () => setProgress(null),
  };
}
