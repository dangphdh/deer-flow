// Optimized SyntaxHighlighter component with dynamic imports
"use client";

import dynamic from 'next/dynamic';
import { useTheme } from 'next-themes';
import { memo } from 'react';

// Dynamic import for the main syntax highlighter to reduce initial bundle size
const SyntaxHighlighter = dynamic(() => import('react-syntax-highlighter').then(mod => ({ default: mod.Prism })), {
  ssr: false,
  loading: () => <div className="bg-muted rounded p-4 animate-pulse">Loading code...</div>,
});

interface OptimizedSyntaxHighlighterProps {
  children: string;
  language?: string;
  className?: string;
  showLineNumbers?: boolean;
  customStyle?: React.CSSProperties;
}

const OptimizedSyntaxHighlighter = memo(({
  children,
  language = 'text',
  className = '',
  showLineNumbers = false,
  customStyle = {},
}: OptimizedSyntaxHighlighterProps) => {
  const { resolvedTheme } = useTheme();

  const defaultStyle = {
    margin: 0,
    background: resolvedTheme === 'dark' ? '#1e1e1e' : '#f8f8f8',
    fontSize: '14px',
    ...customStyle,
  };

  return (
    <SyntaxHighlighter
      language={language}
      showLineNumbers={showLineNumbers}
      className={className}
      customStyle={defaultStyle}
    >
      {children}
    </SyntaxHighlighter>
  );
});

OptimizedSyntaxHighlighter.displayName = 'OptimizedSyntaxHighlighter';

export default OptimizedSyntaxHighlighter;
