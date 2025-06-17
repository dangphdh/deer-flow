# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from src.prompts.planner_model import StepType

from .types import State
from .nodes import (
    coordinator_node,
    planner_node,
    reporter_node,
    research_team_node,
    researcher_node,
    coder_node,
    multi_agent_expert_node,
    human_feedback_node,
    background_investigation_node,
)


def continue_to_running_research_team(state: State):
    current_plan = state.get("current_plan")
    if not current_plan or not current_plan.steps:
        return "planner"
    if all(step.execution_res for step in current_plan.steps):
        return "planner"
    for step in current_plan.steps:
        if not step.execution_res:
            break
    
    # Check if multi-agent collaboration is enabled and beneficial for this step
    enable_multi_agent = state.get("enable_multi_agent_experts", False)
    if enable_multi_agent and _should_use_multi_agent(step):
        return "multi_agent_experts"
    
    if step.step_type and step.step_type == StepType.RESEARCH:
        return "researcher"
    if step.step_type and step.step_type == StepType.PROCESSING:
        return "coder"
    return "planner"


def _should_use_multi_agent(step):
    """Determine if multi-agent experts should be used for this step."""
    # Example logic: use multi-agent for research or complex steps
    keywords = ["collaborative", "multi-agent", "panel", "expert", "comprehensive", "debate", "discussion"]
    if hasattr(step, "title") and any(k in step.title.lower() for k in keywords):
        return True
    if hasattr(step, "description") and any(k in step.description.lower() for k in keywords):
        return True
    # Optionally, use for all RESEARCH steps
    from src.prompts.planner_model import StepType
    if hasattr(step, "step_type") and step.step_type == StepType.RESEARCH:
        return True
    return False


def _build_base_graph():
    """Build and return the base state graph with all nodes and edges."""
    builder = StateGraph(State)
    builder.add_edge(START, "coordinator")
    builder.add_node("coordinator", coordinator_node)
    builder.add_node("background_investigator", background_investigation_node)
    builder.add_node("planner", planner_node)
    builder.add_node("reporter", reporter_node)
    builder.add_node("research_team", research_team_node)
    builder.add_node("researcher", researcher_node)
    builder.add_node("coder", coder_node)
    builder.add_node("multi_agent_experts", multi_agent_expert_node)
    builder.add_node("human_feedback", human_feedback_node)
    builder.add_edge("background_investigator", "planner")
    builder.add_conditional_edges(
        "research_team",
        continue_to_running_research_team,
        ["planner", "researcher", "coder", "multi_agent_experts"],
    )
    builder.add_edge("reporter", END)
    return builder


def build_graph_with_memory():
    """Build and return the agent workflow graph with memory."""
    # use persistent memory to save conversation history
    # TODO: be compatible with SQLite / PostgreSQL
    
    memory = MemorySaver()

    # build state graph
    builder = _build_base_graph()
    return builder.compile(checkpointer=memory)


def build_graph():
    """Build and return the agent workflow graph without memory."""
    # build state graph
    builder = _build_base_graph()
    return builder.compile()


graph = build_graph()
