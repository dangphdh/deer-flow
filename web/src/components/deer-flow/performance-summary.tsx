// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useEffect, useState } from "react";

interface PerformanceEntry {
  name: string;
  value: number;
  unit: string;
  description: string;
}

/**
 * Performance metrics utility for monitoring optimization improvements
 * Provides insights into bundle size, loading times, and resource efficiency
 */
export function usePerformanceMetrics() {
  const [metrics, setMetrics] = useState<PerformanceEntry[]>([]);

  useEffect(() => {
    // Wait for page to load completely
    const collectMetrics = () => {
      const performanceMetrics: PerformanceEntry[] = [];

      // Navigation timing metrics
      if (typeof window !== 'undefined' && window.performance) {
        const navigation = window.performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
        
        if (navigation) {
          performanceMetrics.push({
            name: 'DOM Content Loaded',
            value: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,
            unit: 'ms',
            description: 'Time to parse HTML and construct DOM'
          });

          performanceMetrics.push({
            name: 'Load Complete',
            value: navigation.loadEventEnd - navigation.loadEventStart,
            unit: 'ms',
            description: 'Total page load time'
          });

          performanceMetrics.push({
            name: 'DNS Lookup',
            value: navigation.domainLookupEnd - navigation.domainLookupStart,
            unit: 'ms',
            description: 'DNS resolution time'
          });

          performanceMetrics.push({
            name: 'Connection Time',
            value: navigation.connectEnd - navigation.connectStart,
            unit: 'ms',
            description: 'TCP connection establishment'
          });
        }

        // Resource timing for critical resources
        const resources = window.performance.getEntriesByType('resource') as PerformanceResourceTiming[];
        const jsResources = resources.filter(r => r.name.includes('.js'));
        const cssResources = resources.filter(r => r.name.includes('.css'));

        if (jsResources.length > 0) {
          const totalJSTime = jsResources.reduce((acc, r) => acc + r.duration, 0);
          performanceMetrics.push({
            name: 'JavaScript Load Time',
            value: totalJSTime,
            unit: 'ms',
            description: `Total time to load ${jsResources.length} JS files`
          });
        }

        if (cssResources.length > 0) {
          const totalCSSTime = cssResources.reduce((acc, r) => acc + r.duration, 0);
          performanceMetrics.push({
            name: 'CSS Load Time',
            value: totalCSSTime,
            unit: 'ms',
            description: `Total time to load ${cssResources.length} CSS files`
          });
        }

        // Memory usage (if available)
        if ((window.performance as any).memory) {
          const memory = (window.performance as any).memory;
          performanceMetrics.push({
            name: 'JS Heap Size',
            value: Math.round(memory.usedJSHeapSize / 1024 / 1024),
            unit: 'MB',
            description: 'Current JavaScript memory usage'
          });
        }
      }

      setMetrics(performanceMetrics);
    };

    // Collect metrics after page load
    if (document.readyState === 'complete') {
      collectMetrics();
    } else {
      window.addEventListener('load', collectMetrics);
      return () => window.removeEventListener('load', collectMetrics);
    }
  }, []);

  return metrics;
}

/**
 * Performance summary component for development insights
 */
export function PerformanceSummary() {
  const metrics = usePerformanceMetrics();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    // Only show in development with a keyboard shortcut
    const handleKeyPress = (event: KeyboardEvent) => {
      // Ctrl/Cmd + Shift + P to toggle performance metrics
      if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'P') {
        setIsVisible(!isVisible);
      }
    };

    if (process.env.NODE_ENV === 'development') {
      window.addEventListener('keydown', handleKeyPress);
      return () => window.removeEventListener('keydown', handleKeyPress);
    }
  }, [isVisible]);

  if (!isVisible || process.env.NODE_ENV !== 'development') {
    return null;
  }

  return (
    <div className="fixed top-4 left-4 z-50 max-w-md rounded-lg bg-background/95 p-4 shadow-xl backdrop-blur-sm border">
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-sm font-semibold">Performance Metrics</h3>
        <button
          onClick={() => setIsVisible(false)}
          className="text-muted-foreground hover:text-foreground"
        >
          ✕
        </button>
      </div>
      <div className="space-y-2 text-xs">
        {metrics.length === 0 ? (
          <p className="text-muted-foreground">Loading metrics...</p>
        ) : (
          metrics.map((metric, index) => (
            <div key={index} className="border-b border-border/20 pb-2">
              <div className="flex justify-between items-center">
                <span className="font-medium">{metric.name}:</span>
                <span className="font-mono">
                  {metric.value.toFixed(1)}{metric.unit}
                </span>
              </div>
              <p className="text-muted-foreground mt-1">{metric.description}</p>
            </div>
          ))
        )}
      </div>
      <div className="mt-3 pt-2 border-t border-border/20">
        <p className="text-muted-foreground text-xs">
          Press Ctrl+Shift+P to toggle this panel
        </p>
      </div>
    </div>
  );
}
