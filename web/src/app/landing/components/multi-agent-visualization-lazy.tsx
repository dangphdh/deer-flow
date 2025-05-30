// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { lazy, Suspense } from "react";

import { Skeleton } from "~/components/ui/skeleton";
import { cn } from "~/lib/utils";

// Lazy load the multi-agent visualization to reduce initial bundle size
const LazyMultiAgentVisualization = lazy(() =>
  import("./multi-agent-visualization").then((mod) => ({
    default: mod.MultiAgentVisualization,
  }))
);

// Loading component with skeleton
const MultiAgentVisualizationSkeleton = ({ className }: { className?: string }) => (
  <div className={cn("flex h-full w-full flex-col pb-4", className)}>
    <div className="flex min-h-0 flex-grow rounded-lg border bg-background">
      <div className="flex h-full w-full items-center justify-center">
        <div className="flex flex-col items-center space-y-4">
          <Skeleton className="h-12 w-12 rounded-full" />
          <Skeleton className="h-4 w-32" />
          <div className="flex space-x-4">
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-8 w-8 rounded-full" />
            <Skeleton className="h-8 w-8 rounded-full" />
          </div>
        </div>
      </div>
    </div>
    <div className="h-4 shrink-0"></div>
    <div className="flex h-6 w-full shrink-0 items-center justify-center">
      <div className="bg-muted/50 z-[200] flex rounded-3xl px-4 py-2">
        <Skeleton className="h-6 w-6 rounded" />
        <Skeleton className="ml-2 h-6 w-6 rounded" />
        <Skeleton className="ml-2 h-6 w-40 rounded" />
        <Skeleton className="ml-2 h-6 w-6 rounded" />
      </div>
    </div>
  </div>
);

export function OptimizedMultiAgentVisualization({ 
  className 
}: { 
  className?: string 
}) {
  return (
    <Suspense fallback={<MultiAgentVisualizationSkeleton className={className} />}>
      <LazyMultiAgentVisualization className={className} />
    </Suspense>
  );
}
