# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import unittest
from unittest.mock import patch, MagicMock
import asyncio
from typing import List, Dict

from src.agents.multi_agent_coordinator import MultiAgentCoordinator, CollaborationTurn, CollaborationSession
from src.agents.expert_agents import ExpertAgent, ExpertProfile


class MockExpertAgent(ExpertAgent):
    """Mock expert for testing purposes."""
    
    def __init__(self, profile: ExpertProfile, responses: List[str], questions: List[str]):
        super().__init__(profile)
        self.responses = responses
        self.questions = questions
        self.response_index = 0
        self.question_index = 0
        
    def generate_response(self, topic: str, context: str, previous_responses: List[str]) -> str:
        """Return next mock response."""
        if self.response_index < len(self.responses):
            response = self.responses[self.response_index]
            self.response_index += 1
            return response
        return "Default response from " + self.profile.name
        
    def ask_follow_up_question(self, topic: str, current_discussion: str) -> str:
        """Return next mock question."""
        if self.question_index < len(self.questions):
            question = self.questions[self.question_index]
            self.question_index += 1
            return question
        return None


class TestMultiAgentCoordinator(unittest.TestCase):
    """Tests for MultiAgentCoordinator functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create mock expert profiles
        self.profiles = {
            "research": ExpertProfile(
                name="Research Analyst",
                role_description="Research Specialist",
                domain_expertise="academic research",
                perspective="data-driven analysis",
                tools=["web_search"]
            ),
            "technical": ExpertProfile(
                name="Technical Architect",
                role_description="Technical Expert",
                domain_expertise="technical implementation",
                perspective="implementation feasibility",
                tools=["python_repl"]
            ),
            "domain": ExpertProfile(
                name="Domain Expert",
                role_description="Specialized Domain Expert",
                domain_expertise="specific field knowledge",
                perspective="domain-specific insights",
                tools=["web_search"]
            )
        }
        
        # Configure mock responses
        self.mock_responses = {
            "research": [
                "Based on academic research, the topic shows significant trends...",
                "Further analysis indicates that methodological approaches vary..."
            ],
            "technical": [
                "From a technical perspective, implementation would require...",
                "Architectural considerations suggest that scaling would need..."
            ],
            "domain": [
                "As a domain expert, I can confirm that industry practices...",
                "The specialized knowledge in this field points to..."
            ]
        }
        
        # Configure mock questions
        self.mock_questions = {
            "research": [
                "What empirical evidence supports these claims?",
                "How do methodological differences affect outcomes?"
            ],
            "technical": [
                "What technical constraints would limit implementation?",
                "Which architectural patterns would optimize performance?"
            ],
            "domain": [
                "How do industry standards compare to theoretical models?",
                "What specialized approaches have proven effective?"
            ]
        }

    def create_mock_experts(self) -> Dict[str, MockExpertAgent]:
        """Create mock expert agents."""
        experts = {}
        for expert_type, profile in self.profiles.items():
            experts[expert_type] = MockExpertAgent(
                profile,
                self.mock_responses[expert_type],
                self.mock_questions[expert_type]
            )
        return experts

    def test_session_creation(self):
        """Test creating a new collaboration session."""
        coordinator = MultiAgentCoordinator(max_experts=3)
        
        # Use patch to mock the expert creation
        with patch('src.agents.expert_agents.create_expert_agent') as mock_create_expert:
            # Configure mock experts
            mock_experts = list(self.create_mock_experts().values())
            mock_create_expert.side_effect = mock_experts
            
            # Create session
            session_id = coordinator.start_collaboration(
                topic="test topic",
                context="test context",
                expert_types=["research_analyst", "technical_architect", "domain_expert"]
            )
            
            # Verify session was created correctly
            self.assertIn(session_id, coordinator.sessions)
            session = coordinator.sessions[session_id]
            
            self.assertEqual(session.topic, "test topic")
            self.assertEqual(len(session.experts), 3)
            self.assertEqual(session.current_context, "test context")
            self.assertEqual(len(session.conversation_history), 0)

    def test_collaboration_round(self):
        """Test running a collaboration round."""
        coordinator = MultiAgentCoordinator(max_experts=3)
        
        # Setup mock experts and create session
        mock_experts = list(self.create_mock_experts().values())
        
        # Create session manually to control experts
        session_id = "test_session"
        coordinator.sessions[session_id] = CollaborationSession(
            topic="test topic",
            experts=mock_experts,
            conversation_history=[],
            current_context="test context"
        )
        
        # Run collaboration round
        turns = coordinator.run_collaboration_round(session_id)
        
        # Verify turns
        self.assertEqual(len(turns), len(mock_experts))
        for i, turn in enumerate(turns):
            self.assertEqual(turn.turn_type, "response")
            self.assertEqual(turn.content, mock_experts[i].responses[0])

    def test_synthesis_generation(self):
        """Test generating a synthesis of expert perspectives."""
        coordinator = MultiAgentCoordinator(max_experts=3)
        
        # Setup mock collaboration session with conversation history
        session_id = "test_session"
        mock_experts = list(self.create_mock_experts().values())
        
        # Create session with pre-populated conversation history
        session = CollaborationSession(
            topic="test topic",
            experts=mock_experts,
            conversation_history=[
                CollaborationTurn(
                    expert_name=expert.profile.name,
                    expert_role=expert.profile.role_description,
                    content=expert.responses[0],
                    turn_type="response",
                    timestamp="2023-01-01",
                )
                for expert in mock_experts
            ],
            current_context="test context"
        )
        coordinator.sessions[session_id] = session
        
        # Mock LLM for synthesis
        with patch('src.llms.llm.get_llm_by_type') as mock_llm:
            mock_llm_instance = MagicMock()
            mock_llm.return_value = mock_llm_instance
            mock_response = MagicMock()
            mock_response.content = "Synthesized collaboration result"
            mock_llm_instance.invoke.return_value = mock_response
            
            # Generate synthesis
            synthesis = coordinator.get_collaboration_summary(session_id)
            
            # Verify synthesis
            self.assertEqual(synthesis, "Synthesized collaboration result")
            mock_llm_instance.invoke.assert_called_once()

    def test_expert_perspectives(self):
        """Test extracting expert perspectives."""
        coordinator = MultiAgentCoordinator(max_experts=3)
        
        # Setup mock collaboration session with conversation history
        session_id = "test_session"
        mock_experts = list(self.create_mock_experts().values())
        
        # Create conversation turns for each expert
        turns = []
        for expert in mock_experts:
            for response in expert.responses:
                turns.append(
                    CollaborationTurn(
                        expert_name=expert.profile.name,
                        expert_role=expert.profile.role_description,
                        content=response,
                        turn_type="response",
                        timestamp="2023-01-01",
                    )
                )
        
        # Create session
        session = CollaborationSession(
            topic="test topic",
            experts=mock_experts,
            conversation_history=turns,
            current_context="test context"
        )
        coordinator.sessions[session_id] = session
        
        # Get perspectives
        perspectives = coordinator.get_expert_perspectives(session_id)
        
        # Verify perspectives
        self.assertEqual(len(perspectives), len(mock_experts))
        for expert in mock_experts:
            expert_name = expert.profile.name
            self.assertIn(expert_name, perspectives)
            
            # Should combine all responses from the expert
            for response in expert.responses:
                self.assertIn(response, perspectives[expert_name])

    def test_dynamic_topic_handling(self):
        """Test coordinator handling of different topics."""
        coordinator = MultiAgentCoordinator(max_experts=3)
        
        topics = [
            "artificial intelligence ethics",
            "sustainable architecture",
            "quantum computing applications"
        ]
        
        with patch('src.agents.expert_agents.generate_dynamic_experts') as mock_generate:
            # Generate one expert per topic
            for topic in topics:
                mock_generate.return_value = [
                    self.profiles["domain"]
                ]
                
                session_id = coordinator.start_collaboration(
                    topic=topic,
                    context=f"Analysis of {topic}"
                )
                
                # Verify topic was set correctly
                self.assertEqual(coordinator.sessions[session_id].topic, topic)
                
                # Verify dynamic expert generation was called with topic
                mock_generate.assert_called_with(topic, coordinator.max_experts)


if __name__ == "__main__":
    unittest.main()
