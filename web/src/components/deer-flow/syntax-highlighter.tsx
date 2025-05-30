// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { lazy, Suspense } from "react";
import { Skeleton } from "~/components/ui/skeleton";
import { cn } from "~/lib/utils";

// Import styles directly to avoid lazy loading issues
import oneDark from "react-syntax-highlighter/dist/esm/styles/prism/one-dark";
import prism from "react-syntax-highlighter/dist/esm/styles/prism/prism";

// Lazy load syntax highlighter to reduce initial bundle size
const LazySyntaxHighlighter = lazy(() =>
  import("react-syntax-highlighter").then((mod) => ({
    default: mod.Prism,
  }))
);

interface OptimizedSyntaxHighlighterProps {
  children: string;
  language?: string;
  theme?: "dark" | "light";
  className?: string;
  showLineNumbers?: boolean;
  customStyle?: React.CSSProperties;
}

const SyntaxHighlighterSkeleton = ({ 
  children, 
  className 
}: { 
  children: string; 
  className?: string; 
}) => (
  <pre className={cn("rounded-md bg-muted p-4", className)}>
    <code className="text-sm">{children}</code>
  </pre>
);

export function OptimizedSyntaxHighlighter({
  children,
  language = "text",
  theme = "dark",
  className,
  showLineNumbers = false,
  customStyle,
}: OptimizedSyntaxHighlighterProps) {
  const style = theme === "dark" ? oneDark : prism;

  return (
    <Suspense fallback={<SyntaxHighlighterSkeleton className={className}>{children}</SyntaxHighlighterSkeleton>}>
      <LazySyntaxHighlighter
        language={language}
        style={style}
        showLineNumbers={showLineNumbers}
        customStyle={customStyle}
        className={className}
      >
        {children}
      </LazySyntaxHighlighter>
    </Suspense>
  );
}
