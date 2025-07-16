// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";

import { LoadingAnimation } from "~/components/deer-flow/loading-animation";
import { Card } from "~/components/ui/card";
import type { Option, Resource } from "~/core/messages";
import { sendMessage, useStore } from "~/core/store";
import { useHybridStreaming } from "~/hooks/useHybridStreaming";
import { cn } from "~/lib/utils";

import { InputBox } from "~/app/chat/components/input-box";
import { MessageListView } from "~/app/chat/components/message-list-view";

export interface ChatComponentProps {
  className?: string;
  enableWebSocket?: boolean;
  onConnectionChange?: (connected: boolean, method: 'websocket' | 'sse') => void;
  onError?: (error: Error) => void;
}

export function ChatComponent({
  className,
  enableWebSocket = false,
  onConnectionChange,
  onError,
}: ChatComponentProps) {
  const t = useTranslations("chat");
  const responding = useStore((state) => state.responding);
  const messageCount = useStore((state) => state.messageIds.length);
  
  const [feedback, setFeedback] = useState<{ option: Option } | null>(null);
  const [isConnecting, setIsConnecting] = useState(false);

  // Initialize hybrid streaming
  const {
    isWebSocketConnected,
    isWebSocketConnecting,
    streamingMethod,
    error: streamingError,
    connectWebSocket,
    disconnectWebSocket,
    sendChatMessage,
    startResearchStream,
    stopStreaming,
  } = useHybridStreaming({
    enableWebSocket,
    enableSSE: true,
    fallbackToSSE: true,
  });

  // Notify parent component about connection changes
  useEffect(() => {
    const method = streamingMethod === 'none' ? 'sse' : streamingMethod as 'websocket' | 'sse';
    onConnectionChange?.(isWebSocketConnected, method);
  }, [isWebSocketConnected, streamingMethod, onConnectionChange]);

  // Handle connection errors
  useEffect(() => {
    if (streamingError) {
      onError?.(new Error(streamingError));
    }
  }, [streamingError, onError]);

  const handleSend = useCallback(
    async (
      message: string,
      options?: {
        interruptFeedback?: string;
        resources?: Array<Resource>;
      }
    ) => {
      if (!message.trim()) return;

      setIsConnecting(true);
      try {
        if (enableWebSocket && isWebSocketConnected && streamingMethod === 'websocket') {
          // Use WebSocket for sending if available and connected
          await sendChatMessage(message);
        } else {
          // Fallback to traditional SSE-based sending
          await sendMessage(
            message,
            {
              interruptFeedback: options?.interruptFeedback ?? feedback?.option.value,
              resources: options?.resources,
            }
          );
        }
        
        // Clear feedback after successful send
        setFeedback(null);
      } catch (error) {
        console.error('Failed to send message:', error);
        onError?.(error as Error);
      } finally {
        setIsConnecting(false);
      }
    },
    [
      enableWebSocket,
      isWebSocketConnected,
      streamingMethod,
      sendChatMessage,
      feedback,
      onError,
    ]
  );

  const handleCancel = useCallback(() => {
    // Handle message cancellation
    if (responding) {
      // Cancel ongoing operation
      stopStreaming();
      disconnectWebSocket();
      // Reconnect after cancellation
      setTimeout(() => {
        if (enableWebSocket) {
          connectWebSocket();
        }
      }, 1000);
    }
  }, [responding, stopStreaming, disconnectWebSocket, connectWebSocket, enableWebSocket]);

  const handleFeedback = useCallback((feedback: { option: Option }) => {
    setFeedback(feedback);
  }, []);

  const handleRemoveFeedback = useCallback(() => {
    setFeedback(null);
  }, []);

  return (
    <div className={cn("flex h-full w-full flex-col", className)}>
      {/* Connection Status Indicator */}
      {enableWebSocket && (
        <div className="flex items-center justify-between p-2 text-xs text-muted-foreground">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "h-2 w-2 rounded-full",
                isWebSocketConnected
                  ? "bg-green-500"
                  : isConnecting
                  ? "bg-yellow-500"
                  : "bg-red-500"
              )}
            />
            <span>
              {isWebSocketConnected
                ? `Connected via ${streamingMethod.toUpperCase()}`
                : isConnecting
                ? "Connecting..."
                : "Disconnected"}
            </span>
          </div>
          {streamingError && (
            <span className="text-red-500">
              Error: {streamingError}
            </span>
          )}
        </div>
      )}

      {/* Main Chat Interface */}
      <Card className="flex h-full w-full flex-col overflow-hidden">
        {/* Message List */}
        <div className="flex-1 overflow-hidden">
          <MessageListView
            className="h-full"
            onFeedback={handleFeedback}
            onSendMessage={handleSend}
          />
        </div>

        {/* Input Area */}
        <div className="border-t p-4">
          <InputBox
            responding={responding || isConnecting}
            feedback={feedback}
            onSend={handleSend}
            onCancel={handleCancel}
            onRemoveFeedback={handleRemoveFeedback}
          />
        </div>
      </Card>

      {/* Loading State for Connection */}
      {isConnecting && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/50">
          <div className="flex flex-col items-center gap-2">
            <LoadingAnimation />
            <span className="text-sm text-muted-foreground">
              {enableWebSocket ? "Establishing connection..." : "Sending message..."}
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ChatComponent;