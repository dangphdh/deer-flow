# Multi-Agent Expert Collaboration

This documentation explains the multi-agent expert collaboration feature in Deer Flow, which enables multiple specialized AI agents to work together on complex research and analysis tasks.

## Overview

The multi-agent expert collaboration system brings together diverse specialized AI agents to collaboratively tackle complex research topics. Inspired by STORM (Synthesis of Topic Outlines through Retrieval and Multi-perspective Question Asking), this system simulates an expert panel discussion with each agent bringing unique domain expertise and perspective.

## Key Components

1. **Expert Agents**: Specialized agents with defined expertise domains and perspectives
   - Research Analysts
   - Technical Architects
   - Domain Specialists
   - Business Analysts
   - Security Experts
   - AI/ML Specialists

2. **Multi-Agent Coordinator**: Orchestrates collaboration between expert agents
   - Manages turn-taking
   - Synthesizes insights
   - Ensures comprehensive coverage

3. **Collaborative Protocol**: Structured approach to expert collaboration
   - Multi-round discussions
   - Follow-up questioning
   - Periodic synthesis

## Use Cases

The multi-agent expert system is particularly valuable for:

- **Complex Research Topics**: Requiring diverse viewpoints and expertise
- **Interdisciplinary Analysis**: Combining insights from multiple domains
- **Decision Support**: Analyzing options from multiple perspectives
- **Comprehensive Exploration**: Deep investigation of multifaceted topics
- **Identifying Gaps**: Revealing blind spots in analysis

## How It Works

1. The system dynamically selects relevant expert types based on the research topic
2. Experts take turns providing insights from their specialized perspectives
3. Experts ask follow-up questions to deepen the investigation
4. The coordinator periodically synthesizes insights into a coherent analysis
5. The final output combines individual expert contributions with synthesis

## Configuration

Multi-agent experts can be enabled and configured in `config/multi_agent.py`:

```python
@dataclass
class MultiAgentExpertConfig:
    enabled: bool = True                 # Enable/disable functionality
    max_experts: int = 4                 # Maximum experts per collaboration
    max_rounds: int = 3                  # Collaboration rounds
    synthesis_interval: int = 3          # Turns before synthesis
    max_insights: int = 12               # Maximum insights before stopping
    default_expert_types: List[str]      # Expert types to include
    coordinator_llm_type: str = "reasoning"  # LLM for coordination
    dynamic_experts: bool = True         # Generate experts dynamically
```

## Usage

Enable multi-agent experts when running the workflow:

```python
await run_agent_workflow_async(
    user_input="Analyze the impact of quantum computing on cryptography",
    enable_multi_agent_experts=True  # Enable multi-agent collaboration
)
```

## Example Output

Multi-agent collaborations produce rich, multifaceted analyses that combine diverse perspectives:

```
# Multi-Agent Expert Analysis: Impact of Quantum Computing on Cryptography

## Key Insights
- Research Analyst: Quantum computers could break RSA and ECC encryption through Shor's algorithm
- Technical Architect: Post-quantum cryptography standards are being developed with NIST finalizing candidates
- Security Expert: Organizations should prepare for crypto-agility to quickly change encryption methods
- AI Specialist: Machine learning can help identify vulnerable systems and optimize quantum-resistant solutions

## Individual Expert Perspectives
[Details of each expert's analysis...]

## Collaboration Insights
[Synthesis of key agreements, disagreements, and knowledge gaps...]
```

## Implementation Details

The multi-agent system is integrated into the Deer Flow graph in these key files:

- `src/agents/expert_agents.py`: Definitions of expert agent types
- `src/agents/multi_agent_coordinator.py`: Collaboration orchestration
- `src/graph/nodes.py`: Multi-agent node integration
- `src/config/multi_agent.py`: Configuration settings

## Testing

The multi-agent expert system has comprehensive tests to ensure functionality:

- **Unit Tests**: Test individual components in isolation
  - `tests/unit/agents/test_expert_agents.py`: Tests expert agent implementations
  - `tests/unit/agents/test_multi_agent_coordinator.py`: Tests the collaboration coordinator

- **Integration Tests**: Test system components working together
  - `tests/integration/test_multi_agent_experts.py`: Main integration tests
  - `tests/integration/test_multi_agent_graph_node.py`: Tests graph node integration

- **Benchmark Tests**: Compare performance and quality
  - `tests/benchmark/test_multi_agent_benchmark.py`: Comparative benchmarks

To run multi-agent tests:

```bash
# Run all multi-agent tests
python -m pytest tests/unit/agents/ tests/integration/test_multi_agent_*.py

# Run just the benchmark tests (takes longer)
python -m pytest tests/benchmark/test_multi_agent_benchmark.py
```

## Future Enhancements

Planned enhancements for the multi-agent expert system include:

1. Expert memory across multiple sessions
2. Interactive human participation in expert discussions
3. Visual knowledge maps for expert insights
4. Domain-specific expert customization
5. Enhanced debate and adversarial analysis modes
