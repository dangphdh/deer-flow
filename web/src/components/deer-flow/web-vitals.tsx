// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

'use client';

import { useEffect } from 'react';
import { type Metric } from 'web-vitals';

function sendToAnalytics(metric: Metric) {
  // Only log in development for now
  if (process.env.NODE_ENV === 'development') {
    console.log('Web Vitals:', metric);
  }
  
  // In production, you might want to send to your analytics service
  // Example: analytics.track('Web Vitals', metric);
}

export function WebVitals() {
  useEffect(() => {
    async function loadWebVitals() {
      const { onCLS, onINP, onFCP, onLCP, onTTFB } = await import('web-vitals');
      
      onCLS(sendToAnalytics);
      onINP(sendToAnalytics);
      onFCP(sendToAnalytics);
      onLCP(sendToAnalytics);
      onTTFB(sendToAnalytics);
    }
    
    loadWebVitals();
  }, []);

  return null;
}
