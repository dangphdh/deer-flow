// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import type { Metadata } from "next";
import dynamic from "next/dynamic";
import { useMemo } from "react";

import { SiteHeader } from "./chat/components/site-header";
import { Jumbotron } from "./landing/components/jumbotron";

// Static metadata for better SEO and performance
export const metadata: Metadata = {
  title: "🌸 OverBloom - AI-Powered Research Platform",
  description: "Deep Exploration and Efficient Research platform that combines language models with specialized tools for complex research tasks. Multi-agent workflow automation.",
  keywords: ["AI research", "multi-agent", "workflow automation", "LLM", "research platform"],
  openGraph: {
    title: "🌸 OverBloom - AI-Powered Research Platform",
    description: "Transform your research workflow with AI-powered multi-agent automation",
    type: "website",
  },
  robots: {
    index: true,
    follow: true,
  },
};

// Lazy load below-the-fold components for better initial page load
const Ray = dynamic(() => import("./landing/components/ray").then(mod => ({ default: mod.Ray })));

const CaseStudySection = dynamic(() => import("./landing/sections/case-study-section").then(mod => ({ default: mod.CaseStudySection })), {
  loading: () => <div className="h-96 animate-pulse bg-muted/20 rounded-lg" />,
});

const MultiAgentSection = dynamic(() => import("./landing/sections/multi-agent-section").then(mod => ({ default: mod.MultiAgentSection })), {
  loading: () => <div className="h-96 animate-pulse bg-muted/20 rounded-lg" />,
});

const CoreFeatureSection = dynamic(() => import("./landing/sections/core-features-section").then(mod => ({ default: mod.CoreFeatureSection })), {
  loading: () => <div className="h-96 animate-pulse bg-muted/20 rounded-lg" />,
});

const JoinCommunitySection = dynamic(() => import("./landing/sections/join-community-section").then(mod => ({ default: mod.JoinCommunitySection })), {
  loading: () => <div className="h-48 animate-pulse bg-muted/20 rounded-lg" />,
});

export default function HomePage() {
  return (
    <div className="flex flex-col items-center">
      <SiteHeader />
      <main className="container flex flex-col items-center justify-center gap-56">
        <Jumbotron />
        <CaseStudySection />
        <MultiAgentSection />
        <CoreFeatureSection />
        <JoinCommunitySection />
      </main>
      <Footer />
      <Ray />
    </div>
  );
}

function Footer() {
  const year = useMemo(() => new Date().getFullYear(), []);
  return (
    <footer className="container mt-32 flex flex-col items-center justify-center">
      <hr className="from-border/0 via-border/70 to-border/0 m-0 h-px w-full border-none bg-gradient-to-r" />
      <div className="text-muted-foreground container flex h-20 flex-col items-center justify-center text-sm">
        <p className="text-center font-serif text-lg md:text-xl">
          &quot;Originated from Open Source, give back to Open Source.&quot;
        </p>
      </div>
      <div className="text-muted-foreground container mb-8 flex flex-col items-center justify-center text-xs">
        <p>Licensed under MIT License</p>
        <p>&copy; {year} OverBloom</p>
      </div>
    </footer>
  );
}
