import { env } from "~/env";

import { type DeerFlowConfig } from "../config/types";

import { resolveServiceURL } from "./resolve-service-url";

// Default configuration fallback for when the API is not available
const DEFAULT_CONFIG: DeerFlowConfig = {
  max_search_results: 5,
  search_before_planning: true,
  max_plan_iterations: 2,
  enable_deep_thinking: true,
  resources: [],
  static_website_only: env.NEXT_PUBLIC_STATIC_WEBSITE_ONLY ?? false,
  models: {
    basic: ["gpt-3.5-turbo"],
    reasoning: ["gpt-4"],
  },
  rag: {
    provider: "default",
  },
};

declare global {
  interface Window {
    __deerflowConfig: DeerFlowConfig;
  }
}

export async function loadConfig() {
  try {
    // Set a timeout to prevent hanging during server-side rendering
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), 3000);
    
    const res = await fetch(resolveServiceURL("./config"), {
      signal: controller.signal,
      next: { revalidate: 60 } // Cache for 60 seconds
    });
    
    clearTimeout(timeoutId);
    
    if (!res.ok) {
      console.warn(`Failed to load config: ${res.status} ${res.statusText}`);
      return DEFAULT_CONFIG;
    }
    
    const config = await res.json();
    return config;
  } catch (error) {
    console.warn("Error loading config, using default:", error);
    return DEFAULT_CONFIG;
  }
}

export function getConfig(): DeerFlowConfig {
  if (
    typeof window === "undefined" ||
    typeof window.__deerflowConfig === "undefined"
  ) {
    // For server-side rendering or when config isn't available, return default config
    console.warn("Config not available on window, using default config");
    return DEFAULT_CONFIG;
  }
  return window.__deerflowConfig;
}
