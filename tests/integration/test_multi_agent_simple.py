# Integration test for multi-agent feature

import unittest
import asyncio
from unittest.mock import patch, MagicMock

# Simple test to verify multi-agent workflow integration
class TestMultiAgentIntegration(unittest.TestCase):
    """Test that multi-agent feature gets activated correctly when enabled."""

    @patch('src.workflow.build_graph')
    async def test_multi_agent_flag_passed_to_graph(self, mock_build_graph):
        """Test that the multi-agent flag is correctly passed to the graph."""
        from src.workflow import run_agent_workflow_async
        
        # Set up mock
        mock_graph = MagicMock()
        mock_build_graph.return_value = mock_graph
        mock_graph.run.return_value = MagicMock(goto=None)
        
        # Run with multi-agent enabled
        await run_agent_workflow_async(
            user_input="Test query",
            enable_multi_agent_experts=True,
            max_plan_iterations=1
        )
        
        # Verify that build_graph was called with enable_multi_agent_experts=True in state
        build_graph_call = mock_build_graph.call_args[0][0]
        self.assertTrue(build_graph_call.get("enable_multi_agent_experts", False))
        
        # Reset mock
        mock_build_graph.reset_mock()
        
        # Run with multi-agent disabled
        await run_agent_workflow_async(
            user_input="Test query",
            enable_multi_agent_experts=False,
            max_plan_iterations=1
        )
        
        # Verify that build_graph was called with enable_multi_agent_experts=False in state
        build_graph_call = mock_build_graph.call_args[0][0]
        self.assertFalse(build_graph_call.get("enable_multi_agent_experts", True))


def run_tests():
    test_loader = unittest.TestLoader()
    test_suite = test_loader.loadTestsFromTestCase(TestMultiAgentIntegration)
    test_runner = unittest.TextTestRunner(verbosity=2)
    test_runner.run(test_suite)

if __name__ == "__main__":
    asyncio.run(unittest.main())
