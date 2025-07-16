// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

'use client';

import { useState } from 'react';
import { Button } from '~/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '~/components/ui/card';
import { Input } from '~/components/ui/input';
import { Badge } from '~/components/ui/badge';
import { useHybridStreaming } from '~/hooks/useHybridStreaming';

export function WebSocketDemo() {
  const [query, setQuery] = useState('');
  const [threadId] = useState(`thread_${Date.now()}`);

  const {
    isStreaming,
    streamingMethod,
    progress,
    error,
    messages,
    isWebSocketConnected,
    isWebSocketConnecting,
    websocketMessages,
    reconnectAttempts,
    startResearchStream,
    stopStreaming,
    sendChatMessage,
    sendTypingIndicator,
    getRoomInfo,
    connectWebSocket,
    disconnectWebSocket,
    clearMessages,
    onWebSocketEvent,
  } = useHybridStreaming({
    enableWebSocket: true,
    enableSSE: true,
    websocketUrl: 'ws://localhost:8000/ws',
    clientId: `demo_client_${Date.now()}`,
    roomId: 'demo-room',
    fallbackToSSE: true,
  });

  const handleStartResearch = () => {
    if (!query.trim()) return;

    startResearchStream(query, {
      thread_id: threadId,
      auto_accepted_plan: true,
      max_plan_iterations: 3,
      max_step_num: 5,
      max_search_results: 10,
      enable_deep_thinking: false,
      enable_background_investigation: true,
      report_style: 'academic',
    });
  };

  const handleSendChat = () => {
    if (!query.trim()) return;
    sendChatMessage(query);
    setQuery('');
  };

  const getConnectionStatus = () => {
    if (isWebSocketConnecting) return { status: 'Connecting...', variant: 'secondary' as const };
    if (isWebSocketConnected) return { status: 'Connected', variant: 'default' as const };
    if (reconnectAttempts > 0) return { status: `Reconnecting (${reconnectAttempts})`, variant: 'destructive' as const };
    return { status: 'Disconnected', variant: 'destructive' as const };
  };

  const connectionStatus = getConnectionStatus();

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      <div className="flex items-center justify-between">
        <h1 className="text-2xl font-bold">WebSocket Streaming Demo</h1>
        <Badge variant={connectionStatus.variant}>
          {connectionStatus.status}
        </Badge>
      </div>

      {/* Connection Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Connection</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Button 
              onClick={connectWebSocket}
              disabled={isWebSocketConnected || isWebSocketConnecting}
              variant="outline"
            >
              Connect WebSocket
            </Button>
            <Button 
              onClick={disconnectWebSocket}
              disabled={!isWebSocketConnected}
              variant="outline"
            >
              Disconnect
            </Button>
            <Button 
              onClick={getRoomInfo}
              disabled={!isWebSocketConnected}
              variant="outline"
            >
              Get Room Info
            </Button>
          </div>
          
          <div className="text-sm text-muted-foreground">
            Streaming Method: <Badge variant="outline">{streamingMethod}</Badge>
            {reconnectAttempts > 0 && (
              <span className="ml-2">Reconnect Attempts: {reconnectAttempts}</span>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Research Controls */}
      <Card>
        <CardHeader>
          <CardTitle>Research Streaming</CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex gap-2">
            <Input
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter research query or chat message..."
              onKeyPress={(e) => e.key === 'Enter' && handleStartResearch()}
            />
            <Button 
              onClick={handleStartResearch}
              disabled={isStreaming || !query.trim()}
            >
              Start Research
            </Button>
            <Button 
              onClick={handleSendChat}
              disabled={!isWebSocketConnected || !query.trim()}
              variant="outline"
            >
              Send Chat
            </Button>
          </div>
          
          {isStreaming && (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-sm">Streaming in progress...</span>
                <Button 
                  onClick={stopStreaming}
                  variant="outline"
                  size="sm"
                >
                  Stop
                </Button>
              </div>
              {progress && (
                <div className="space-y-1">
                  <div className="flex justify-between text-xs">
                    <span>{progress.stage}</span>
                    <span>{progress.progress}%</span>
                  </div>
                  <div className="w-full bg-secondary rounded-full h-2">
                    <div 
                      className="bg-primary h-2 rounded-full transition-all duration-300"
                      style={{ width: `${progress.progress}%` }}
                    />
                  </div>
                  <p className="text-xs text-muted-foreground">{progress.message}</p>
                </div>
              )}
            </div>
          )}
          
          {error && (
            <div className="p-3 bg-destructive/10 border border-destructive rounded-md">
              <p className="text-sm text-destructive">{error}</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* WebSocket Messages */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            WebSocket Messages ({websocketMessages.length})
            <Button 
              onClick={clearMessages}
              variant="outline"
              size="sm"
            >
              Clear
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {websocketMessages.length === 0 ? (
              <p className="text-sm text-muted-foreground">No WebSocket messages yet</p>
            ) : (
              websocketMessages.map((message, index) => (
                <div 
                  key={index}
                  className="p-2 bg-secondary/50 rounded text-xs font-mono"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline" className="text-xs">
                      {message.type}
                    </Badge>
                    <span className="text-muted-foreground">
                      {message.timestamp}
                    </span>
                  </div>
                  <pre className="whitespace-pre-wrap">
                    {JSON.stringify(message.data, null, 2)}
                  </pre>
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Research Results */}
      <Card>
        <CardHeader>
          <CardTitle>Research Results ({messages.length})</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {messages.length === 0 ? (
              <p className="text-sm text-muted-foreground">No research results yet</p>
            ) : (
              messages.map((message, index) => (
                <div 
                  key={index}
                  className="p-2 bg-secondary/50 rounded text-xs"
                >
                  <div className="flex items-center gap-2 mb-1">
                    <Badge variant="outline" className="text-xs">
                      {message.type}
                    </Badge>
                    <span className="text-muted-foreground">
                      {('timestamp' in message && message.timestamp) ? message.timestamp : 'No timestamp'}
                    </span>
                  </div>
                  
                  {'data' in message && message.data !== undefined && (
                    <div className="text-sm">
                      {typeof message.data === 'object' && message.data !== null ? (
                        <pre className="whitespace-pre-wrap">
                          {JSON.stringify(message.data, null, 2)}
                        </pre>
                      ) : (
                        <p>{String(message.data ?? '')}</p>
                      )}
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </CardContent>
      </Card>

      {/* Instructions */}
      <Card>
        <CardHeader>
          <CardTitle>How to Test</CardTitle>
        </CardHeader>
        <CardContent className="text-sm space-y-2">
          <ol className="list-decimal list-inside space-y-1">
            <li>Make sure the backend server is running with WebSocket support</li>
            <li>Click "Connect WebSocket" to establish connection</li>
            <li>Enter a research query and click "Start Research" to test streaming</li>
            <li>Use "Send Chat" to send real-time chat messages</li>
            <li>Open multiple browser tabs to test multi-user functionality</li>
            <li>Try disconnecting and reconnecting to test auto-reconnect</li>
          </ol>
          
          <div className="mt-4 p-3 bg-blue-50 rounded-md">
            <p className="font-medium">Features being tested:</p>
            <ul className="list-disc list-inside mt-1 space-y-1">
              <li>WebSocket connection with auto-reconnect</li>
              <li>Real-time progress updates during research</li>
              <li>Bi-directional communication (chat)</li>
              <li>Fallback to SSE when WebSocket fails</li>
              <li>Message queuing during disconnection</li>
              <li>Room-based communication</li>
            </ul>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
