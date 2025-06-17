# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from langchain_core.messages import HumanMessage, AIMessage

from src.llms.llm import get_llm_by_type
from src.agents import create_agent
from src.tools import get_web_search_tool, crawl_tool, python_repl_tool
from src.graph.types import State


@dataclass
class ExpertProfile:
    """Profile for an expert agent with specific domain knowledge."""
    name: str
    role_description: str
    domain_expertise: str
    perspective: str
    tools: List[str]  # Tools this expert specializes in


class ExpertAgent(ABC):
    """Base class for expert agents in the multi-agent system."""
    
    def __init__(self, profile: ExpertProfile, llm_type: str = "basic"):
        self.profile = profile
        self.llm_type = llm_type
        self.conversation_history: List[Dict[str, Any]] = []
        
    @abstractmethod
    def generate_response(self, topic: str, context: str, previous_responses: List[str]) -> str:
        """Generate a response based on the expert's domain knowledge."""
        pass
        
    @abstractmethod
    def ask_follow_up_question(self, topic: str, current_discussion: str) -> Optional[str]:
        """Generate a follow-up question based on the expert's perspective."""
        pass


class ResearchExpert(ExpertAgent):
    """Expert specialized in research and information gathering."""
    
    def __init__(self, profile: ExpertProfile):
        super().__init__(profile, "basic")
        self.tools = [get_web_search_tool(max_results=5), crawl_tool]
        
    def generate_response(self, topic: str, context: str, previous_responses: List[str]) -> str:
        """Generate research-focused response with citations."""
        prompt = f"""As a {self.profile.role_description}, provide insights on: {topic}

            Context: {context}

            Previous expert responses:
            {chr(10).join(previous_responses)}

            Your perspective: {self.profile.perspective}
            Domain expertise: {self.profile.domain_expertise}

            Provide a research-backed response with specific insights from your domain. Focus on:
            1. Evidence-based analysis
            2. Key research findings
            3. Methodological considerations
            4. Gaps in current knowledge

            Response:"""

        llm = get_llm_by_type(self.llm_type)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
        
    def ask_follow_up_question(self, topic: str, current_discussion: str) -> Optional[str]:
        """Generate research-focused follow-up questions."""
        prompt = f"""Based on the current discussion about {topic}, what important research question should we explore next?

        Current discussion:
        {current_discussion}

        As a {self.profile.role_description}, suggest ONE specific, actionable research question that would advance our understanding. Focus on your expertise in {self.profile.domain_expertise}.

        Question:"""

        llm = get_llm_by_type(self.llm_type)
        response = llm.invoke([HumanMessage(content=prompt)])
        question = response.content.strip()
        return question if question and len(question) > 10 else None


class TechnicalExpert(ExpertAgent):
    """Expert specialized in technical analysis and implementation."""
    
    def __init__(self, profile: ExpertProfile):
        super().__init__(profile, "basic")
        self.tools = [python_repl_tool]
        
    def generate_response(self, topic: str, context: str, previous_responses: List[str]) -> str:
        """Generate technical analysis and implementation insights."""
        prompt = f"""As a {self.profile.role_description}, provide technical analysis for: {topic}

        Context: {context}

        Previous expert responses:
        {chr(10).join(previous_responses)}

        Your technical perspective: {self.profile.perspective}
        Domain expertise: {self.profile.domain_expertise}

        Provide technical insights focusing on:
        1. Implementation feasibility
        2. Technical challenges and solutions
        3. Best practices and standards
        4. Performance and scalability considerations

        Response:"""

        llm = get_llm_by_type(self.llm_type)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
        
    def ask_follow_up_question(self, topic: str, current_discussion: str) -> Optional[str]:
        """Generate technical follow-up questions."""
        prompt = f"""Based on the technical discussion about {topic}, what critical technical question needs addressing?

        Current discussion:
        {current_discussion}

        As a {self.profile.role_description}, suggest ONE specific technical question that would help clarify implementation details or identify potential issues. Focus on {self.profile.domain_expertise}.

        Question:"""

        llm = get_llm_by_type(self.llm_type)
        response = llm.invoke([HumanMessage(content=prompt)])
        question = response.content.strip()
        return question if question and len(question) > 10 else None


class DomainExpert(ExpertAgent):
    """Expert specialized in specific domain knowledge."""
    
    def __init__(self, profile: ExpertProfile):
        super().__init__(profile, "basic")
        
    def generate_response(self, topic: str, context: str, previous_responses: List[str]) -> str:
        """Generate domain-specific insights."""
        prompt = f"""As a {self.profile.role_description}, provide domain expertise on: {topic}

        Context: {context}

        Previous expert responses:
        {chr(10).join(previous_responses)}

        Your domain perspective: {self.profile.perspective}
        Specialized knowledge: {self.profile.domain_expertise}

        Provide insights focusing on:
        1. Domain-specific considerations
        2. Industry best practices
        3. Regulatory or compliance aspects
        4. Real-world applications and implications

        Response:"""

        llm = get_llm_by_type(self.llm_type)
        response = llm.invoke([HumanMessage(content=prompt)])
        return response.content
        
    def ask_follow_up_question(self, topic: str, current_discussion: str) -> Optional[str]:
        """Generate domain-specific follow-up questions."""
        prompt = f"""Given the discussion about {topic}, what important domain-specific question should we explore?

        Current discussion:
        {current_discussion}

        As a {self.profile.role_description}, suggest ONE specific question that addresses domain-specific concerns, regulations, or practical applications in {self.profile.domain_expertise}.

        Question:"""

        llm = get_llm_by_type(self.llm_type)
        response = llm.invoke([HumanMessage(content=prompt)])
        question = response.content.strip()
        return question if question and len(question) > 10 else None


# Predefined expert profiles for common domains
EXPERT_PROFILES = {
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
    "ai_specialist": ExpertProfile(
        name="AI/ML Specialist",
        role_description="AI/ML Domain Expert",
        domain_expertise="Machine learning, deep learning, AI ethics, model deployment",
        perspective="AI/ML implementation and ethical considerations",
        tools=["python_repl", "web_search"]
    ),
    "business_analyst": ExpertProfile(
        name="Business Analyst",
        role_description="Senior Business Analyst",
        domain_expertise="Business strategy, market analysis, ROI assessment",
        perspective="Business value and strategic implications",
        tools=["web_search", "crawl"]
    ),
    "security_expert": ExpertProfile(
        name="Security Expert",
        role_description="Cybersecurity Specialist",
        domain_expertise="Information security, privacy, compliance, risk assessment",
        perspective="Security and privacy implications",
        tools=["web_search"]
    )
}


def create_expert_agent(expert_type: str, custom_profile: Optional[ExpertProfile] = None) -> ExpertAgent:
    """Factory function to create expert agents."""
    profile = custom_profile or EXPERT_PROFILES.get(expert_type)
    if not profile:
        raise ValueError(f"Unknown expert type: {expert_type}")
        
    if "research" in expert_type.lower() or "analyst" in expert_type.lower():
        return ResearchExpert(profile)
    elif "technical" in expert_type.lower() or "architect" in expert_type.lower():
        return TechnicalExpert(profile)
    else:
        return DomainExpert(profile)


def generate_dynamic_experts(topic: str, num_experts: int = 3) -> List[ExpertProfile]:
    """Generate expert profiles dynamically based on the research topic."""
    prompt = f"""Generate {num_experts} expert profiles for researching the topic: "{topic}"

For each expert, provide:
1. Name (role title)
2. Role description (1 sentence)
3. Domain expertise (specific areas of knowledge)
4. Perspective (unique viewpoint they bring)

Format as JSON array with these fields: name, role_description, domain_expertise, perspective, tools

Focus on diverse, complementary expertise that would provide comprehensive coverage of the topic.

Experts:"""

    llm = get_llm_by_type("reasoning")
    response = llm.invoke([HumanMessage(content=prompt)])
    
    try:
        import json
        experts_data = json.loads(response.content)
        profiles = []
        for expert in experts_data:
            profile = ExpertProfile(
                name=expert.get("name", "Expert"),
                role_description=expert.get("role_description", "Domain Expert"),
                domain_expertise=expert.get("domain_expertise", "General knowledge"),
                perspective=expert.get("perspective", "Balanced perspective"),
                tools=expert.get("tools", ["web_search"])
            )
            profiles.append(profile)
        return profiles
    except (json.JSONDecodeError, KeyError):
        # Fallback to default experts
        return [
            EXPERT_PROFILES["research_analyst"],
            EXPERT_PROFILES["technical_architect"],
            EXPERT_PROFILES["ai_specialist"]
        ]
