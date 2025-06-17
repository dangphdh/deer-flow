import unittest
import os

class TestMultiAgentFiles(unittest.TestCase):
    def test_key_files_exist(self):
        """Test that key multi-agent files exist in the project."""
        project_dir = "/media/dangpdh/Mydisk/Dang/Project/AI search/deer-flow"
        
        expected_files = [
            os.path.join(project_dir, "src/agents/expert_agents.py"),
            os.path.join(project_dir, "src/agents/multi_agent_coordinator.py"),
            os.path.join(project_dir, "src/config/multi_agent.py"),
            os.path.join(project_dir, "docs/multi_agent_experts.md"),
            os.path.join(project_dir, "examples/multi_agent_demo.py")
        ]
        
        for file_path in expected_files:
            exists = os.path.isfile(file_path)
            self.assertTrue(exists, f"Expected file {file_path} should exist")

if __name__ == "__main__":
    unittest.main()
