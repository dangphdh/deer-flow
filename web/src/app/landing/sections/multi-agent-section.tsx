// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import { OptimizedMultiAgentVisualization } from "../components/multi-agent-visualization-lazy";
import { SectionHeader } from "../components/section-header";

export function MultiAgentSection() {
  return (
    <section className="relative flex w-full flex-col items-center justify-center">
      <SectionHeader
        anchor="multi-agent-architecture"
        title="Multi-Agent Architecture"
        description="Experience the agent teamwork with our Supervisor + Handoffs design pattern."
      />
      <div className="flex h-[70vh] w-full flex-col items-center justify-center">
        <div className="h-full w-full">
          <OptimizedMultiAgentVisualization />
        </div>
      </div>
    </section>
  );
}
