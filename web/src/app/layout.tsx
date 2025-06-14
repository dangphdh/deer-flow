// Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
// SPDX-License-Identifier: MIT

import "~/styles/globals.css";

import { type Metadata } from "next";
import { Geist } from "next/font/google";
import Script from "next/script";

import { PerformanceSummary } from "~/components/deer-flow/performance-summary";
import { ThemeProviderWrapper } from "~/components/deer-flow/theme-provider-wrapper";
import { WebVitals } from "~/components/deer-flow/web-vitals";
import { WebVitalsMonitor } from "~/components/deer-flow/web-vitals-monitor";
import { loadConfig } from "~/core/api/config";
import { env } from "~/env";

import { Toaster } from "../components/deer-flow/toaster";

export const metadata: Metadata = {
  title: "🌸 OverBloom",
  description:
    "Deep Exploration and Efficient Research, an AI tool that combines language models with specialized tools for research tasks.",
  icons: [{ rel: "icon", url: "/favicon.ico" }],
};

const geist = Geist({
  subsets: ["latin"],
  variable: "--font-geist-sans",
  display: "swap",
  preload: true,
});

export default async function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  const conf = await loadConfig();
  return (
    <html lang="en" className={`${geist.variable}`} suppressHydrationWarning>
      <head>
        {/* Performance optimizations: Resource hints for external domains */}
        <link rel="preconnect" href="https://cdn.amplitude.com" />
        <link rel="dns-prefetch" href="https://cdn.amplitude.com" />
        
        <script>{`window.__deerflowConfig = ${JSON.stringify(conf)}`}</script>
        {/* Define isSpace function globally to fix markdown-it issues with Next.js + Turbopack
          https://github.com/markdown-it/markdown-it/issues/1082#issuecomment-2749656365 */}
        <Script id="markdown-it-fix" strategy="beforeInteractive">
          {`
            if (typeof window !== 'undefined' && typeof window.isSpace === 'undefined') {
              window.isSpace = function(code) {
                return code === 0x20 || code === 0x09 || code === 0x0A || code === 0x0B || code === 0x0C || code === 0x0D;
              };
            }
          `}
        </Script>
      </head>
      <body className="bg-app">
        <ThemeProviderWrapper>{children}</ThemeProviderWrapper>
        <Toaster />
        <WebVitals />
        <WebVitalsMonitor />
        <PerformanceSummary />
        {
          // NO USER BEHAVIOR TRACKING OR PRIVATE DATA COLLECTION BY DEFAULT
          //
          // When `NEXT_PUBLIC_STATIC_WEBSITE_ONLY` is `true`, the script will be injected
          // into the page only when `AMPLITUDE_API_KEY` is provided in `.env`
        }
        {env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY && env.AMPLITUDE_API_KEY && (
          <>
            <Script 
              src="https://cdn.amplitude.com/script/d2197dd1df3f2959f26295bb0e7e849f.js"
              strategy="lazyOnload"
            ></Script>
            <Script id="amplitude-init" strategy="lazyOnload">
              {`
                // Optimize amplitude initialization to not block main thread
                if (typeof window !== 'undefined' && window.amplitude) {
                  window.amplitude.init('${env.AMPLITUDE_API_KEY}', {
                    "fetchRemoteConfig": true,
                    "autocapture": true,
                    "attribution": {
                      "disabled": true  // Disable attribution tracking for better performance
                    },
                    "serverZone": "US",  // Specify server zone to reduce latency
                    "logLevel": "WARN"   // Reduce logging for production performance
                  });
                }
              `}
            </Script>
          </>
        )}
      </body>
    </html>
  );
}
