### Enhanced `forge_benchmarking.py`
# forge_benchmarking.py
import time
import random
import psutil
import logging
from typing import Dict, Any, Optional
from enum import Enum
from functools import wraps

# Set up logging
logger = logging.getLogger(__name__)

class BenchmarkCategory(Enum):
    QUALITY = "quality"
    SPEED = "speed"
    EFFICIENCY = "efficiency"
    FIDELITY = "fidelity"
    MEMORY = "memory"
    STABILITY = "stability"

class BenchmarkLevel(Enum):
    BASIC = "basic"
    DETAILED = "detailed"
    COMPREHENSIVE = "comprehensive"

# Default benchmark configuration
_BENCHMARK_CONFIG = {
    BenchmarkLevel.BASIC: {
        BenchmarkCategory.QUALITY: True,
        BenchmarkCategory.SPEED: True,
        BenchmarkCategory.EFFICIENCY: False,
        BenchmarkCategory.FIDELITY: False,
        BenchmarkCategory.MEMORY: False,
        BenchmarkCategory.STABILITY: False
    },
    BenchmarkLevel.DETAILED: {
        BenchmarkCategory.QUALITY: True,
        BenchmarkCategory.SPEED: True,
        BenchmarkCategory.EFFICIENCY: True,
        BenchmarkCategory.FIDELITY: True,
        BenchmarkCategory.MEMORY: False,
        BenchmarkCategory.STABILITY: False
    },
    BenchmarkLevel.COMPREHENSIVE: {
        BenchmarkCategory.QUALITY: True,
        BenchmarkCategory.SPEED: True,
        BenchmarkCategory.EFFICIENCY: True,
        BenchmarkCategory.FIDELITY: True,
        BenchmarkCategory.MEMORY: True,
        BenchmarkCategory.STABILITY: True
    }
}

def timing_decorator(func):
    """Decorator to measure function execution time."""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        return result, execution_time
    return wrapper

def get_system_metrics() -> Dict[str, Any]:
    """Get current system metrics."""
    try:
        return {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": round(psutil.virtual_memory().available / (1024 ** 3), 2),
            "disk_usage_percent": psutil.disk_usage('/').percent
        }
    except Exception as e:
        logger.warning(f"Could not collect system metrics: {e}")
        return {}

def simulate_benchmark(category: BenchmarkCategory) -> Dict[str, Any]:
    """Simulate benchmark results for a specific category."""
    base_scores = {
        BenchmarkCategory.QUALITY: {"score": round(random.uniform(0.85, 0.98), 3), "weight": 0.3},
        BenchmarkCategory.SPEED: {"score": round(random.uniform(0.75, 0.95), 3), "weight": 0.25},
        BenchmarkCategory.EFFICIENCY: {"score": round(random.uniform(0.80, 0.94), 3), "weight": 0.2},
        BenchmarkCategory.FIDELITY: {"score": round(random.uniform(0.88, 0.99), 3), "weight": 0.15},
        BenchmarkCategory.MEMORY: {"score": round(random.uniform(0.70, 0.90), 3), "weight": 0.05},
        BenchmarkCategory.STABILITY: {"score": round(random.uniform(0.92, 0.99), 3), "weight": 0.05}
    }
    
    score_data = base_scores[category]
    score = score_data["score"]
    
    # Add some realistic variability based on category
    if category == BenchmarkCategory.SPEED:
        score_variation = random.uniform(-0.08, 0.05)
    elif category == BenchmarkCategory.MEMORY:
        score_variation = random.uniform(-0.10, 0.03)
    else:
        score_variation = random.uniform(-0.04, 0.02)
    
    final_score = max(0.1, min(1.0, score + score_variation))
    
    return {
        "score": round(final_score, 3),
        "weight": score_data["weight"],
        "status": "simulated",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ")
    }

def calculate_overall_score(benchmarks: Dict[str, Dict[str, Any]]) -> float:
    """Calculate weighted overall score from individual benchmarks."""
    total_weight = 0
    weighted_sum = 0
    
    for category, data in benchmarks.items():
        if "score" in data and "weight" in data:
            weighted_sum += data["score"] * data["weight"]
            total_weight += data["weight"]
    
    if total_weight > 0:
        return round(weighted_sum / total_weight, 3)
    return 0.0

def run_benchmarks(level: BenchmarkLevel = BenchmarkLevel.DETAILED) -> Dict[str, Any]:
    """
    Run comprehensive benchmark analysis.
    
    Args:
        level: The depth of benchmarking to perform
        
    Returns:
        Dictionary containing benchmark results and metrics
    """
    benchmark_start = time.time()
    logger.info(f"Starting benchmark analysis at level: {level.value}")
    
    # Get system metrics
    system_metrics = get_system_metrics()
    
    # Run configured benchmarks
    benchmarks = {}
    config = _BENCHMARK_CONFIG[level]
    
    for category, should_run in config.items():
        if should_run:
            benchmarks[category.value] = simulate_benchmark(category)
    
    # Calculate overall score
    overall_score = calculate_overall_score(benchmarks)
    
    # Generate benchmark metadata
    benchmark_end = time.time()
    benchmark_duration = benchmark_end - benchmark_start
    
    results = {
        "overall_score": overall_score,
        "benchmark_level": level.value,
        "benchmarks": benchmarks,
        "system_metrics": system_metrics,
        "metadata": {
            "duration_seconds": round(benchmark_duration, 3),
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "version": "1.0",
            "status": "completed"
        }
    }
    
    # Add performance assessment
    results["performance_assessment"] = _assess_performance(overall_score)
    
    logger.info(f"Benchmark completed in {benchmark_duration:.2f}s - Overall score: {overall_score}")
    return results

def _assess_performance(score: float) -> Dict[str, Any]:
    """Assess performance based on overall score."""
    if score >= 0.9:
        assessment = "excellent"
        recommendation = "Ideal configuration for production use"
    elif score >= 0.8:
        assessment = "good"
        recommendation = "Solid performance, minor optimizations possible"
    elif score >= 0.7:
        assessment = "fair"
        recommendation = "Acceptable but consider optimization"
    elif score >= 0.6:
        assessment = "marginal"
        recommendation = "Needs optimization for reliable performance"
    else:
        assessment = "poor"
        recommendation = "Requires significant optimization"
    
    return {
        "level": assessment,
        "score_range": f"{score:.3f}",
        "recommendation": recommendation,
        "color": "green" if score >= 0.8 else "yellow" if score >= 0.7 else "red"
    }

def quick_benchmark() -> Dict[str, Any]:
    """
    Run a quick benchmark for basic assessment.
    This is the equivalent of the original run_benchmarks() function.
    """
    return run_benchmarks(BenchmarkLevel.BASIC)

# Compatibility function - maintains backward compatibility
def run_benchmarks() -> Dict[str, Any]:
    """
    Generate benchmark metrics. 
    Later: replace with real ComfyUI performance analysis.
    """
    return quick_benchmark()

# Example usage and testing
if __name__ == "__main__":
    # Test different benchmark levels
    print("=== Quick Benchmark ===")
    quick_result = quick_benchmark()
    print(f"Overall Score: {quick_result['overall_score']}")
    
    print("\n=== Detailed Benchmark ===")
    detailed_result = run_benchmarks(BenchmarkLevel.DETAILED)
    print(f"Overall Score: {detailed_result['overall_score']}")
    for category, data in detailed_result['benchmarks'].items():
        print(f"  {category}: {data['score']} (weight: {data['weight']})")
    
    print("\n=== Comprehensive Benchmark ===")
    comprehensive_result = run_benchmarks(BenchmarkLevel.COMPREHENSIVE)
    print(f"Overall Score: {comprehensive_result['overall_score']}")
    print(f"Performance: {comprehensive_result['performance_assessment']['level']}")
    print(f"Recommendation: {comprehensive_result['performance_assessment']['recommendation']}")
