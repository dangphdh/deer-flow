# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import asyncio
import unittest
import logging
from datetime import datetime
import json
from pathlib import Path

from src.workflow import run_agent_workflow_async
from src.config.multi_agent import MultiAgentExpertConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class TestMultiAgentExperts(unittest.TestCase):
    """Test cases to compare standard research workflow with multi-agent experts."""

    def setUp(self):
        """Set up test parameters."""
        self.test_topics = [
            "the impact of quantum computing on modern cryptography",
            "sustainable energy solutions for urban environments",
            "ethical considerations in artificial intelligence deployment"
        ]
        
        # Output directory for test results
        output_dir = Path("./tests/output/multi_agent_comparison")
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        
        # Common parameters
        self.common_params = {
            "max_plan_iterations": 1,
            "max_step_num": 2,  # Smaller number for testing
            "enable_background_investigation": True,
            "debug": False
        }
    
    def capture_state_changes(self, state_changes, label):
        """Capture state changes from workflow to a file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = self.output_dir / f"{label}_{timestamp}.json"
        
        with open(filename, "w") as f:
            json.dump(state_changes, f, indent=2)
        
        return filename
    
    async def _run_workflow_with_capture(self, input_text, enable_multi_agent=False):
        """Run workflow and capture state changes."""
        state_changes = []
        
        # Create a callback to capture state changes
        async def state_callback(state):
            state_copy = {k: v for k, v in state.items() if k not in ["messages", "observations"]}
            if "current_plan" in state_copy and hasattr(state_copy["current_plan"], "model_dump"):
                state_copy["current_plan"] = state_copy["current_plan"].model_dump()
            state_changes.append(state_copy)
        
        # Run workflow
        final_state = await run_agent_workflow_async(
            user_input=input_text,
            enable_multi_agent_experts=enable_multi_agent,
            **self.common_params
        )
        
        return state_changes, final_state
    
    def test_compare_workflows(self):
        """Compare standard workflow with multi-agent experts workflow."""
        results = {}
        
        for topic in self.test_topics:
            # Format both test prompts the same way
            standard_prompt = f"Provide a comprehensive analysis of '{topic}'."
            multi_agent_prompt = f"Provide a comprehensive analysis of '{topic}'."
            
            # Run standard workflow
            standard_changes, standard_final = asyncio.run(
                self._run_workflow_with_capture(standard_prompt, enable_multi_agent=False)
            )
            
            # Run multi-agent workflow
            multi_agent_changes, multi_agent_final = asyncio.run(
                self._run_workflow_with_capture(multi_agent_prompt, enable_multi_agent=True)
            )
            
            # Save results
            standard_file = self.capture_state_changes(standard_changes, f"standard_{topic.replace(' ', '_')[:20]}")
            multi_agent_file = self.capture_state_changes(multi_agent_changes, f"multi_agent_{topic.replace(' ', '_')[:20]}")
            
            results[topic] = {
                "standard_file": str(standard_file),
                "multi_agent_file": str(multi_agent_file),
                "standard_steps": len(standard_changes),
                "multi_agent_steps": len(multi_agent_changes),
            }
            
            logger.info(f"Completed comparison for topic: {topic}")
            logger.info(f"Standard workflow: {standard_file}")
            logger.info(f"Multi-agent workflow: {multi_agent_file}")
        
        # Output summary
        summary_file = self.output_dir / "comparison_summary.json"
        with open(summary_file, "w") as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Comparison summary written to: {summary_file}")


class TestMultiAgentComponents(unittest.TestCase):
    """Test individual components of the multi-agent expert system."""
    
    def test_expert_agent_creation(self):
        """Test that expert agents can be created correctly."""
        from src.agents.expert_agents import create_expert_agent, EXPERT_PROFILES
        
        # Test creating each predefined expert type
        for expert_type, profile in EXPERT_PROFILES.items():
            expert = create_expert_agent(expert_type)
            self.assertEqual(expert.profile.name, profile.name)
            self.assertEqual(expert.profile.domain_expertise, profile.domain_expertise)
    
    def test_dynamic_expert_generation(self):
        """Test dynamic expert generation based on topic."""
        from src.agents.expert_agents import generate_dynamic_experts
        
        # Test with a specific topic
        topic = "cybersecurity in cloud computing"
        experts = generate_dynamic_experts(topic, num_experts=2)
        
        # Verify we got the expected number of experts
        self.assertGreaterEqual(len(experts), 1)
        self.assertLessEqual(len(experts), 3)  # Allowing for fallback case
        
        # Check that profiles have required fields
        for expert in experts:
            self.assertTrue(hasattr(expert, "name"))
            self.assertTrue(hasattr(expert, "role_description"))
            self.assertTrue(hasattr(expert, "domain_expertise"))
            self.assertTrue(hasattr(expert, "perspective"))
    
    def test_multi_agent_coordinator(self):
        """Test the multi-agent coordinator functionality."""
        from src.agents.multi_agent_coordinator import MultiAgentCoordinator
        
        # Create coordinator
        coordinator = MultiAgentCoordinator(max_experts=2)
        
        # Start collaboration session
        topic = "test topic"
        session_id = coordinator.start_collaboration(
            topic=topic,
            expert_types=["research_analyst", "technical_architect"]
        )
        
        # Verify session was created
        self.assertIn(session_id, coordinator.sessions)
        self.assertEqual(coordinator.sessions[session_id].topic, topic)
        self.assertEqual(len(coordinator.sessions[session_id].experts), 2)


if __name__ == "__main__":
    unittest.main()
