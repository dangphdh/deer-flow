# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import unittest
import sys
import os

class TestMultiAgentStructure(unittest.TestCase):
    """Test that multi-agent expert components are properly structured."""

    def test_modules_exist(self):
        """Test that required multi-agent modules exist."""
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        src_dir = os.path.join(project_root, 'src')
        
        # Check that files exist
        multi_agent_files = [
            os.path.join(src_dir, 'agents', 'expert_agents.py'),
            os.path.join(src_dir, 'agents', 'multi_agent_coordinator.py'),
            os.path.join(src_dir, 'config', 'multi_agent.py'),
        ]
        
        for file_path in multi_agent_files:
            self.assertTrue(os.path.exists(file_path), f"File {file_path} should exist")
    
    def test_documentation_exists(self):
        """Test that multi-agent documentation exists."""
        # Get the project root directory
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        docs_path = os.path.join(project_root, 'docs')
        
        # Check if documentation exists
        multi_agent_docs = os.path.join(docs_path, 'multi_agent_experts.md')
        self.assertTrue(os.path.exists(multi_agent_docs), "Multi-agent documentation should exist")


if __name__ == '__main__':
    unittest.main()
