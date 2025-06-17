# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from langchain_core.messages import HumanMessage

from .expert_agents import ExpertAgent, ExpertProfile, create_expert_agent, generate_dynamic_experts
from src.llms.llm import get_llm_by_type

logger = logging.getLogger(__name__)


@dataclass
class CollaborationTurn:
    """Represents a single turn in the multi-agent collaboration."""
    expert_name: str
    expert_role: str
    content: str
    turn_type: str  # "response", "question", "synthesis"
    timestamp: str
    sources: List[str] = None


@dataclass
class CollaborationSession:
    """Manages a multi-agent collaboration session."""
    topic: str
    experts: List[ExpertAgent]
    conversation_history: List[CollaborationTurn]
    current_context: str
    max_turns: int = 15
    synthesis_interval: int = 5  # Synthesize every N turns


class MultiAgentCoordinator:
    """Coordinates collaboration between multiple expert agents."""
    
    def __init__(self, max_experts: int = 4, synthesis_interval: int = 5):
        self.max_experts = max_experts
        self.synthesis_interval = synthesis_interval
        self.sessions: Dict[str, CollaborationSession] = {}
        
    def start_collaboration(
        self, 
        topic: str, 
        context: str = "", 
        expert_types: Optional[List[str]] = None,
        custom_experts: Optional[List[ExpertProfile]] = None
    ) -> str:
        """Start a new multi-agent collaboration session."""
        session_id = f"session_{len(self.sessions)}"
        
        # Generate or use provided experts
        if custom_experts:
            expert_profiles = custom_experts[:self.max_experts]
        elif expert_types:
            expert_profiles = [
                ExpertProfile(
                    name=expert_type.replace("_", " ").title(),
                    role_description=f"{expert_type.replace('_', ' ').title()} Expert",
                    domain_expertise=expert_type,
                    perspective=f"Specialized {expert_type} perspective",
                    tools=["web_search"]
                ) for expert_type in expert_types[:self.max_experts]
            ]
        else:
            expert_profiles = generate_dynamic_experts(topic, self.max_experts)
            
        # Create expert agents
        experts = []
        for i, profile in enumerate(expert_profiles):
            if i == 0:
                expert_type = "research_analyst"
            elif i == 1:
                expert_type = "technical_architect"
            else:
                expert_type = "domain_expert"
            experts.append(create_expert_agent(expert_type, profile))
            
        # Initialize session
        session = CollaborationSession(
            topic=topic,
            experts=experts,
            conversation_history=[],
            current_context=context,
            synthesis_interval=self.synthesis_interval
        )
        
        self.sessions[session_id] = session
        logger.info(f"Started collaboration session {session_id} with {len(experts)} experts")
        
        return session_id
        
    def run_collaboration_round(self, session_id: str) -> List[CollaborationTurn]:
        """Run one round of collaboration with all experts."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        round_turns = []
        current_responses = []
        
        # Get responses from all experts
        for expert in session.experts:
            try:
                # Collect previous responses from this round
                previous_responses = [turn.content for turn in session.conversation_history[-3:]]
                
                # Generate expert response
                response = expert.generate_response(
                    topic=session.topic,
                    context=session.current_context,
                    previous_responses=previous_responses
                )
                
                turn = CollaborationTurn(
                    expert_name=expert.profile.name,
                    expert_role=expert.profile.role_description,
                    content=response,
                    turn_type="response",
                    timestamp=self._get_timestamp()
                )
                
                round_turns.append(turn)
                current_responses.append(response)
                session.conversation_history.append(turn)
                
                logger.debug(f"Expert {expert.profile.name} contributed: {response[:100]}...")
                
            except Exception as e:
                logger.error(f"Error getting response from expert {expert.profile.name}: {e}")
                
        # Generate follow-up questions
        self._generate_follow_up_questions(session, round_turns)
        
        # Synthesize if needed
        if len(session.conversation_history) % session.synthesis_interval == 0:
            synthesis = self._synthesize_discussion(session)
            if synthesis:
                synthesis_turn = CollaborationTurn(
                    expert_name="Synthesizer",
                    expert_role="Discussion Synthesizer",
                    content=synthesis,
                    turn_type="synthesis",
                    timestamp=self._get_timestamp()
                )
                round_turns.append(synthesis_turn)
                session.conversation_history.append(synthesis_turn)
                
        return round_turns
        
    def _generate_follow_up_questions(self, session: CollaborationSession, recent_turns: List[CollaborationTurn]):
        """Generate follow-up questions from experts."""
        current_discussion = "\n\n".join([
            f"{turn.expert_name}: {turn.content}" for turn in recent_turns
        ])
        
        for expert in session.experts:
            try:
                question = expert.ask_follow_up_question(session.topic, current_discussion)
                if question:
                    question_turn = CollaborationTurn(
                        expert_name=expert.profile.name,
                        expert_role=expert.profile.role_description,
                        content=question,
                        turn_type="question",
                        timestamp=self._get_timestamp()
                    )
                    session.conversation_history.append(question_turn)
                    
            except Exception as e:
                logger.error(f"Error generating question from expert {expert.profile.name}: {e}")
                
    def _synthesize_discussion(self, session: CollaborationSession) -> Optional[str]:
        """Synthesize the recent discussion into key insights."""
        recent_discussion = "\n\n".join([
            f"{turn.expert_name} ({turn.turn_type}): {turn.content}" 
            for turn in session.conversation_history[-session.synthesis_interval:]
        ])
        
        prompt = f"""Synthesize the following expert discussion about "{session.topic}":

{recent_discussion}

Provide a concise synthesis that:
1. Identifies key agreements and disagreements
2. Highlights the most important insights
3. Notes any gaps that need further exploration
4. Suggests next steps for investigation

Synthesis:"""

        try:
            llm = get_llm_by_type("reasoning")
            response = llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except Exception as e:
            logger.error(f"Error synthesizing discussion: {e}")
            return None
            
    def get_collaboration_summary(self, session_id: str) -> str:
        """Get a comprehensive summary of the collaboration session."""
        session = self.sessions.get(session_id)
        if not session:
            return "Session not found"
            
        # Separate different types of contributions
        responses = [turn for turn in session.conversation_history if turn.turn_type == "response"]
        questions = [turn for turn in session.conversation_history if turn.turn_type == "question"]
        syntheses = [turn for turn in session.conversation_history if turn.turn_type == "synthesis"]
        
        summary = f"""# Multi-Agent Collaboration Summary: {session.topic}

## Participating Experts
{chr(10).join([f"- {expert.profile.name}: {expert.profile.role_description}" for expert in session.experts])}

## Key Insights ({len(responses)} expert responses)
"""
        
        # Add expert contributions
        for i, response in enumerate(responses):
            summary += f"\n### Insight {i+1}: {response.expert_name}\n{response.content}\n"
            
        # Add important questions
        if questions:
            summary += f"\n## Critical Questions Raised ({len(questions)} questions)\n"
            for i, question in enumerate(questions[-5:]):  # Last 5 questions
                summary += f"\n{i+1}. **{question.expert_name}**: {question.content}\n"
                
        # Add syntheses
        if syntheses:
            summary += f"\n## Discussion Syntheses\n"
            for synthesis in syntheses:
                summary += f"\n{synthesis.content}\n\n---\n"
                
        return summary
        
    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime
        return datetime.now().isoformat()
        
    def get_expert_perspectives(self, session_id: str) -> Dict[str, str]:
        """Get individual expert perspectives on the topic."""
        session = self.sessions.get(session_id)
        if not session:
            return {}
            
        perspectives = {}
        for expert in session.experts:
            expert_responses = [
                turn.content for turn in session.conversation_history 
                if turn.expert_name == expert.profile.name and turn.turn_type == "response"
            ]
            if expert_responses:
                perspectives[expert.profile.name] = {
                    "role": expert.profile.role_description,
                    "expertise": expert.profile.domain_expertise,
                    "perspective": expert.profile.perspective,
                    "contributions": expert_responses
                }
                
        return perspectives
        
    def extend_collaboration(self, session_id: str, additional_context: str) -> List[CollaborationTurn]:
        """Extend an existing collaboration with new context."""
        session = self.sessions.get(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")
            
        # Add new context
        session.current_context += f"\n\nAdditional Context:\n{additional_context}"
        
        # Run another collaboration round
        return self.run_collaboration_round(session_id)
