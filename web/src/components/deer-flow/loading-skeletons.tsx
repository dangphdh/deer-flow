// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { Skeleton } from "~/components/ui/skeleton";

export function LandingSkeleton() {
  return (
    <div className="flex flex-col items-center gap-56">
      {/* Header skeleton */}
      <div className="w-full h-16">
        <Skeleton className="h-full w-full" />
      </div>
      
      {/* Jumbotron skeleton */}
      <div className="container flex flex-col items-center gap-8">
        <Skeleton className="h-12 w-96" />
        <Skeleton className="h-6 w-64" />
        <Skeleton className="h-10 w-32" />
      </div>
      
      {/* Section skeletons */}
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="container">
          <Skeleton className="h-96 w-full rounded-lg" />
        </div>
      ))}
    </div>
  );
}

export function ChatSkeleton() {
  return (
    <div className="flex h-full w-full items-center justify-center">
      <div className="flex flex-col items-center gap-4">
        <Skeleton className="h-16 w-16 rounded-full" />
        <Skeleton className="h-4 w-32" />
      </div>
    </div>
  );
}
