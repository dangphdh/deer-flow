# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import argparse
import logging
from src.workflow import run_agent_workflow_async
from src.config.multi_agent import get_multi_agent_config, MultiAgentExpertConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


async def run_multi_agent_demo(topic: str, debug: bool = False, max_steps: int = 4):
    """Run a demonstration of the multi-agent expert collaboration feature.
    
    Args:
        topic: The research topic to analyze
        debug: Whether to enable debug logging
        max_steps: Maximum number of steps in the plan
    """
    print(f"\n{'=' * 80}\n")
    print(f"🤖 MULTI-AGENT EXPERT COLLABORATION DEMO: {topic}\n")
    print(f"{'=' * 80}\n")
    
    print("🚀 Starting workflow with multi-agent expert collaboration enabled...\n")
    
    await run_agent_workflow_async(
        user_input=f"Provide a comprehensive analysis of '{topic}'. Use multiple expert perspectives and synthesize insights.",
        debug=debug,
        max_plan_iterations=1,
        max_step_num=max_steps,
        enable_background_investigation=True,
        enable_multi_agent_experts=True,  # Enable multi-agent collaboration
    )
    
    print(f"\n{'=' * 80}\n")
    print("✅ Multi-agent expert collaboration demonstration completed!")
    print(f"{'=' * 80}\n")


def main():
    """Parse command line arguments and run the demo."""
    parser = argparse.ArgumentParser(
        description="Demonstrate multi-agent expert collaboration in Deer Flow"
    )
    
    parser.add_argument(
        "--topic", 
        type=str, 
        default="the impact of quantum computing on modern cryptography",
        help="The research topic to analyze with multi-agent experts"
    )
    
    parser.add_argument(
        "--debug", 
        action="store_true",
        help="Enable debug logging"
    )
    
    parser.add_argument(
        "--max-steps", 
        type=int, 
        default=4,
        help="Maximum number of steps in the plan"
    )
    
    args = parser.parse_args()
    
    # Run the async demo
    asyncio.run(run_multi_agent_demo(
        topic=args.topic,
        debug=args.debug,
        max_steps=args.max_steps
    ))


if __name__ == "__main__":
    main()