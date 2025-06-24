export interface ModelConfig {
  basic: string[];
  reasoning: string[];
}

export interface RagConfig {
  provider: string;
}

export interface ResourceFile {
  title: string;
  description: string;
  path: string;
}

export interface DeerFlowConfig {
  rag?: RagConfig;
  models?: ModelConfig;
  max_search_results?: number;
  search_before_planning?: boolean;
  max_plan_iterations?: number;
  enable_deep_thinking?: boolean;
  resources?: ResourceFile[];
  static_website_only?: boolean;
}
