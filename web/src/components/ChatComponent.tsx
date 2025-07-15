/**
 * Chat Component with WebSocket integration
 */

'use client';

import React, { useEffect, useRef, useState } from 'react';
import { Send, Users, Wifi, WifiOff } from 'lucide-react';

import { useWebSocketContext } from '../contexts/WebSocketContext';
import type { WebSocketMessage } from '../hooks/useWebSocket';
import styles from './ChatComponent.module.css';
import { useProgressBar } from '../hooks/useProgressBar';

export interface ChatComponentProps {
  className?: string;
}

export function ChatComponent({ className = '' }: ChatComponentProps) {
  const {
    isConnected,
    isConnecting,
    isReconnecting,
    messages,
    sendChatMessage,
    clearMessages,
    roomId,
    setRoomId,
  } = useWebSocketContext();

  const [inputMessage, setInputMessage] = useState('');
  const [newRoomId, setNewRoomId] = useState(roomId);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = () => {
    if (inputMessage.trim() && isConnected) {
      sendChatMessage(inputMessage.trim());
      setInputMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const handleRoomChange = () => {
    if (newRoomId.trim() && newRoomId !== roomId) {
      setRoomId(newRoomId.trim());
    }
  };

  const getConnectionStatus = () => {
    if (isConnecting) return { text: 'Connecting...', icon: WifiOff, color: 'text-yellow-500' };
    if (isReconnecting) return { text: 'Reconnecting...', icon: WifiOff, color: 'text-yellow-500' };
    if (isConnected) return { text: 'Connected', icon: Wifi, color: 'text-green-500' };
    return { text: 'Disconnected', icon: WifiOff, color: 'text-red-500' };
  };

  const status = getConnectionStatus();
  const StatusIcon = status.icon;

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2">
          <Users className="w-5 h-5 text-gray-500" />
          <span className="font-medium text-gray-900">Room: {roomId}</span>
        </div>
        <div className={`flex items-center space-x-2 ${status.color}`}>
          <StatusIcon className="w-4 h-4" />
          <span className="text-sm">{status.text}</span>
        </div>
      </div>

      {/* Room switcher */}
      <div className="flex items-center space-x-2 p-3 border-b border-gray-100">
        <input
          type="text"
          value={newRoomId}
          onChange={(e) => setNewRoomId(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleRoomChange()}
          placeholder="Enter room ID"
          className="flex-1 px-3 py-1 text-sm border border-gray-300 rounded focus:outline-none focus:border-blue-500"
        />
        <button
          onClick={handleRoomChange}
          disabled={!newRoomId.trim() || newRoomId === roomId}
          className="px-3 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
          title="Switch to different room"
        >
          Switch
        </button>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-3">
        {messages.length === 0 ? (
          <div className="text-center text-gray-500 py-8">
            No messages yet. Start a conversation!
          </div>
        ) : (
          messages.map((message, index) => (
            <MessageItem key={index} message={message} />
          ))
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="p-4 border-t border-gray-200">
        <div className="flex space-x-2">
          <div className="flex space-x-1 mb-2">
            <button
              onClick={clearMessages}
              className="px-2 py-1 text-xs bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
              title="Clear all messages"
            >
              Clear
            </button>
          </div>
        </div>
        <div className="flex space-x-2">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Type a message..." : "Connecting..."}
            disabled={!isConnected}
            className="flex-1 px-3 py-2 border border-gray-300 rounded-lg resize-none focus:outline-none focus:border-blue-500 disabled:bg-gray-100"
            rows={1}
          />
          <button
            onClick={handleSendMessage}
            disabled={!isConnected || !inputMessage.trim()}
            className="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed"
            title="Send message"
          >
            <Send className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
}

interface MessageItemProps {
  message: WebSocketMessage;
}

function ProgressBar({ progress }: { progress: number }) {
  const progressRef = useProgressBar(progress);
  
  return (
    <div className="flex-1 bg-gray-200 rounded-full h-2">
      <div 
        ref={progressRef}
        className={`bg-yellow-500 h-2 rounded-full ${styles['progress-bar-fill']}`}
      />
    </div>
  );
}

function MessageItem({ message }: MessageItemProps) {
  const formatTime = (timestamp?: string) => {
    if (!timestamp) return '';
    try {
      return new Date(timestamp).toLocaleTimeString();
    } catch {
      return '';
    }
  };

  const getMessageColor = (type: string) => {
    switch (type) {
      case 'chat_message': return 'bg-blue-50 border-blue-200';
      case 'research_request': return 'bg-green-50 border-green-200';
      case 'progress_update': return 'bg-yellow-50 border-yellow-200';
      case 'research_result': return 'bg-purple-50 border-purple-200';
      case 'user_joined': return 'bg-green-50 border-green-200';
      case 'user_left': return 'bg-red-50 border-red-200';
      default: return 'bg-gray-50 border-gray-200';
    }
  };

  const renderMessageContent = () => {
    switch (message.type) {
      case 'chat_message':
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-900">
                {message.client_id === 'You' ? 'You' : message.client_id}
              </span>
              <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
            </div>
            <p className="text-gray-700">{message.content}</p>
          </div>
        );

      case 'research_request':
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-green-700">Research Request</span>
              <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
            </div>
            <p className="text-gray-700">Query: {message.query}</p>
            {message.request_id && (
              <p className="text-xs text-gray-500 mt-1">ID: {message.request_id}</p>
            )}
          </div>
        );

      case 'progress_update':
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-yellow-700">Progress Update</span>
              <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
            </div>
            <div className="space-y-1">
              <p className="text-gray-700">{message.message}</p>
              <div className="flex items-center space-x-2">
                <span className="text-xs text-gray-500">{message.stage}</span>
                <ProgressBar progress={message.progress || 0} />
                <span className="text-xs text-gray-500">{message.progress || 0}%</span>
              </div>
            </div>
          </div>
        );

      case 'research_result':
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-purple-700">
                Research Result {message.section && `- ${message.section}`}
              </span>
              <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
            </div>
            <div className="text-gray-700 whitespace-pre-wrap">{message.content}</div>
            {message.is_final && (
              <div className="mt-2 px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">
                Final Result
              </div>
            )}
          </div>
        );

      case 'user_joined':
      case 'user_left':
        return (
          <div className="text-center">
            <span className="text-sm text-gray-600">
              {message.client_id} {message.type === 'user_joined' ? 'joined' : 'left'} the room
            </span>
            <span className="text-xs text-gray-500 ml-2">
              {formatTime(message.timestamp)}
            </span>
          </div>
        );

      default:
        return (
          <div>
            <div className="flex items-center justify-between mb-1">
              <span className="text-sm font-medium text-gray-700">{message.type}</span>
              <span className="text-xs text-gray-500">{formatTime(message.timestamp)}</span>
            </div>
            <pre className="text-xs text-gray-600 whitespace-pre-wrap">
              {JSON.stringify(message, null, 2)}
            </pre>
          </div>
        );
    }
  };

  return (
    <div className={`p-3 rounded-lg border ${getMessageColor(message.type)}`}>
      {renderMessageContent()}
    </div>
  );
}
