# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import unittest
import asyncio
from unittest.mock import patch, MagicMock
import json
from pathlib import Path

from src.agents.expert_agents import create_expert_agent, EXPERT_PROFILES
from src.agents.multi_agent_coordinator import MultiAgentCoordinator
from src.workflow import run_agent_workflow_async


class TestMultiAgentComparison(unittest.TestCase):
    """Detailed comparison tests between standard and multi-agent expert workflows."""

    def setUp(self):
        """Set up the test environment."""
        self.test_topic = "the environmental impact of blockchain technology"
        self.output_dir = Path("./tests/output/unit_comparison")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Common workflow parameters (reduced for testing)
        self.workflow_params = {
            "max_plan_iterations": 1,
            "max_step_num": 2,
            "enable_background_investigation": False,
            "debug": False
        }

    @patch("src.agents.multi_agent_coordinator.MultiAgentCoordinator")
    @patch("src.workflow.run_agent_workflow_async")
    def test_multi_agent_activation(self, mock_workflow, mock_coordinator):
        """Test that multi-agent experts are properly activated when enabled."""
        # Setup mocks
        mock_coordinator_instance = MagicMock()
        mock_coordinator.return_value = mock_coordinator_instance
        mock_coordinator_instance.start_collaboration.return_value = "test_session_id"
        
        # Mock workflow return value
        mock_workflow.return_value = {"result": "test_result"}
        
        # Run workflow with multi-agent enabled
        asyncio.run(run_agent_workflow_async(
            user_input=f"Analyze {self.test_topic}",
            enable_multi_agent_experts=True,
            **self.workflow_params
        ))
        
        # Verify multi-agent coordinator was called
        mock_coordinator.assert_called_once()
        mock_coordinator_instance.start_collaboration.assert_called_once()

    @patch("src.agents.multi_agent_coordinator.MultiAgentCoordinator")
    @patch("src.workflow.run_agent_workflow_async")
    def test_multi_agent_not_activated(self, mock_workflow, mock_coordinator):
        """Test that multi-agent experts are not activated when disabled."""
        # Setup mocks
        mock_workflow.return_value = {"result": "test_result"}
        
        # Run workflow with multi-agent disabled
        asyncio.run(run_agent_workflow_async(
            user_input=f"Analyze {self.test_topic}",
            enable_multi_agent_experts=False,
            **self.workflow_params
        ))
        
        # Verify multi-agent coordinator was not called
        mock_coordinator.assert_not_called()

    def test_expert_agents_response_quality(self):
        """Test that expert agents generate appropriate responses."""
        # Create different expert types
        experts = {
            "research": create_expert_agent("research_analyst"),
            "technical": create_expert_agent("technical_architect"),
            "domain": create_expert_agent("domain_expert")
        }
        
        # Test topic
        topic = self.test_topic
        context = f"Analyzing {topic}"
        previous_responses = []
        
        # Get responses from each expert
        responses = {}
        for expert_type, expert in experts.items():
            response = expert.generate_response(topic, context, previous_responses)
            responses[expert_type] = response
            previous_responses.append(f"{expert_type}: {response[:100]}...")
            
            # Assert responses are not empty and have meaningful content
            self.assertIsNotNone(response)
            self.assertGreater(len(response), 100)
            self.assertIn(expert.profile.domain_expertise, response.lower())
        
        # Check that responses differ between experts (specialization check)
        self.assertNotEqual(responses["research"], responses["technical"])
        self.assertNotEqual(responses["research"], responses["domain"])
        
        # Save responses for manual review
        with open(self.output_dir / "expert_responses.json", "w") as f:
            json.dump({k: v for k, v in responses.items()}, f, indent=2)

    def test_collaboration_synthesis(self):
        """Test that collaboration produces a synthesized result."""
        # Create coordinator
        coordinator = MultiAgentCoordinator(max_experts=3, synthesis_interval=2)
        
        # Start collaboration
        session_id = coordinator.start_collaboration(
            topic=self.test_topic,
            context=f"Analyze the following topic: {self.test_topic}",
            expert_types=["research_analyst", "technical_architect", "domain_expert"]
        )
        
        # Run rounds
        for _ in range(2):
            turns = coordinator.run_collaboration_round(session_id)
            self.assertGreater(len(turns), 0)
        
        # Get synthesis
        summary = coordinator.get_collaboration_summary(session_id)
        perspectives = coordinator.get_expert_perspectives(session_id)
        
        # Assert synthesis quality
        self.assertIsNotNone(summary)
        self.assertGreater(len(summary), 100)
        self.assertGreaterEqual(len(perspectives), 2)
        
        # Check that synthesis contains expert perspectives
        for perspective in perspectives.values():
            self.assertIn(perspective[:50].lower(), summary.lower())

    @unittest.skip("This test runs a full workflow and may take time - enable manually")
    def test_end_to_end_comparison(self):
        """Compare standard and multi-agent workflows end to end."""
        # Run standard workflow
        standard_result = asyncio.run(run_agent_workflow_async(
            user_input=f"Analyze {self.test_topic}",
            enable_multi_agent_experts=False,
            **self.workflow_params
        ))
        
        # Run multi-agent workflow
        multi_agent_result = asyncio.run(run_agent_workflow_async(
            user_input=f"Analyze {self.test_topic}",
            enable_multi_agent_experts=True,
            **self.workflow_params
        ))
        
        # Compare and save results
        results = {
            "standard": standard_result,
            "multi_agent": multi_agent_result,
        }
        
        with open(self.output_dir / "workflow_comparison.json", "w") as f:
            json.dump(results, f, indent=2)
            
        # Basic assertions (would need more specific comparisons based on actual output)
        self.assertIsNotNone(standard_result)
        self.assertIsNotNone(multi_agent_result)
        self.assertNotEqual(standard_result, multi_agent_result)


if __name__ == "__main__":
    unittest.main()
