import unittest
import os
import re

class TestMultiAgentImplementation(unittest.TestCase):
    """Test the multi-agent expert integration in the deer-flow project."""
    
    def setUp(self):
        """Set up the test environment."""
        self.project_dir = "/media/dangpdh/Mydisk/Dang/Project/AI search/deer-flow"
        
        # Key file paths
        self.expert_agents_path = os.path.join(self.project_dir, "src/agents/expert_agents.py")
        self.coordinator_path = os.path.join(self.project_dir, "src/config/multi_agent.py")
        self.nodes_path = os.path.join(self.project_dir, "src/graph/nodes.py")
        self.workflow_path = os.path.join(self.project_dir, "src/workflow.py")
        self.docs_path = os.path.join(self.project_dir, "docs/multi_agent_experts.md")
    
    def test_key_files_exist(self):
        """Test that all required multi-agent files exist."""
        key_files = [
            self.expert_agents_path,
            self.coordinator_path, 
            self.nodes_path,
            self.workflow_path,
            self.docs_path,
            os.path.join(self.project_dir, "examples/multi_agent_demo.py"),
            os.path.join(self.project_dir, "tests/integration/test_multi_agent_experts.py")
        ]
        
        for file_path in key_files:
            self.assertTrue(os.path.isfile(file_path), f"File {file_path} should exist")
    
    def test_expert_agents_implementation(self):
        """Test that expert_agents.py contains the expected classes."""
        with open(self.expert_agents_path, 'r') as f:
            content = f.read()
            
        # Check for key classes
        self.assertIn("class ExpertAgent", content)
        self.assertIn("class ResearchExpert", content)
        self.assertIn("class TechnicalExpert", content)
        self.assertIn("class DomainExpert", content)
        
        # Check for key functions
        self.assertIn("def create_expert_agent", content)
        self.assertIn("def generate_dynamic_experts", content)
        
        # Check for EXPERT_PROFILES dictionary
        self.assertIn("EXPERT_PROFILES", content)
    
    def test_workflow_integration(self):
        """Test that workflow.py has the multi-agent flag."""
        with open(self.workflow_path, 'r') as f:
            content = f.read()
        
        # Check for enable_multi_agent_experts parameter
        self.assertIn("enable_multi_agent_experts", content)
    
    def test_graph_node_implementation(self):
        """Test that nodes.py has multi-agent expert node."""
        with open(self.nodes_path, 'r') as f:
            content = f.read()
        
        # Check for multi-agent node definition
        self.assertIn("def multi_agent_expert_node", content)
    
    def test_documentation_content(self):
        """Test that documentation covers the required topics."""
        with open(self.docs_path, 'r') as f:
            content = f.read()
        
        # Check for key sections
        key_topics = [
            "multi-agent expert",
            "expert",
            "collaboration",
            "research",
            "coordinator"
        ]
        
        for topic in key_topics:
            self.assertIn(topic, content.lower(), f"Documentation should mention {topic}")
            
    def test_demo_usage(self):
        """Test that demo file properly demonstrates the feature."""
        with open(os.path.join(self.project_dir, "examples/multi_agent_demo.py"), 'r') as f:
            content = f.read()
            
        # Check that demo enables multi-agent feature
        self.assertIn("enable_multi_agent_experts=True", content)


if __name__ == "__main__":
    unittest.main()
