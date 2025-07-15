/**
 * WebSocket Test Page
 */

'use client';

import React from 'react';

import { ChatComponent } from '../../components/ChatComponent';
import { ResearchComponent } from '../../components/ResearchComponent';
import { WebSocketProvider } from '../../contexts/WebSocketContext';

export default function WebSocketTestPage() {
  return (
    <WebSocketProvider
      defaultRoomId="test-room"
      wsUrl="ws://localhost:8001/ws"
      autoConnect={true}
    >
      <div className="min-h-screen bg-gray-100 p-4">
        <div className="max-w-7xl mx-auto">
          <div className="mb-6">
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              WebSocket Streaming Test
            </h1>
            <p className="text-gray-600">
              Test real-time communication and research streaming with WebSocket
            </p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-200px)]">
            {/* Chat Component */}
            <div className="flex flex-col">
              <h2 className="text-xl font-semibold text-gray-800 mb-3">Real-time Chat</h2>
              <ChatComponent className="flex-1" />
            </div>

            {/* Research Component */}
            <div className="flex flex-col">
              <h2 className="text-xl font-semibold text-gray-800 mb-3">AI Research Streaming</h2>
              <ResearchComponent className="flex-1" />
            </div>
          </div>

          {/* Instructions */}
          <div className="mt-6 bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">How to Test</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h4 className="font-medium text-gray-800 mb-2">Chat Testing:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Open multiple browser tabs to simulate multiple users</li>
                  <li>• Switch between different rooms to test room isolation</li>
                  <li>• Watch real-time message synchronization</li>
                  <li>• Test connection resilience by refreshing pages</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-gray-800 mb-2">Research Testing:</h4>
                <ul className="text-sm text-gray-600 space-y-1">
                  <li>• Enter a research query like &ldquo;AI trends 2024&rdquo;</li>
                  <li>• Watch real-time progress updates</li>
                  <li>• See streaming research results as they generate</li>
                  <li>• Download final report when complete</li>
                </ul>
              </div>
            </div>
          </div>

          {/* Technical Info */}
          <div className="mt-6 bg-blue-50 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 mb-3">Technical Features</h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Real-time Features:</h4>
                <ul className="text-blue-700 space-y-1">
                  <li>• Bidirectional WebSocket communication</li>
                  <li>• Room-based message routing</li>
                  <li>• Automatic reconnection with exponential backoff</li>
                  <li>• Heartbeat mechanism for connection health</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Message Types:</h4>
                <ul className="text-blue-700 space-y-1">
                  <li>• chat_message - Real-time chat</li>
                  <li>• research_request - AI research queries</li>
                  <li>• progress_update - Research progress</li>
                  <li>• research_result - Streaming results</li>
                </ul>
              </div>
              <div>
                <h4 className="font-medium text-blue-800 mb-2">Quality Features:</h4>
                <ul className="text-blue-700 space-y-1">
                  <li>• Message queuing during disconnection</li>
                  <li>• Type-safe TypeScript implementation</li>
                  <li>• Error handling and recovery</li>
                  <li>• Performance optimized rendering</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </WebSocketProvider>
  );
}
