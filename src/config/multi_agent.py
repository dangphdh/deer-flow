# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Union, Any

from src.config.configuration import Configuration


@dataclass
class MultiAgentExpertConfig:
    """Configuration for multi-agent expert collaborations."""
    
    # Enable/disable multi-agent expert functionality
    enabled: bool = True
    
    # Maximum number of experts to use in a collaboration
    max_experts: int = 4
    
    # Number of rounds for multi-agent collaboration
    max_rounds: int = 3
    
    # Minimum number of turns before synthesis
    synthesis_interval: int = 3
    
    # Maximum insights before early stopping
    max_insights: int = 12
    
    # Expert types to always include (if available)
    default_expert_types: List[str] = field(default_factory=lambda: [
        "research_analyst",
        "technical_architect"
    ])
    
    # LLM type for synthesis and coordination
    coordinator_llm_type: str = "reasoning"
    
    # Enable dynamic expert generation based on topics
    dynamic_experts: bool = True
    

def get_multi_agent_config(config: Configuration) -> MultiAgentExpertConfig:
    """Get multi-agent configuration from global config."""
    if not hasattr(config, "multi_agent") or not config.multi_agent:
        return MultiAgentExpertConfig()
        
    # Extract multi-agent settings from config
    multi_agent_config = MultiAgentExpertConfig()
    
    # Override defaults with values from config
    ma_config = config.multi_agent
    if isinstance(ma_config, dict):
        if "enabled" in ma_config:
            multi_agent_config.enabled = bool(ma_config["enabled"])
            
        if "max_experts" in ma_config:
            multi_agent_config.max_experts = int(ma_config["max_experts"])
            
        if "max_rounds" in ma_config:
            multi_agent_config.max_rounds = int(ma_config["max_rounds"])
            
        if "synthesis_interval" in ma_config:
            multi_agent_config.synthesis_interval = int(ma_config["synthesis_interval"])
            
        if "max_insights" in ma_config:
            multi_agent_config.max_insights = int(ma_config["max_insights"])
            
        if "default_expert_types" in ma_config:
            multi_agent_config.default_expert_types = ma_config["default_expert_types"]
            
        if "coordinator_llm_type" in ma_config:
            multi_agent_config.coordinator_llm_type = ma_config["coordinator_llm_type"]
            
        if "dynamic_experts" in ma_config:
            multi_agent_config.dynamic_experts = bool(ma_config["dynamic_experts"])
    
    return multi_agent_config