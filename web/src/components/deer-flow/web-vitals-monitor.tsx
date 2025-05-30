// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { useEffect, useState } from "react";
import { onCLS, onFCP, onLCP, onTTFB, onINP } from "web-vitals";

interface WebVitalsData {
  cls?: number;
  fcp?: number;
  inp?: number;
  lcp?: number;
  ttfb?: number;
}

interface VitalMetric {
  name: string;
  value: number;
  rating: 'good' | 'needs-improvement' | 'poor';
  threshold: { good: number; poor: number };
}

export function useWebVitals() {
  const [vitals, setVitals] = useState<WebVitalsData>({});

  useEffect(() => {
    // Cumulative Layout Shift
    onCLS((metric) => {
      setVitals(prev => ({ ...prev, cls: metric.value }));
    });

    // First Contentful Paint
    onFCP((metric) => {
      setVitals(prev => ({ ...prev, fcp: metric.value }));
    });

    // First Input Delay (replaced with Interaction to Next Paint in v4)
    onINP((metric) => {
      setVitals(prev => ({ ...prev, inp: metric.value }));
    });

    // Largest Contentful Paint
    onLCP((metric) => {
      setVitals(prev => ({ ...prev, lcp: metric.value }));
    });

    // Time to First Byte
    onTTFB((metric) => {
      setVitals(prev => ({ ...prev, ttfb: metric.value }));
    });
  }, []);

  const getMetrics = (): VitalMetric[] => {
    const metrics: VitalMetric[] = [];

    if (vitals.cls !== undefined) {
      metrics.push({
        name: 'CLS',
        value: vitals.cls,
        rating: vitals.cls <= 0.1 ? 'good' : vitals.cls <= 0.25 ? 'needs-improvement' : 'poor',
        threshold: { good: 0.1, poor: 0.25 }
      });
    }

    if (vitals.fcp !== undefined) {
      metrics.push({
        name: 'FCP',
        value: vitals.fcp,
        rating: vitals.fcp <= 1800 ? 'good' : vitals.fcp <= 3000 ? 'needs-improvement' : 'poor',
        threshold: { good: 1800, poor: 3000 }
      });
    }

    if (vitals.inp !== undefined) {
      metrics.push({
        name: 'INP',
        value: vitals.inp,
        rating: vitals.inp <= 200 ? 'good' : vitals.inp <= 500 ? 'needs-improvement' : 'poor',
        threshold: { good: 200, poor: 500 }
      });
    }

    if (vitals.lcp !== undefined) {
      metrics.push({
        name: 'LCP',
        value: vitals.lcp,
        rating: vitals.lcp <= 2500 ? 'good' : vitals.lcp <= 4000 ? 'needs-improvement' : 'poor',
        threshold: { good: 2500, poor: 4000 }
      });
    }

    if (vitals.ttfb !== undefined) {
      metrics.push({
        name: 'TTFB',
        value: vitals.ttfb,
        rating: vitals.ttfb <= 800 ? 'good' : vitals.ttfb <= 1800 ? 'needs-improvement' : 'poor',
        threshold: { good: 800, poor: 1800 }
      });
    }

    return metrics;
  };

  return { vitals, getMetrics };
}

/**
 * Performance monitoring component for development
 * Only shows in development mode to avoid production bundle size impact
 */
export function WebVitalsMonitor() {
  const { getMetrics } = useWebVitals();
  const [showMonitor, setShowMonitor] = useState(false);

  useEffect(() => {
    // Only show in development
    if (process.env.NODE_ENV === 'development') {
      // Show monitor after a delay to avoid affecting initial load metrics
      const timer = setTimeout(() => setShowMonitor(true), 3000);
      return () => clearTimeout(timer);
    }
  }, []);

  if (!showMonitor || process.env.NODE_ENV !== 'development') {
    return null;
  }

  const metrics = getMetrics();

  return (
    <div className="fixed bottom-4 right-4 z-50 rounded-lg bg-background/90 p-3 shadow-lg backdrop-blur-sm border">
      <h3 className="text-sm font-semibold mb-2">Core Web Vitals</h3>
      <div className="space-y-1">
        {metrics.map((metric) => (
          <div key={metric.name} className="flex items-center justify-between text-xs">
            <span className="font-mono">{metric.name}:</span>
            <span 
              className={`font-mono px-2 py-1 rounded ${
                metric.rating === 'good' 
                  ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-100'
                  : metric.rating === 'needs-improvement'
                  ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-100'
                  : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-100'
              }`}
            >
              {metric.value.toFixed(metric.name === 'CLS' ? 3 : 0)}
              {metric.name === 'CLS' ? '' : 'ms'}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
