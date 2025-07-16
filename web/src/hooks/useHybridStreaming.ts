// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { useCallback, useEffect, useRef, useState } from 'react';

import { chatStream } from '~/core/api/chat';
import type { ChatEvent } from '~/core/api/types';

import { useWebSocket, type ProgressData, type WebSocketMessage } from './useWebSocket';

export interface HybridStreamingOptions {
  enableWebSocket?: boolean;
  enableSSE?: boolean;
  websocketUrl?: string;
  clientId?: string;
  roomId?: string;
  fallbackToSSE?: boolean;
}

export interface StreamingState {
  isStreaming: boolean;
  streamingMethod: 'websocket' | 'sse' | 'none';
  progress: ProgressData | null;
  error: string | null;
  messages: (WebSocketMessage | ChatEvent)[];
}

/**
 * Hybrid streaming hook that combines WebSocket real-time features with SSE streaming
 * - Uses WebSocket for real-time collaboration, progress updates, and notifications
 * - Uses SSE for main research streaming (existing functionality)
 * - Automatically falls back to SSE if WebSocket fails
 */
export function useHybridStreaming(options: HybridStreamingOptions = {}) {
  const {
    enableWebSocket = true,
    enableSSE = true,
    websocketUrl = 'ws://localhost:8000/ws',
    clientId = `client_${Date.now()}`,
    roomId = 'default',
    fallbackToSSE = true,
  } = options;

  const [state, setState] = useState<StreamingState>({
    isStreaming: false,
    streamingMethod: 'none',
    progress: null,
    error: null,
    messages: [],
  });

  const abortControllerRef = useRef<AbortController | null>(null);
  const sseStreamRef = useRef<AsyncIterable<ChatEvent> | null>(null);

  // WebSocket integration
  const webSocket = useWebSocket(
    websocketUrl,
    clientId,
    roomId,
    { 
      autoConnect: enableWebSocket,
      reconnectInterval: 2000,
      maxReconnectAttempts: 3,
    }
  );

  // Handle WebSocket events
  useEffect(() => {
    if (!enableWebSocket) return;

    const handleProgress = (data: unknown) => {
      setState(prev => ({
        ...prev,
        progress: data as ProgressData,
      }));
    };

    const handleResult = (data: unknown) => {
      setState(prev => ({
        ...prev,
        messages: [...prev.messages, {
          type: 'research_result',
          data,
          timestamp: new Date().toISOString(),
        }],
      }));
    };

    const handleError = (data: unknown) => {
      setState(prev => ({
        ...prev,
        error: typeof data === 'string' ? data : 'WebSocket error occurred',
      }));
    };

    const handleConnected = () => {
      setState(prev => ({
        ...prev,
        streamingMethod: 'websocket',
        error: null,
      }));
    };

    const handleDisconnected = () => {
      if (fallbackToSSE && enableSSE) {
        setState(prev => ({
          ...prev,
          streamingMethod: 'sse',
          error: null,
        }));
      }
    };

    // Register event handlers
    const cleanupProgress = webSocket.on('progress', handleProgress);
    const cleanupResult = webSocket.on('result', handleResult);
    const cleanupError = webSocket.on('error', handleError);
    const cleanupConnected = webSocket.on('connected', handleConnected);
    const cleanupDisconnected = webSocket.on('disconnected', handleDisconnected);

    return () => {
      cleanupProgress();
      cleanupResult();
      cleanupError();
      cleanupConnected();
      cleanupDisconnected();
    };
  }, [enableWebSocket, webSocket, fallbackToSSE, enableSSE]);

  // Sync WebSocket state
  useEffect(() => {
    setState(prev => ({
      ...prev,
      progress: webSocket.progress,
    }));
  }, [webSocket.progress]);

  // Main streaming function for research
  const startResearchStream = useCallback(async (
    query: string,
    params: {
      thread_id: string;
      auto_accepted_plan?: boolean;
      max_plan_iterations?: number;
      max_step_num?: number;
      max_search_results?: number;
      interrupt_feedback?: string;
      enable_deep_thinking?: boolean;
      enable_background_investigation?: boolean;
      report_style?: "academic" | "popular_science" | "news" | "social_media";
    }
  ) => {
    // Stop any existing stream
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    setState(prev => ({
      ...prev,
      isStreaming: true,
      error: null,
      messages: [],
    }));

    try {
      // Send research request via WebSocket if connected
      if (webSocket.isConnected && enableWebSocket) {
        const requestId = `req_${Date.now()}`;
        webSocket.sendResearchRequest(query, requestId);
        
        setState(prev => ({
          ...prev,
          streamingMethod: 'websocket',
        }));
        
        // WebSocket will handle progress updates and results
        return;
      }

      // Fallback to SSE streaming
      if (enableSSE) {
        setState(prev => ({
          ...prev,
          streamingMethod: 'sse',
        }));

        abortControllerRef.current = new AbortController();
        
        const stream = chatStream(query, {
          thread_id: params.thread_id,
          resources: [],
          auto_accepted_plan: params.auto_accepted_plan ?? false,
          max_plan_iterations: params.max_plan_iterations ?? 3,
          max_step_num: params.max_step_num ?? 5,
          max_search_results: params.max_search_results,
          interrupt_feedback: params.interrupt_feedback,
          enable_deep_thinking: params.enable_deep_thinking,
          enable_background_investigation: params.enable_background_investigation ?? true,
          report_style: params.report_style,
        }, {
          abortSignal: abortControllerRef.current.signal,
        });

        sseStreamRef.current = stream;

        // Process SSE stream
        for await (const event of stream) {
          setState(prev => ({
            ...prev,
            messages: [...prev.messages, event],
          }));

          // Extract progress information from SSE if available
          if (event.type === 'message_chunk' && event.data?.content) {
            // You can parse content for progress indicators here
            // This is where you'd extract stage information from the streaming content
          }
        }
      }

    } catch (error) {
      if (error instanceof Error && error.name !== 'AbortError') {
        setState(prev => ({
          ...prev,
          error: error.message,
          isStreaming: false,
        }));
      }
    } finally {
      setState(prev => ({
        ...prev,
        isStreaming: false,
      }));
    }
  }, [webSocket, enableWebSocket, enableSSE]);

  // Stop streaming
  const stopStreaming = useCallback(() => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
      abortControllerRef.current = null;
    }

    setState(prev => ({
      ...prev,
      isStreaming: false,
    }));
  }, []);

  // Send chat message (WebSocket only)
  const sendChatMessage = useCallback((content: string) => {
    if (webSocket.isConnected && enableWebSocket) {
      return webSocket.sendChatMessage(content);
    }
    return false;
  }, [webSocket, enableWebSocket]);

  // Send typing indicator (WebSocket only)
  const sendTypingIndicator = useCallback((isTyping: boolean) => {
    if (webSocket.isConnected && enableWebSocket) {
      return webSocket.sendTypingIndicator(isTyping);
    }
    return false;
  }, [webSocket, enableWebSocket]);

  // Get room information (WebSocket only)
  const getRoomInfo = useCallback(() => {
    if (webSocket.isConnected && enableWebSocket) {
      return webSocket.requestRoomInfo();
    }
    return false;
  }, [webSocket, enableWebSocket]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, []);

  return {
    // State
    ...state,
    
    // WebSocket state
    isWebSocketConnected: webSocket.isConnected,
    isWebSocketConnecting: webSocket.isConnecting,
    websocketMessages: webSocket.messages,
    reconnectAttempts: webSocket.reconnectAttempts,
    
    // Methods
    startResearchStream,
    stopStreaming,
    sendChatMessage,
    sendTypingIndicator,
    getRoomInfo,
    
    // WebSocket methods
    connectWebSocket: webSocket.connect,
    disconnectWebSocket: webSocket.disconnect,
    
    // Utility
    clearMessages: () => {
      setState(prev => ({ ...prev, messages: [] }));
      webSocket.clearMessages();
    },
    clearProgress: () => {
      setState(prev => ({ ...prev, progress: null }));
      webSocket.clearProgress();
    },
    
    // Event handling
    onWebSocketEvent: webSocket.on,
  };
}
