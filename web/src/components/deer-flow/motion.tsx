// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { lazy, Suspense, type ComponentProps } from "react";

// Lazy load framer-motion components to reduce initial bundle size

// Create specific motion components
const LazyMotionDiv = lazy(() =>
  import("framer-motion").then((mod) => ({ default: mod.motion.div }))
);

const LazyMotionLi = lazy(() =>
  import("framer-motion").then((mod) => ({ default: mod.motion.li }))
);

const LazyMotionSpan = lazy(() =>
  import("framer-motion").then((mod) => ({ default: mod.motion.span }))
);

const LazyAnimatePresence = lazy(() =>
  import("framer-motion").then((mod) => ({ default: mod.AnimatePresence }))
);

// Fallback component for loading states
const MotionFallback = ({ children, className, ...props }: any) => (
  <div className={className} {...props}>
    {children}
  </div>
);

// Type-safe motion component props
type MotionDivProps = {
  children?: React.ReactNode;
  className?: string;
  initial?: any;
  animate?: any;
  exit?: any;
  transition?: any;
  style?: React.CSSProperties;
  [key: string]: any;
};

// Optimized motion components with suspense boundaries
export const MotionDiv = (props: MotionDivProps) => (
  <Suspense fallback={<MotionFallback {...props} />}>
    <LazyMotionDiv {...props} />
  </Suspense>
);

export const MotionLi = (props: MotionDivProps) => (
  <Suspense fallback={<li className={props.className}>{props.children}</li>}>
    <LazyMotionLi {...props} />
  </Suspense>
);

export const MotionSpan = (props: MotionDivProps) => (
  <Suspense fallback={<span className={props.className}>{props.children}</span>}>
    <LazyMotionSpan {...props} />
  </Suspense>
);

type AnimatePresenceProps = {
  children?: React.ReactNode;
  mode?: "wait" | "sync" | "popLayout";
  [key: string]: any;
};

export const OptimizedAnimatePresence = (props: AnimatePresenceProps) => (
  <Suspense fallback={<div>{props.children}</div>}>
    <LazyAnimatePresence {...props} />
  </Suspense>
);
