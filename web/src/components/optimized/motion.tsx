// Optimized motion components with dynamic imports to reduce initial bundle size
"use client";

import dynamic from 'next/dynamic';
import { type ReactNode } from 'react';

// Dynamic imports for motion components to reduce initial bundle size
const MotionDiv = dynamic(() => import('framer-motion').then(mod => ({ default: mod.motion.div })), {
  ssr: false,
  loading: () => <div style={{ opacity: 0 }} />,
});

const MotionLi = dynamic(() => import('framer-motion').then(mod => ({ default: mod.motion.li })), {
  ssr: false,
  loading: () => <li style={{ opacity: 0 }} />,
});

const MotionSpan = dynamic(() => import('framer-motion').then(mod => ({ default: mod.motion.span })), {
  ssr: false,
  loading: () => <span style={{ opacity: 0 }} />,
});

const AnimatePresence = dynamic(() => import('framer-motion').then(mod => ({ default: mod.AnimatePresence })), {
  ssr: false,
  loading: () => <>{/* empty loading state */}</>,
});

// Simplified motion props for common use cases
interface BasicMotionProps {
  children: ReactNode;
  className?: string;
  style?: React.CSSProperties;
  initial?: { opacity?: number; y?: string | number; scale?: number };
  animate?: { opacity?: number; y?: string | number; scale?: number };
  exit?: { opacity?: number; y?: string | number; scale?: number };
  transition?: { duration?: number; ease?: string; delay?: number };
  whileHover?: { scale?: number };
  onClick?: () => void;
}

interface MotionDivProps extends BasicMotionProps {
  ref?: React.RefObject<HTMLDivElement | null>;
}

interface MotionLiProps extends BasicMotionProps {
  ref?: React.RefObject<HTMLLIElement | null>;
}

interface MotionSpanProps extends BasicMotionProps {
  ref?: React.RefObject<HTMLSpanElement | null>;
}

export function OptimizedMotionDiv(props: MotionDivProps) {
  return <MotionDiv {...props} />;
}

export function OptimizedMotionLi(props: MotionLiProps) {
  return <MotionLi {...props} />;
}

export function OptimizedMotionSpan(props: MotionSpanProps) {
  return <MotionSpan {...props} />;
}

export function OptimizedAnimatePresence({ 
  children, 
  mode = "wait" 
}: { 
  children: ReactNode; 
  mode?: "wait" | "sync" | "popLayout"; 
}) {
  return <AnimatePresence mode={mode}>{children}</AnimatePresence>;
}

// Fallback components for SSR or when motion is disabled
export function StaticDiv({ children, className, style, onClick }: Omit<MotionDivProps, 'initial' | 'animate' | 'exit' | 'transition' | 'whileHover' | 'ref'>) {
  return <div className={className} style={style} onClick={onClick}>{children}</div>;
}

export function StaticLi({ children, className, style, onClick }: Omit<MotionLiProps, 'initial' | 'animate' | 'exit' | 'transition' | 'whileHover' | 'ref'>) {
  return <li className={className} style={style} onClick={onClick}>{children}</li>;
}

export function StaticSpan({ children, className, style, onClick }: Omit<MotionSpanProps, 'initial' | 'animate' | 'exit' | 'transition' | 'whileHover' | 'ref'>) {
  return <span className={className} style={style} onClick={onClick}>{children}</span>;
}
