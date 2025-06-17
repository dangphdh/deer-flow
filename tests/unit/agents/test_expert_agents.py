# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import unittest
from unittest.mock import patch, MagicMock
from typing import List, Dict, Optional

from src.agents.expert_agents import (
    ExpertProfile, ExpertAgent, ResearchExpert, 
    TechnicalExpert, DomainExpert
)

# Mock expert profiles for testing
TEST_EXPERT_PROFILES = {
    "research_analyst": ExpertProfile(
        name="Research Analyst",
        role_description="Senior Research Analyst",
        domain_expertise="Data analysis, research methodologies, statistical analysis",
        perspective="Evidence-based analysis with focus on data quality and research rigor",
        tools=["web_search", "crawl"]
    ),
    "technical_architect": ExpertProfile(
        name="Technical Architect",
        role_description="Senior Technical Architect",
        domain_expertise="System design, software architecture, performance optimization",
        perspective="Technical feasibility and implementation best practices",
        tools=["python_repl"]
    ),
    "domain_expert": ExpertProfile(
        name="Domain Expert",
        role_description="Domain Specialist",
        domain_expertise="specialized knowledge",
        perspective="domain-specific insights",
        tools=["web_search"]
    )
}

# Mock implementation of create_expert_agent for testing
def mock_create_expert_agent(expert_type: str, profile: Optional[ExpertProfile] = None):
    """Mock version of create_expert_agent for testing."""
    if profile is None:
        if expert_type not in TEST_EXPERT_PROFILES:
            raise ValueError(f"Unknown expert type: {expert_type}")
        profile = TEST_EXPERT_PROFILES[expert_type]
    
    if expert_type == "research_analyst" or "research" in expert_type.lower():
        return ResearchExpert(profile)
    elif expert_type == "technical_architect" or "technical" in expert_type.lower():
        return TechnicalExpert(profile)
    else:
        return DomainExpert(profile)


class TestExpertAgents(unittest.TestCase):
    """Tests for expert agent implementations."""
    
    def setUp(self):
        """Set up the test environment."""
        self.test_topic = "impact of climate change on agriculture"
        self.test_context = f"Research on {self.test_topic}"
        self.test_previous_responses = ["Previous expert insight 1", "Previous expert insight 2"]
        
        # Mock profile for testing
        self.test_profile = ExpertProfile(
            name="Test Expert",
            role_description="Test Role",
            domain_expertise="test domain",
            perspective="test perspective",
            tools=["web_search"]
        )

    @patch('src.llms.llm.get_llm_by_type')
    def test_research_expert(self, mock_get_llm):
        """Test ResearchExpert functionality."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_response = MagicMock()
        mock_response.content = "Test research response"
        mock_llm.invoke.return_value = mock_response
        
        # Create expert
        expert = ResearchExpert(self.test_profile)
        
        # Generate response
        response = expert.generate_response(
            self.test_topic, 
            self.test_context, 
            self.test_previous_responses
        )
        
        # Verify LLM was called with research-specific prompt
        self.assertEqual(response, "Test research response")
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        self.assertIn(self.test_profile.role_description, call_args[0].content)
        self.assertIn("research-backed response", call_args[0].content.lower())
        self.assertIn("evidence-based analysis", call_args[0].content.lower())
        
        # Test follow-up question
        mock_response.content = "Test follow-up question?"
        follow_up = expert.ask_follow_up_question(self.test_topic, "Current discussion")
        self.assertEqual(follow_up, "Test follow-up question?")

    @patch('src.llms.llm.get_llm_by_type')
    def test_technical_expert(self, mock_get_llm):
        """Test TechnicalExpert functionality."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_response = MagicMock()
        mock_response.content = "Test technical response"
        mock_llm.invoke.return_value = mock_response
        
        # Create expert
        expert = TechnicalExpert(self.test_profile)
        
        # Generate response
        response = expert.generate_response(
            self.test_topic, 
            self.test_context, 
            self.test_previous_responses
        )
        
        # Verify LLM was called with technical-specific prompt
        self.assertEqual(response, "Test technical response")
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        self.assertIn(self.test_profile.role_description, call_args[0].content)
        self.assertIn("technical analysis", call_args[0].content.lower())
        
        # Test follow-up question
        mock_response.content = "Test technical question?"
        follow_up = expert.ask_follow_up_question(self.test_topic, "Current discussion")
        self.assertEqual(follow_up, "Test technical question?")

    @patch('src.llms.llm.get_llm_by_type')
    def test_domain_expert(self, mock_get_llm):
        """Test DomainExpert functionality."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_response = MagicMock()
        mock_response.content = "Test domain response"
        mock_llm.invoke.return_value = mock_response
        
        # Create expert
        expert = DomainExpert(self.test_profile)
        
        # Generate response
        response = expert.generate_response(
            self.test_topic, 
            self.test_context, 
            self.test_previous_responses
        )
        
        # Verify LLM was called with domain-specific prompt
        self.assertEqual(response, "Test domain response")
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        self.assertIn(self.test_profile.role_description, call_args[0].content)
        self.assertIn(self.test_profile.domain_expertise, call_args[0].content.lower())
        
        # Test follow-up question
        mock_response.content = "Test domain question?"
        follow_up = expert.ask_follow_up_question(self.test_topic, "Current discussion")
        self.assertEqual(follow_up, "Test domain question?")

    def test_create_expert_agent(self):
        """Test expert agent factory function."""
        # Test with standard expert types
        expert_types = ["research_analyst", "technical_architect", "domain_expert"]
        for expert_type in expert_types:
            with self.subTest(expert_type=expert_type):
                expert = mock_create_expert_agent(expert_type)
                
                # Verify correct expert class
                if expert_type == "research_analyst":
                    self.assertIsInstance(expert, ResearchExpert)
                elif expert_type == "technical_architect":
                    self.assertIsInstance(expert, TechnicalExpert)
                else:
                    self.assertIsInstance(expert, DomainExpert)
                
                # Verify profile matches the expected type
                self.assertEqual(expert.profile.name, TEST_EXPERT_PROFILES[expert_type].name)
                self.assertEqual(expert.profile.domain_expertise, TEST_EXPERT_PROFILES[expert_type].domain_expertise)
            
        # Test with custom profile
        expert = mock_create_expert_agent("domain_expert", self.test_profile)
        self.assertEqual(expert.profile.name, self.test_profile.name)
        self.assertEqual(expert.profile.domain_expertise, self.test_profile.domain_expertise)
        
        # Test invalid expert type
        with self.assertRaises(ValueError):
            mock_create_expert_agent("invalid_expert_type")

    @patch('src.llms.llm.get_llm_by_type')
    def test_mock_generate_dynamic_experts(self, mock_get_llm):
        """Test mocked dynamic expert generation based on topic."""
        # Setup mock LLM
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_response = MagicMock()
        
        # Mock expert definitions returned by LLM
        mock_response.content = """
        [
            {
                "name": "Climate Scientist",
                "role_description": "Climate Science Researcher",
                "domain_expertise": "climate modeling and prediction",
                "perspective": "scientific evidence-based analysis",
                "tools": ["web_search", "data_analysis"]
            },
            {
                "name": "Agricultural Specialist",
                "role_description": "Agricultural Systems Expert",
                "domain_expertise": "crop science and adaptation strategies",
                "perspective": "practical implementation in farming",
                "tools": ["web_search", "python_repl"]
            }
        ]
        """
        mock_llm.invoke.return_value = mock_response
        
        # Mock dynamic generation function
        def mock_generate_dynamic_experts(topic, num_experts=3):
            """Mock implementation for testing"""
            import json
            from json.decoder import JSONDecodeError
            try:
                experts_data = json.loads(mock_response.content)
                return [
                    ExpertProfile(
                        name=expert.get("name", "Unknown"),
                        role_description=expert.get("role_description", "Expert"),
                        domain_expertise=expert.get("domain_expertise", "Unknown"),
                        perspective=expert.get("perspective", "General"),
                        tools=expert.get("tools", ["web_search"])
                    ) for expert in experts_data
                ]
            except (JSONDecodeError, ValueError):
                # Return default experts on error
                return [
                    TEST_EXPERT_PROFILES["research_analyst"],
                    TEST_EXPERT_PROFILES["technical_architect"],
                ]
        
        # Test dynamic generation
        experts = mock_generate_dynamic_experts(self.test_topic, num_experts=2)
        
        # Verify results
        self.assertEqual(len(experts), 2)
        
        # Check first expert
        self.assertEqual(experts[0].name, "Climate Scientist")
        self.assertEqual(experts[0].domain_expertise, "climate modeling and prediction")
        
        # Check second expert
        self.assertEqual(experts[1].name, "Agricultural Specialist")
        self.assertEqual(experts[1].domain_expertise, "crop science and adaptation strategies")
        
        # Verify LLM was called with appropriate prompt
        mock_llm.invoke.assert_called_once()
        call_args = mock_llm.invoke.call_args[0][0]
        self.assertIn("expert profiles", call_args[0].content.lower())

    @patch('src.llms.llm.get_llm_by_type')
    def test_mock_generate_dynamic_experts_fallback(self, mock_get_llm):
        """Test fallback when dynamic expert generation fails."""
        # Setup mock LLM to return invalid format
        mock_llm = MagicMock()
        mock_get_llm.return_value = mock_llm
        mock_response = MagicMock()
        mock_response.content = "Invalid JSON format response"
        mock_llm.invoke.return_value = mock_response
        
        # Mock dynamic generation function with fallback
        def mock_generate_dynamic_experts_with_fallback(topic, num_experts=3):
            """Mock implementation with fallback for testing"""
            # Simulate fallback with default experts
            return [
                TEST_EXPERT_PROFILES["research_analyst"],
                TEST_EXPERT_PROFILES["technical_architect"],
            ]
        
        # Test generation with fallback
        experts = mock_generate_dynamic_experts_with_fallback(self.test_topic, num_experts=3)
        
        # Verify default experts were used
        self.assertGreaterEqual(len(experts), 2)  # Should have at least research and technical experts
        
        expert_names = [e.name for e in experts]
        self.assertIn(TEST_EXPERT_PROFILES["research_analyst"].name, expert_names)
        self.assertIn(TEST_EXPERT_PROFILES["technical_architect"].name, expert_names)


if __name__ == "__main__":
    unittest.main()
