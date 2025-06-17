# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import unittest
import asyncio
from unittest.mock import patch, MagicMock
import json

from src.graph.types import State, Command
from src.graph.nodes import multi_agent_expert_node
from src.graph.graph import Graph
from src.graph.builder import build_graph
from src.agents.multi_agent_coordinator import MultiAgentCoordinator, CollaborationTurn, CollaborationSession
from src.agents.expert_agents import ExpertProfile


class TestMultiAgentExpertNode(unittest.TestCase):
    """Test the multi-agent expert node functionality in the graph."""
    
    def setUp(self):
        """Set up the test environment."""
        self.test_topic = "quantum computing applications"
        
        # Mock state with current plan
        self.mock_state = {
            "user_input": f"Research on {self.test_topic}",
            "enable_multi_agent_experts": True,
            "locale": "en-US",
            "messages": [],
            "observations": []
        }
        
        # Mock plan structure
        self.mock_plan = MagicMock()
        self.mock_step = MagicMock()
        self.mock_step.title = self.test_topic
        self.mock_step.description = f"Research and analyze {self.test_topic}"
        self.mock_step.execution_res = None
        self.mock_plan.steps = [self.mock_step]
        self.mock_state["current_plan"] = self.mock_plan

    @patch('src.graph.nodes.MultiAgentCoordinator')
    async def test_multi_agent_node_execution(self, mock_coordinator_class):
        """Test execution of the multi-agent expert node."""
        # Setup mock coordinator
        mock_coordinator = MagicMock()
        mock_coordinator_class.return_value = mock_coordinator
        mock_coordinator.start_collaboration.return_value = "test_session_id"
        
        mock_turns = [
            CollaborationTurn(
                expert_name="Research Analyst",
                expert_role="Research Expert",
                content="Research insight on quantum computing",
                turn_type="response",
                timestamp="2023-01-01"
            ),
            CollaborationTurn(
                expert_name="Technical Architect",
                expert_role="Technical Expert",
                content="Technical insight on quantum computing",
                turn_type="response",
                timestamp="2023-01-01"
            )
        ]
        mock_coordinator.run_collaboration_round.return_value = mock_turns
        
        mock_coordinator.get_collaboration_summary.return_value = "Synthesized expert analysis"
        mock_coordinator.get_expert_perspectives.return_value = {
            "Research Analyst": "Research perspective",
            "Technical Architect": "Technical perspective"
        }
        
        # Run node
        state = State(**self.mock_state)
        config = {}
        result = await multi_agent_expert_node(state, config)
        
        # Verify coordinator was initialized and used correctly
        mock_coordinator_class.assert_called_once()
        mock_coordinator.start_collaboration.assert_called_once()
        mock_coordinator.run_collaboration_round.assert_called()
        mock_coordinator.get_collaboration_summary.assert_called_once()
        mock_coordinator.get_expert_perspectives.assert_called_once()
        
        # Verify result is a Command to go to research_team
        self.assertIsInstance(result, Command)
        self.assertEqual(result.goto, "research_team")
        
        # Verify state was updated with expert analysis
        update = result.update if hasattr(result, 'update') else {}
        self.assertIn("messages", update)
        self.assertIn("observations", update)
        
        # Verify the step execution result was updated
        self.assertIsNotNone(self.mock_step.execution_res)
        self.assertIn("Synthesized expert analysis", self.mock_step.execution_res)

    @patch('src.graph.nodes.MultiAgentCoordinator')
    async def test_multi_agent_node_error_handling(self, mock_coordinator_class):
        """Test error handling in the multi-agent expert node."""
        # Setup mock coordinator to raise exception
        mock_coordinator_class.side_effect = Exception("Test error")
        
        # Run node
        state = State(**self.mock_state)
        config = {}
        result = await multi_agent_expert_node(state, config)
        
        # Verify graceful fallback to research_team
        self.assertIsInstance(result, Command)
        self.assertEqual(result.goto, "research_team")
        
        # Step execution result should not be set
        self.assertIsNone(self.mock_step.execution_res)

    @patch('src.graph.builder._determine_route')
    def test_graph_routing_with_multi_agent(self, mock_determine_route):
        """Test that the graph is built with multi-agent routing when enabled."""
        # Setup mock route determination
        mock_determine_route.return_value = "multi_agent_experts"
        
        # Build graph with multi-agent enabled
        state = State(
            user_input=f"Research on {self.test_topic}",
            enable_multi_agent_experts=True
        )
        graph = build_graph(state)
        
        # Verify graph structure
        self.assertIn("multi_agent_experts", graph.nodes)
        
        # Use asyncio to run the routing logic
        async def test_routing():
            result = await graph.run("intent", state, {})
            return result
        
        result = asyncio.run(test_routing())
        
        # Verify routing
        mock_determine_route.assert_called_once()
        self.assertEqual(result.goto, "multi_agent_experts")

    @patch('src.graph.builder._determine_route')
    def test_graph_routing_without_multi_agent(self, mock_determine_route):
        """Test that the graph bypasses multi-agent routing when disabled."""
        # Setup mock route determination to go directly to research_team
        mock_determine_route.return_value = "research_team"
        
        # Build graph with multi-agent disabled
        state = State(
            user_input=f"Research on {self.test_topic}",
            enable_multi_agent_experts=False
        )
        graph = build_graph(state)
        
        # Verify graph structure still includes the node
        self.assertIn("multi_agent_experts", graph.nodes)
        
        # Use asyncio to run the routing logic
        async def test_routing():
            result = await graph.run("intent", state, {})
            return result
        
        result = asyncio.run(test_routing())
        
        # Verify routing bypasses multi-agent
        mock_determine_route.assert_called_once()
        self.assertEqual(result.goto, "research_team")


if __name__ == "__main__":
    unittest.main()
