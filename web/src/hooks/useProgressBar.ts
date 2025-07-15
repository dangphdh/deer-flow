/**
 * Utility hook for progress bar styling without inline styles
 */

import { useEffect, useRef } from 'react';

export function useProgressBar(progress: number) {
  const progressRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (progressRef.current) {
      progressRef.current.style.width = `${progress}%`;
    }
  }, [progress]);

  return progressRef;
}
