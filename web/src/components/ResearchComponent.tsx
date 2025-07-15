/**
 * Research Component with WebSocket streaming
 */

'use client';

import React, { useState, useEffect, useRef } from 'react';
import { Search, Download, RefreshCw, Zap } from 'lucide-react';

import { useWebSocketContext } from '../contexts/WebSocketContext';
import type { ProgressUpdate, ResearchResult } from '../hooks/useWebSocket';
import { useProgressBar } from '../hooks/useProgressBar';
import styles from './ResearchComponent.module.css';

export interface ResearchComponentProps {
  className?: string;
}

export function ResearchComponent({ className = '' }: ResearchComponentProps) {
  const {
    isConnected,
    progress,
    messages,
    sendResearchRequest,
  } = useWebSocketContext();

  const progressBarRef = useProgressBar(progress?.progress || 0);

  const [query, setQuery] = useState('');
  const [isResearching, setIsResearching] = useState(false);
  const [currentRequestId, setCurrentRequestId] = useState<string | null>(null);
  const [researchResults, setResearchResults] = useState<ResearchResult[]>([]);
  const [finalReport, setFinalReport] = useState<string>('');
  
  const resultsRef = useRef<HTMLDivElement>(null);

  // Listen for research results
  useEffect(() => {
    const researchMessages = messages.filter(msg => 
      msg.type === 'research_result' && 
      'request_id' in msg &&
      msg.request_id === currentRequestId
    ).map(msg => ({
      ...msg,
      request_id: msg.request_id || '',
      section: msg.section || '',
      is_final: msg.is_final || false,
      content: msg.content || '',
      timestamp: msg.timestamp || ''
    })) as ResearchResult[];

    setResearchResults(researchMessages);

    // Find final report
    const finalResult = researchMessages.find(msg => msg.is_final);
    if (finalResult) {
      setFinalReport(finalResult.content);
      setIsResearching(false);
    }
  }, [messages, currentRequestId]);

  // Auto-scroll results
  useEffect(() => {
    if (resultsRef.current) {
      resultsRef.current.scrollTop = resultsRef.current.scrollHeight;
    }
  }, [researchResults]);

  const handleStartResearch = () => {
    if (!query.trim() || !isConnected || isResearching) return;

    const requestId = `research_${Date.now()}`;
    setCurrentRequestId(requestId);
    setIsResearching(true);
    setResearchResults([]);
    setFinalReport('');

    sendResearchRequest(query.trim(), requestId);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleStartResearch();
    }
  };

  const handleDownloadReport = () => {
    if (!finalReport) return;

    const blob = new Blob([finalReport], { type: 'text/markdown' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `research-report-${query.replace(/[^a-zA-Z0-9]/g, '-')}.md`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const resetResearch = () => {
    setIsResearching(false);
    setCurrentRequestId(null);
    setResearchResults([]);
    setFinalReport('');
    setQuery('');
  };

  return (
    <div className={`flex flex-col h-full bg-white rounded-lg shadow-lg ${className}`}>
      {/* Header */}
      <div className="p-4 border-b border-gray-200">
        <div className="flex items-center space-x-2 mb-4">
          <Search className="w-5 h-5 text-blue-500" />
          <h2 className="text-lg font-semibold text-gray-900">AI Research</h2>
          {isConnected ? (
            <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">Connected</span>
          ) : (
            <span className="text-xs bg-red-100 text-red-700 px-2 py-1 rounded">Disconnected</span>
          )}
        </div>

        {/* Search Input */}
        <div className="space-y-3">
          <div className="flex space-x-2">
            <input
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Enter your research query..."
              disabled={!isConnected || isResearching}
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500 disabled:bg-gray-100"
            />
            <button
              onClick={handleStartResearch}
              disabled={!isConnected || !query.trim() || isResearching}
              className="px-6 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 disabled:bg-gray-300 disabled:cursor-not-allowed flex items-center space-x-2"
              title={isResearching ? "Research in progress" : "Start research query"}
            >
              {isResearching ? (
                <>
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Researching...</span>
                </>
              ) : (
                <>
                  <Zap className="w-4 h-4" />
                  <span>Start Research</span>
                </>
              )}
            </button>
          </div>

          {/* Progress Bar */}
          {isResearching && progress && (
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-gray-600">{progress.stage}: {progress.message}</span>
                <span className="text-gray-500">{progress.progress}%</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  ref={progressBarRef}
                  className={`bg-blue-500 h-2 rounded-full ${styles['progress-bar-fill']}`}
                />
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex space-x-2">
            <button
              onClick={resetResearch}
              className="px-3 py-1 text-sm bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
              title="Reset research and clear results"
            >
              Reset
            </button>
            {finalReport && (
              <button
                onClick={handleDownloadReport}
                className="px-3 py-1 text-sm bg-green-100 text-green-600 rounded hover:bg-green-200 flex items-center space-x-1"
                title="Download research report as text file"
              >
                <Download className="w-3 h-3" />
                <span>Download Report</span>
              </button>
            )}
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="flex-1 overflow-hidden flex flex-col">
        {researchResults.length === 0 && !isResearching ? (
          <div className="flex-1 flex items-center justify-center text-gray-500">
            <div className="text-center">
              <Search className="w-12 h-12 mx-auto text-gray-300 mb-4" />
              <p>Enter a query to start researching</p>
              <p className="text-sm mt-2">AI will gather information and create a comprehensive report</p>
            </div>
          </div>
        ) : (
          <div className="flex-1 overflow-y-auto p-4 space-y-4" ref={resultsRef}>
            {/* Streaming Results */}
            {researchResults.map((result, index) => (
              <div key={index} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-2">
                  <h3 className="font-medium text-gray-900">
                    {result.section || `Section ${index + 1}`}
                  </h3>
                  <div className="flex items-center space-x-2">
                    {result.is_final && (
                      <span className="text-xs bg-green-100 text-green-700 px-2 py-1 rounded">
                        Final Report
                      </span>
                    )}
                    <span className="text-xs text-gray-500">
                      {new Date(result.timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
                <div className="prose prose-sm max-w-none">
                  <div className="whitespace-pre-wrap text-gray-700">
                    {result.content}
                  </div>
                </div>
              </div>
            ))}

            {/* Loading Indicator */}
            {isResearching && (
              <div className="flex items-center justify-center py-8">
                <div className="flex items-center space-x-2 text-gray-500">
                  <RefreshCw className="w-4 h-4 animate-spin" />
                  <span>Generating research report...</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Final Report Preview */}
      {finalReport && (
        <div className="border-t border-gray-200 p-4 bg-gray-50">
          <div className="flex items-center justify-between mb-2">
            <h3 className="font-medium text-gray-900">Final Report Ready</h3>
            <button
              onClick={handleDownloadReport}
              className="text-sm bg-blue-500 text-white px-3 py-1 rounded hover:bg-blue-600 flex items-center space-x-1"
              title="Download final research report"
            >
              <Download className="w-3 h-3" />
              <span>Download</span>
            </button>
          </div>
          <p className="text-sm text-gray-600">
            Research completed! {finalReport.length} characters generated.
          </p>
        </div>
      )}
    </div>
  );
}
