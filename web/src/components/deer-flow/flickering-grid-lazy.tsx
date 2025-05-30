// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

"use client";

import { lazy, Suspense } from "react";
import { cn } from "~/lib/utils";

// Lazy load the FlickeringGrid to reduce initial bundle size
const LazyFlickeringGrid = lazy(() =>
  import("../magicui/flickering-grid").then((mod) => ({
    default: mod.FlickeringGrid,
  }))
);

interface OptimizedFlickeringGridProps {
  squareSize?: number;
  gridGap?: number;
  flickerChance?: number;
  color?: string;
  width?: number;
  height?: number;
  className?: string;
  maxOpacity?: number;
  id?: string;
}

// Fallback component for loading
const FlickeringGridFallback = ({ 
  className, 
  id 
}: { 
  className?: string; 
  id?: string; 
}) => (
  <div 
    id={id}
    className={cn("h-full w-full", className)} 
    style={{ 
      background: "transparent" 
    }} 
  />
);

export function OptimizedFlickeringGrid(props: OptimizedFlickeringGridProps) {
  return (
    <Suspense fallback={<FlickeringGridFallback className={props.className} id={props.id} />}>
      <LazyFlickeringGrid {...props} />
    </Suspense>
  );
}
