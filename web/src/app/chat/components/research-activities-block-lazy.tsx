// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { lazy, Suspense } from "react";

import { Skeleton } from "~/components/ui/skeleton";
import { cn } from "~/lib/utils";

// Lazy load the research activities block to reduce initial bundle size
const LazyResearchActivitiesBlock = lazy(() =>
  import("./research-activities-block").then((mod) => ({
    default: mod.ResearchActivitiesBlock,
  }))
);

// Loading skeleton for research activities
const ResearchActivitiesSkeleton = ({ className }: { className?: string }) => (
  <div className={cn("flex flex-col py-4", className)}>
    {Array.from({ length: 3 }).map((_, i) => (
      <div key={i} className="mb-4 pl-4">
        <div className="flex items-center space-x-2">
          <Skeleton className="h-4 w-4" />
          <Skeleton className="h-4 w-32" />
        </div>
        <Skeleton className="mt-2 h-20 w-full rounded-md" />
      </div>
    ))}
  </div>
);

export function OptimizedResearchActivitiesBlock({
  className,
  researchId,
}: {
  className?: string;
  researchId: string;
}) {
  return (
    <Suspense fallback={<ResearchActivitiesSkeleton className={className} />}>
      <LazyResearchActivitiesBlock className={className} researchId={researchId} />
    </Suspense>
  );
}
