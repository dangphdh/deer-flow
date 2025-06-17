# Copyright (c) 2025 Bytedance Ltd. and/or its affiliates
# SPDX-License-Identifier: MIT

import unittest
import asyncio
import time
from datetime import datetime
import json
from pathlib import Path
import logging
from typing import Dict, Any, List

from src.workflow import run_agent_workflow_async


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MultiAgentBenchmark:
    """Benchmark tool for comparing standard workflow vs multi-agent workflow."""
    
    def __init__(self, output_dir: str = "./tests/output/benchmark"):
        """Initialize benchmark with output directory."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.results = {}
        
        # Test topics - a mix of simple and complex topics
        self.test_topics = [
            "quantum computing applications",
            "sustainable energy solutions",
            "machine learning ethics",
            "cryptocurrency impact on economy",
            "space exploration advancements"
        ]
        
        # Common workflow parameters
        self.workflow_params = {
            "max_plan_iterations": 1,
            "max_step_num": 3,
            "enable_background_investigation": True,
            "debug": False
        }
    
    async def run_benchmark(self, timeout_seconds: int = 300) -> Dict[str, Any]:
        """Run the benchmark comparing standard vs multi-agent workflow."""
        results = {}
        
        for topic in self.test_topics:
            logger.info(f"Starting benchmark for topic: {topic}")
            topic_results = {}
            
            # Test standard workflow
            start_time = time.time()
            try:
                standard_result = await asyncio.wait_for(
                    self._run_workflow(topic, enable_multi_agent=False),
                    timeout=timeout_seconds
                )
                standard_duration = time.time() - start_time
                topic_results["standard"] = {
                    "success": True,
                    "duration": standard_duration,
                    "steps": len(standard_result.get("state_changes", [])),
                    "result": self._extract_final_result(standard_result),
                    "metrics": self._calculate_metrics(standard_result)
                }
                logger.info(f"Standard workflow completed in {standard_duration:.2f}s")
            except asyncio.TimeoutError:
                topic_results["standard"] = {
                    "success": False,
                    "duration": timeout_seconds,
                    "error": "Timeout"
                }
                logger.error(f"Standard workflow timed out after {timeout_seconds}s")
            except Exception as e:
                topic_results["standard"] = {
                    "success": False,
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
                logger.error(f"Standard workflow failed: {e}")
            
            # Test multi-agent workflow
            start_time = time.time()
            try:
                multi_agent_result = await asyncio.wait_for(
                    self._run_workflow(topic, enable_multi_agent=True),
                    timeout=timeout_seconds
                )
                multi_agent_duration = time.time() - start_time
                topic_results["multi_agent"] = {
                    "success": True,
                    "duration": multi_agent_duration,
                    "steps": len(multi_agent_result.get("state_changes", [])),
                    "result": self._extract_final_result(multi_agent_result),
                    "metrics": self._calculate_metrics(multi_agent_result)
                }
                logger.info(f"Multi-agent workflow completed in {multi_agent_duration:.2f}s")
            except asyncio.TimeoutError:
                topic_results["multi_agent"] = {
                    "success": False,
                    "duration": timeout_seconds,
                    "error": "Timeout"
                }
                logger.error(f"Multi-agent workflow timed out after {timeout_seconds}s")
            except Exception as e:
                topic_results["multi_agent"] = {
                    "success": False,
                    "duration": time.time() - start_time,
                    "error": str(e)
                }
                logger.error(f"Multi-agent workflow failed: {e}")
            
            # Calculate comparison metrics if both succeeded
            if topic_results["standard"].get("success") and topic_results["multi_agent"].get("success"):
                topic_results["comparison"] = self._compare_results(
                    topic_results["standard"],
                    topic_results["multi_agent"]
                )
            
            results[topic] = topic_results
            logger.info(f"Completed benchmark for topic: {topic}")
            
            # Save intermediate results
            self._save_results(results)
        
        self.results = results
        return results
    
    async def _run_workflow(self, topic: str, enable_multi_agent: bool) -> Dict[str, Any]:
        """Run workflow and capture state changes and results."""
        state_changes = []
        
        # Create a callback to capture state changes
        async def state_callback(state):
            state_copy = {k: v for k, v in state.items() if k not in ["messages"]}
            if "current_plan" in state_copy and hasattr(state_copy["current_plan"], "model_dump"):
                state_copy["current_plan"] = state_copy["current_plan"].model_dump()
            state_changes.append(state_copy)
        
        # Format prompt
        prompt = f"Provide a comprehensive analysis of '{topic}'"
        
        # Run workflow
        final_state = await run_agent_workflow_async(
            user_input=prompt,
            enable_multi_agent_experts=enable_multi_agent,
            state_callback=state_callback,
            **self.workflow_params
        )
        
        # Capture final observations and messages
        result = {
            "state_changes": state_changes,
            "final_state": {k: v for k, v in final_state.items() 
                           if k not in ["messages"] and not callable(v)},
            "observations": final_state.get("observations", []),
            "enable_multi_agent": enable_multi_agent
        }
        
        return result
    
    def _extract_final_result(self, result: Dict[str, Any]) -> str:
        """Extract the final analysis result from workflow output."""
        observations = result.get("observations", [])
        if observations:
            return observations[-1]
        return ""
    
    def _calculate_metrics(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate metrics for the workflow result."""
        final_result = self._extract_final_result(result)
        metrics = {}
        
        # Length metrics
        metrics["content_length"] = len(final_result)
        metrics["word_count"] = len(final_result.split())
        
        # Information density (simple approximation)
        unique_words = set(word.lower() for word in final_result.split())
        metrics["unique_word_count"] = len(unique_words)
        metrics["lexical_diversity"] = len(unique_words) / max(1, metrics["word_count"])
        
        # Execution metrics
        metrics["state_change_count"] = len(result.get("state_changes", []))
        
        return metrics
    
    def _compare_results(self, standard_results: Dict[str, Any], multi_agent_results: Dict[str, Any]) -> Dict[str, Any]:
        """Compare standard and multi-agent workflow results."""
        comparison = {}
        
        # Duration comparison
        comparison["duration_diff"] = multi_agent_results["duration"] - standard_results["duration"]
        comparison["duration_percent"] = (
            (multi_agent_results["duration"] / standard_results["duration"]) - 1
        ) * 100 if standard_results["duration"] > 0 else float('inf')
        
        # Content comparison
        comparison["content_length_diff"] = (
            multi_agent_results["metrics"]["content_length"] - standard_results["metrics"]["content_length"]
        )
        comparison["content_length_percent"] = (
            (multi_agent_results["metrics"]["content_length"] / standard_results["metrics"]["content_length"]) - 1
        ) * 100 if standard_results["metrics"]["content_length"] > 0 else float('inf')
        
        # Word count comparison
        comparison["word_count_diff"] = (
            multi_agent_results["metrics"]["word_count"] - standard_results["metrics"]["word_count"]
        )
        
        # Lexical diversity comparison
        comparison["diversity_diff"] = (
            multi_agent_results["metrics"]["lexical_diversity"] - standard_results["metrics"]["lexical_diversity"]
        )
        
        # Step count comparison
        comparison["step_count_diff"] = multi_agent_results["steps"] - standard_results["steps"]
        
        return comparison
    
    def _save_results(self, results: Dict[str, Any]) -> None:
        """Save benchmark results to a file."""
        results_file = self.output_dir / f"benchmark_results_{self.timestamp}.json"
        with open(results_file, "w") as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Benchmark results written to: {results_file}")
    
    def generate_summary_report(self) -> str:
        """Generate a summary report of benchmark results."""
        if not self.results:
            return "No benchmark results available"
        
        report = "# Multi-Agent vs Standard Workflow Benchmark Summary\n\n"
        report += f"Benchmark Date: {self.timestamp}\n\n"
        
        # Overall statistics
        successful_comparisons = [
            topic_result["comparison"]
            for topic, topic_result in self.results.items()
            if "comparison" in topic_result
        ]
        
        if successful_comparisons:
            # Average metrics
            avg_duration_diff = sum(c["duration_diff"] for c in successful_comparisons) / len(successful_comparisons)
            avg_duration_percent = sum(c["duration_percent"] for c in successful_comparisons) / len(successful_comparisons)
            avg_content_length_diff = sum(c["content_length_diff"] for c in successful_comparisons) / len(successful_comparisons)
            avg_content_length_percent = sum(c["content_length_percent"] for c in successful_comparisons) / len(successful_comparisons)
            avg_diversity_diff = sum(c["diversity_diff"] for c in successful_comparisons) / len(successful_comparisons)
            
            report += "## Overall Performance Summary\n\n"
            report += f"- Average execution time difference: {avg_duration_diff:.2f}s ({avg_duration_percent:.1f}%)\n"
            report += f"- Average content length difference: {avg_content_length_diff:.0f} chars ({avg_content_length_percent:.1f}%)\n"
            report += f"- Average lexical diversity difference: {avg_diversity_diff:.3f}\n\n"
            
            # Detailed per-topic results
            report += "## Topic-by-Topic Results\n\n"
            
            for topic, topic_result in self.results.items():
                report += f"### {topic}\n\n"
                
                if "comparison" in topic_result:
                    standard = topic_result["standard"]
                    multi_agent = topic_result["multi_agent"]
                    comparison = topic_result["comparison"]
                    
                    report += "**Performance Metrics:**\n\n"
                    report += f"- Standard workflow: {standard['duration']:.2f}s, {standard['metrics']['content_length']} chars\n"
                    report += f"- Multi-agent workflow: {multi_agent['duration']:.2f}s, {multi_agent['metrics']['content_length']} chars\n"
                    report += f"- Time difference: {comparison['duration_diff']:.2f}s ({comparison['duration_percent']:.1f}%)\n"
                    report += f"- Content difference: {comparison['content_length_diff']:.0f} chars ({comparison['content_length_percent']:.1f}%)\n"
                    report += f"- Lexical diversity difference: {comparison['diversity_diff']:.3f}\n\n"
                else:
                    report += "Incomplete benchmark data for this topic\n\n"
        
        else:
            report += "No successful comparisons available\n\n"
        
        # Save report
        report_file = self.output_dir / f"benchmark_report_{self.timestamp}.md"
        with open(report_file, "w") as f:
            f.write(report)
        
        logger.info(f"Benchmark report written to: {report_file}")
        
        return report


class TestMultiAgentBenchmark(unittest.TestCase):
    """Run multi-agent benchmarks."""
    
    @unittest.skip("This is a long-running benchmark test - enable manually")
    def test_run_benchmark(self):
        """Run the multi-agent benchmark."""
        benchmark = MultiAgentBenchmark()
        results = asyncio.run(benchmark.run_benchmark())
        report = benchmark.generate_summary_report()
        
        # Basic verification that results were captured
        self.assertTrue(results)
        self.assertGreater(len(report), 100)


if __name__ == "__main__":
    # Can be run directly for benchmarking
    benchmark = MultiAgentBenchmark()
    asyncio.run(benchmark.run_benchmark())
    benchmark.generate_summary_report()
