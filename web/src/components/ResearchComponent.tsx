// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useTranslations } from "next-intl";
import { useCallback, useEffect, useState } from "react";

import { LoadingAnimation } from "~/components/deer-flow/loading-animation";
import { Card } from "~/components/ui/card";
import { useHybridStreaming } from "~/hooks/useHybridStreaming";
import { cn } from "~/lib/utils";

import { ResearchBlock } from "~/app/chat/components/research-block";

export interface ResearchComponentProps {
  className?: string;
  researchId: string | null;
  enableWebSocket?: boolean;
  enableRealTimeProgress?: boolean;
  onProgressUpdate?: (progress: any) => void;
  onError?: (error: Error) => void;
}

export function ResearchComponent({
  className,
  researchId,
  enableWebSocket = false,
  enableRealTimeProgress = true,
  onProgressUpdate,
  onError,
}: ResearchComponentProps) {
  const t = useTranslations("research");
  const [isInitializing, setIsInitializing] = useState(false);

  // Initialize hybrid streaming for research progress
  const {
    isWebSocketConnected,
    isWebSocketConnecting,
    streamingMethod,
    progress,
    error: streamingError,
    startResearchStream,
    stopStreaming,
    connectWebSocket,
    disconnectWebSocket,
  } = useHybridStreaming({
    enableWebSocket,
    enableSSE: true,
    fallbackToSSE: true,
    roomId: researchId || 'default',
  });

  // Handle progress updates
  useEffect(() => {
    if (progress && enableRealTimeProgress) {
      onProgressUpdate?.(progress);
    }
  }, [progress, enableRealTimeProgress, onProgressUpdate]);

  // Handle streaming errors
  useEffect(() => {
    if (streamingError) {
      onError?.(new Error(streamingError));
    }
  }, [streamingError, onError]);

  // Auto-connect when research starts
  useEffect(() => {
    if (researchId && enableWebSocket && !isWebSocketConnected && !isWebSocketConnecting) {
      setIsInitializing(true);
      connectWebSocket();
      setTimeout(() => setIsInitializing(false), 2000);
    }
  }, [researchId, enableWebSocket, isWebSocketConnected, isWebSocketConnecting, connectWebSocket]);

  // Cleanup on research end
  useEffect(() => {
    return () => {
      if (isWebSocketConnected) {
        stopStreaming();
      }
    };
  }, [isWebSocketConnected, stopStreaming]);

  const handleStartResearch = useCallback(async (
    query: string,
    params: {
      auto_accepted_plan?: boolean;
      max_plan_iterations?: number;
      max_step_num?: number;
      enable_deep_thinking?: boolean;
      enable_background_investigation?: boolean;
      report_style?: "academic" | "popular_science" | "news" | "social_media";
    }
  ) => {
    if (!researchId) return;

    try {
      await startResearchStream(query, {
        thread_id: researchId,
        ...params,
      });
    } catch (error) {
      console.error('Failed to start research stream:', error);
      onError?.(error as Error);
    }
  }, [researchId, startResearchStream, onError]);

  const handleStopResearch = useCallback(() => {
    stopStreaming();
  }, [stopStreaming]);

  return (
    <div className={cn("flex h-full w-full flex-col", className)}>
      {/* Real-time Status Indicator */}
      {enableWebSocket && enableRealTimeProgress && (
        <div className="flex items-center justify-between p-2 text-xs text-muted-foreground border-b">
          <div className="flex items-center gap-2">
            <div
              className={cn(
                "h-2 w-2 rounded-full",
                isWebSocketConnected
                  ? "bg-green-500"
                  : isInitializing || isWebSocketConnecting
                  ? "bg-yellow-500 animate-pulse"
                  : "bg-gray-400"
              )}
            />
            <span>
              {isWebSocketConnected
                ? `Real-time updates via ${streamingMethod.toUpperCase()}`
                : isInitializing || isWebSocketConnecting
                ? "Initializing real-time updates..."
                : "Real-time updates disabled"}
            </span>
          </div>
          
          {/* Progress Indicator */}
          {progress && (
            <div className="flex items-center gap-2">
              <span className="text-xs">
                {progress.stage && `Stage: ${progress.stage}`}
              </span>
              {progress.progress !== undefined && (
                <div className="w-16 h-1 bg-gray-200 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-500 transition-all duration-300"
                    style={{
                      width: `${Math.min(100, Math.max(0, progress.progress))}%`,
                    }}
                  />
                </div>
              )}
            </div>
          )}
          
          {streamingError && (
            <span className="text-red-500 text-xs">
              Error: {streamingError}
            </span>
          )}
        </div>
      )}

      {/* Main Research Interface */}
      <div className="flex-1 overflow-hidden">
        {researchId ? (
          <ResearchBlock
            className="h-full"
            researchId={researchId}
          />
        ) : (
          <Card className="flex h-full w-full items-center justify-center">
            <div className="text-center">
              <h3 className="text-lg font-medium text-muted-foreground">
                {t("noActiveResearch", { default: "No active research" })}
              </h3>
              <p className="text-sm text-muted-foreground mt-2">
                {t("startResearchPrompt", { default: "Start a new research to see progress here" })}
              </p>
            </div>
          </Card>
        )}
      </div>

      {/* Loading overlay for initialization */}
      {isInitializing && (
        <div className="absolute inset-0 flex items-center justify-center bg-background/50 backdrop-blur-sm">
          <div className="flex flex-col items-center gap-2">
            <LoadingAnimation />
            <span className="text-sm text-muted-foreground">
              Initializing real-time research updates...
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default ResearchComponent;