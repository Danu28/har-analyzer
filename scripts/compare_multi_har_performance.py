"""
Multi-HAR Performance Comparison
================================
Performance comparison utilities for multi-run HAR analysis.
Provides functions to compare metrics, calculate trends, and identify patterns across multiple HAR files.

Purpose: Multi-HAR file performance comparison and trend analysis
Used in multi-run analysis workflows to compare performance across different sessions.
"""

import json
import logging
import statistics
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class PerformanceComparator:
    """Handles performance metric comparison across multiple HAR runs."""

    def __init__(self):
        self.critical_metrics = {
            "page_load_time": {"good": 3000, "fair": 5000},  # milliseconds
            "dom_ready_time": {"good": 1500, "fair": 3000},
            "first_contentful_paint": {"good": 1800, "fair": 3000},
            "largest_contentful_paint": {"good": 2500, "fair": 4000},
            "total_blocking_time": {"good": 200, "fair": 600},
            "cumulative_layout_shift": {"good": 0.1, "fair": 0.25},
        }

    def compare_timing_metrics(self, runs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Compare timing metrics across all runs."""
        timing_comparison = {
            "metrics": {},
            "trends": {},
            "performance_scores": [],
            "consistency": {},
        }

        # Extract timing metrics from each run
        metrics_by_run = []
        for i, run_data in enumerate(runs_data):
            run_metrics = self._extract_timing_metrics(run_data)
            run_metrics["run_id"] = i + 1
            run_metrics["run_name"] = run_data.get("run_name", f"Run {i + 1}")
            metrics_by_run.append(run_metrics)

        # Calculate statistics for each metric
        metric_names = [
            "page_load_time",
            "dom_ready_time",
            "first_contentful_paint",
            "largest_contentful_paint",
            "total_blocking_time",
        ]

        for metric in metric_names:
            values = [
                run.get(metric, 0)
                for run in metrics_by_run
                if run.get(metric) is not None
            ]
            if values:
                timing_comparison["metrics"][metric] = {
                    "values": values,
                    "min": min(values),
                    "max": max(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "std_dev": statistics.stdev(values) if len(values) > 1 else 0,
                    "variation_coefficient": (
                        (statistics.stdev(values) / statistics.mean(values)) * 100
                        if len(values) > 1 and statistics.mean(values) > 0
                        else 0
                    ),
                    "consistency_rating": self._calculate_consistency_rating(values),
                }

                # Calculate trend
                timing_comparison["trends"][metric] = self._calculate_trend(values)

        # Calculate overall performance scores
        for run_metrics in metrics_by_run:
            score = self._calculate_performance_score(run_metrics)
            timing_comparison["performance_scores"].append(
                {
                    "run_id": run_metrics["run_id"],
                    "run_name": run_metrics["run_name"],
                    "score": score,
                    "grade": self._get_performance_grade(score),
                }
            )

        # Overall consistency analysis
        timing_comparison["consistency"]["overall_rating"] = (
            self._calculate_overall_consistency(timing_comparison["metrics"])
        )
        timing_comparison["consistency"]["most_consistent"] = (
            self._find_most_consistent_metric(timing_comparison["metrics"])
        )
        timing_comparison["consistency"]["least_consistent"] = (
            self._find_least_consistent_metric(timing_comparison["metrics"])
        )

        return timing_comparison

    def compare_resource_metrics(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare resource metrics across all runs."""
        resource_comparison = {
            "totals": {},
            "by_type": {},
            "size_analysis": {},
            "efficiency": {},
        }

        # Extract resource data from each run
        runs_resources = []
        for i, run_data in enumerate(runs_data):
            resources = self._extract_resource_metrics(run_data)
            resources["run_id"] = i + 1
            resources["run_name"] = run_data.get("run_name", f"Run {i + 1}")
            runs_resources.append(resources)

        # Compare total counts and sizes
        total_requests = [run["total_requests"] for run in runs_resources]
        total_size = [run["total_size"] for run in runs_resources]

        resource_comparison["totals"] = {
            "requests": {
                "values": total_requests,
                "min": min(total_requests),
                "max": max(total_requests),
                "mean": statistics.mean(total_requests),
                "consistency": self._calculate_consistency_rating(total_requests),
            },
            "size": {
                "values": total_size,
                "min": min(total_size),
                "max": max(total_size),
                "mean": statistics.mean(total_size),
                "consistency": self._calculate_consistency_rating(total_size),
            },
        }

        # Compare by resource type
        resource_types = ["html", "css", "javascript", "image", "font", "xhr", "other"]
        for res_type in resource_types:
            type_counts = [
                run["by_type"].get(res_type, {}).get("count", 0)
                for run in runs_resources
            ]
            type_sizes = [
                run["by_type"].get(res_type, {}).get("size", 0)
                for run in runs_resources
            ]

            if any(count > 0 for count in type_counts):
                resource_comparison["by_type"][res_type] = {
                    "count": {
                        "values": type_counts,
                        "mean": statistics.mean(type_counts),
                        "min": min(type_counts),
                        "max": max(type_counts),
                        "consistency": self._calculate_consistency_rating(type_counts),
                    },
                    "size": {
                        "values": type_sizes,
                        "mean": statistics.mean(type_sizes),
                        "min": min(type_sizes),
                        "max": max(type_sizes),
                        "consistency": self._calculate_consistency_rating(type_sizes),
                    },
                }

        # Size efficiency analysis
        resource_comparison["efficiency"] = self._analyze_resource_efficiency(
            runs_resources
        )

        return resource_comparison

    def compare_network_metrics(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Compare network-related metrics across all runs."""
        network_comparison = {
            "connection_reuse": {},
            "third_party_impact": {},
            "ssl_analysis": {},
            "dns_analysis": {},
        }

        # Extract network data from each run
        runs_network = []
        for i, run_data in enumerate(runs_data):
            network = self._extract_network_metrics(run_data)
            network["run_id"] = i + 1
            network["run_name"] = run_data.get("run_name", f"Run {i + 1}")
            runs_network.append(network)

        # Connection reuse analysis
        reuse_rates = [run["connection_reuse_rate"] for run in runs_network]
        network_comparison["connection_reuse"] = {
            "rates": reuse_rates,
            "mean": statistics.mean(reuse_rates),
            "consistency": self._calculate_consistency_rating(reuse_rates),
            "trend": self._calculate_trend(reuse_rates),
            "rating": self._rate_connection_reuse(statistics.mean(reuse_rates)),
        }

        # Third-party impact analysis
        third_party_counts = [run["third_party_requests"] for run in runs_network]
        third_party_sizes = [run["third_party_size"] for run in runs_network]

        network_comparison["third_party_impact"] = {
            "request_count": {
                "values": third_party_counts,
                "mean": statistics.mean(third_party_counts),
                "consistency": self._calculate_consistency_rating(third_party_counts),
            },
            "size_impact": {
                "values": third_party_sizes,
                "mean": statistics.mean(third_party_sizes),
                "consistency": self._calculate_consistency_rating(third_party_sizes),
            },
            "domains": self._analyze_third_party_domains(runs_network),
        }

        # SSL and DNS analysis
        ssl_times = [run.get("avg_ssl_time", 0) for run in runs_network]
        dns_times = [run.get("avg_dns_time", 0) for run in runs_network]

        if any(time > 0 for time in ssl_times):
            network_comparison["ssl_analysis"] = {
                "times": ssl_times,
                "mean": statistics.mean([t for t in ssl_times if t > 0]),
                "consistency": self._calculate_consistency_rating(
                    [t for t in ssl_times if t > 0]
                ),
            }

        if any(time > 0 for time in dns_times):
            network_comparison["dns_analysis"] = {
                "times": dns_times,
                "mean": statistics.mean([t for t in dns_times if t > 0]),
                "consistency": self._calculate_consistency_rating(
                    [t for t in dns_times if t > 0]
                ),
            }

        return network_comparison

    def generate_recommendations(
        self,
        timing_comparison: Dict,
        resource_comparison: Dict,
        network_comparison: Dict,
    ) -> List[Dict[str, Any]]:
        """Generate actionable recommendations based on comparison analysis."""
        recommendations = []

        # Performance timing recommendations
        for metric, data in timing_comparison["metrics"].items():
            if data["consistency_rating"] == "Poor":
                recommendations.append(
                    {
                        "category": "Performance Consistency",
                        "priority": "High",
                        "issue": f"{metric.replace('_', ' ').title()} shows high variation across runs",
                        "description": f"Coefficient of variation: {data['variation_coefficient']:.1f}%",
                        "recommendation": f"Investigate factors causing {metric} inconsistency. Check for competing processes, network conditions, or caching issues.",
                        "impact": "High - Inconsistent performance affects user experience reliability",
                    }
                )

        # Resource optimization recommendations
        if resource_comparison["totals"]["requests"]["consistency"] == "Poor":
            recommendations.append(
                {
                    "category": "Resource Optimization",
                    "priority": "Medium",
                    "issue": "Inconsistent number of requests across runs",
                    "description": f"Request count varies from {resource_comparison['totals']['requests']['min']} to {resource_comparison['totals']['requests']['max']}",
                    "recommendation": "Investigate dynamic content loading, A/B tests, or third-party script variations",
                    "impact": "Medium - May indicate unpredictable resource loading",
                }
            )

        # Network optimization recommendations
        if network_comparison["connection_reuse"]["rating"] in ["Poor", "Fair"]:
            recommendations.append(
                {
                    "category": "Network Optimization",
                    "priority": "High",
                    "issue": "Poor connection reuse efficiency",
                    "description": f"Average connection reuse rate: {network_comparison['connection_reuse']['mean']:.1f}%",
                    "recommendation": "Implement HTTP/2, enable keep-alive connections, optimize domain sharding",
                    "impact": "High - Poor connection reuse significantly impacts load times",
                }
            )

        # Third-party impact recommendations
        third_party_mean = network_comparison["third_party_impact"]["request_count"][
            "mean"
        ]
        if third_party_mean > 50:  # High threshold for third-party requests
            recommendations.append(
                {
                    "category": "Third-Party Optimization",
                    "priority": "Medium",
                    "issue": "High third-party request volume",
                    "description": f"Average third-party requests: {third_party_mean:.0f}",
                    "recommendation": "Audit third-party scripts, implement lazy loading, consider self-hosting critical resources",
                    "impact": "Medium - Third-party dependencies can impact performance and reliability",
                }
            )

        # Sort recommendations by priority
        priority_order = {"High": 0, "Medium": 1, "Low": 2}
        recommendations.sort(key=lambda x: priority_order.get(x["priority"], 3))

        return recommendations

    def _extract_timing_metrics(self, run_data: Dict[str, Any]) -> Dict[str, float]:
        """Extract timing metrics from a single run's data using HAR chunk structure."""
        metrics = {}

        # Try to get metrics from analysis summary if available
        if "analysis_summary" in run_data:
            summary = run_data["analysis_summary"]
            metrics.update(
                {
                    "page_load_time": summary.get("page_load_time", 0),
                    "dom_ready_time": summary.get("dom_ready_time", 0),
                    "first_contentful_paint": summary.get("first_contentful_paint", 0),
                    "largest_contentful_paint": summary.get(
                        "largest_contentful_paint", 0
                    ),
                    "total_blocking_time": summary.get("total_blocking_time", 0),
                }
            )
            return metrics

        # Extract from HAR chunk structure (break_har_file.py output)
        if "header_data" in run_data and run_data["header_data"]:
            header = run_data["header_data"]
            pages = header.get("log", {}).get("pages", [])
            if pages:
                page_timings = pages[0].get("pageTimings", {})
                # Convert milliseconds to seconds for consistency
                metrics["page_load_time"] = page_timings.get("onLoad", 0)
                metrics["dom_ready_time"] = page_timings.get("onContentLoad", 0)
                # Note: FCP, LCP, TBT are not available in basic HAR pageTimings
                # These would need to be extracted from browser dev tools or lighthouse data
                metrics["first_contentful_paint"] = 0  # Not available in standard HAR
                metrics["largest_contentful_paint"] = 0  # Not available in standard HAR
                metrics["total_blocking_time"] = 0  # Not available in standard HAR

        # Fallback to calculating from raw data if needed
        elif "timing_analysis" in run_data:
            timing = run_data["timing_analysis"]
            metrics["page_load_time"] = timing.get("total_time", 0)
            metrics["dom_ready_time"] = timing.get("dom_ready", 0)

        return metrics

    def _extract_resource_metrics(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract resource metrics from a single run's data using HAR chunk structure."""
        resources = {"total_requests": 0, "total_size": 0, "by_type": {}}

        # Try existing structure first
        if "resource_analysis" in run_data:
            res_analysis = run_data["resource_analysis"]
            resources["total_requests"] = res_analysis.get("total_requests", 0)
            resources["total_size"] = res_analysis.get("total_size", 0)
            resources["by_type"] = res_analysis.get("by_type", {})
            return resources

        # Extract from HAR chunk structure (break_har_file.py output)
        if "summary_data" in run_data and run_data["summary_data"]:
            summary = run_data["summary_data"]
            requests = summary.get("requests", [])
            resources["total_requests"] = len(requests)

            # Calculate metrics from request data
            total_size = 0
            by_type = {}

            for request in requests:
                size = request.get("size", 0)
                # Fix negative sizes issue - treat negative as 0
                if size < 0:
                    size = 0

                total_size += size
                resource_type = request.get("resourceType", "unknown")

                if resource_type not in by_type:
                    by_type[resource_type] = {"count": 0, "size": 0}

                by_type[resource_type]["count"] += 1
                by_type[resource_type]["size"] += size

            resources["total_size"] = total_size
            resources["by_type"] = by_type

        return resources

    def _extract_network_metrics(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract network metrics from a single run's data."""
        network = {
            "connection_reuse_rate": 0,
            "third_party_requests": 0,
            "third_party_size": 0,
            "unique_domains": 0,
            "avg_ssl_time": 0,
            "avg_dns_time": 0,
        }

        if "network_analysis" in run_data:
            net_analysis = run_data["network_analysis"]
            network.update(
                {
                    "connection_reuse_rate": net_analysis.get(
                        "connection_reuse_rate", 0
                    ),
                    "third_party_requests": net_analysis.get("third_party_requests", 0),
                    "third_party_size": net_analysis.get("third_party_size", 0),
                    "unique_domains": net_analysis.get("unique_domains", 0),
                    "avg_ssl_time": net_analysis.get("avg_ssl_time", 0),
                    "avg_dns_time": net_analysis.get("avg_dns_time", 0),
                }
            )

        return network

    def _calculate_consistency_rating(self, values: List[float]) -> str:
        """Calculate consistency rating based on coefficient of variation."""
        if len(values) <= 1:
            return "Insufficient Data"

        if all(v == 0 for v in values):
            return "Perfect"

        mean_val = statistics.mean(values)
        if mean_val == 0:
            return "Perfect"

        cv = (statistics.stdev(values) / mean_val) * 100

        if cv < 10:
            return "Excellent"
        elif cv < 20:
            return "Good"
        elif cv < 30:
            return "Fair"
        else:
            return "Poor"

    def _calculate_trend(self, values: List[float]) -> str:
        """Calculate trend direction for a series of values."""
        if len(values) < 2:
            return "Insufficient Data"

        # Simple linear trend calculation
        n = len(values)
        x = list(range(n))
        y = values

        # Calculate slope
        x_mean = sum(x) / n
        y_mean = sum(y) / n

        slope_num = sum((x[i] - x_mean) * (y[i] - y_mean) for i in range(n))
        slope_den = sum((x[i] - x_mean) ** 2 for i in range(n))

        if slope_den == 0:
            return "Stable"

        slope = slope_num / slope_den

        # Determine trend
        threshold = y_mean * 0.05  # 5% of mean as threshold

        if slope > threshold:
            return (
                "Improving"
                if any("time" in str(values) for values in [values])
                else "Worsening"
            )
        elif slope < -threshold:
            return (
                "Worsening"
                if any("time" in str(values) for values in [values])
                else "Improving"
            )
        else:
            return "Stable"

    def _calculate_performance_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall performance score for a run (0-100)."""
        score = 100

        for metric, value in metrics.items():
            if metric in self.critical_metrics and value > 0:
                thresholds = self.critical_metrics[metric]
                if value > thresholds["fair"]:
                    score -= 20  # Poor performance
                elif value > thresholds["good"]:
                    score -= 10  # Fair performance
                # Good performance: no deduction

        return max(0, score)

    def _get_performance_grade(self, score: float) -> str:
        """Convert performance score to letter grade."""
        if score >= 90:
            return "A"
        elif score >= 80:
            return "B"
        elif score >= 70:
            return "C"
        elif score >= 60:
            return "D"
        else:
            return "F"

    def _calculate_overall_consistency(self, metrics: Dict[str, Dict]) -> str:
        """Calculate overall consistency rating across all metrics."""
        ratings = []
        rating_scores = {
            "Excellent": 4,
            "Good": 3,
            "Fair": 2,
            "Poor": 1,
            "Insufficient Data": 0,
        }

        for metric_data in metrics.values():
            rating = metric_data.get("consistency_rating", "Insufficient Data")
            if rating in rating_scores:
                ratings.append(rating_scores[rating])

        if not ratings:
            return "Insufficient Data"

        avg_score = sum(ratings) / len(ratings)

        if avg_score >= 3.5:
            return "Excellent"
        elif avg_score >= 2.5:
            return "Good"
        elif avg_score >= 1.5:
            return "Fair"
        else:
            return "Poor"

    def _find_most_consistent_metric(self, metrics: Dict[str, Dict]) -> str:
        """Find the most consistent metric across runs."""
        rating_scores = {
            "Excellent": 4,
            "Good": 3,
            "Fair": 2,
            "Poor": 1,
            "Insufficient Data": 0,
        }
        best_metric = None
        best_score = -1

        for metric, data in metrics.items():
            rating = data.get("consistency_rating", "Insufficient Data")
            score = rating_scores.get(rating, 0)
            if score > best_score:
                best_score = score
                best_metric = metric

        return best_metric or "None"

    def _find_least_consistent_metric(self, metrics: Dict[str, Dict]) -> str:
        """Find the least consistent metric across runs."""
        rating_scores = {
            "Excellent": 4,
            "Good": 3,
            "Fair": 2,
            "Poor": 1,
            "Insufficient Data": 0,
        }
        worst_metric = None
        worst_score = 5

        for metric, data in metrics.items():
            rating = data.get("consistency_rating", "Insufficient Data")
            score = rating_scores.get(rating, 0)
            if score < worst_score and score > 0:  # Exclude "Insufficient Data"
                worst_score = score
                worst_metric = metric

        return worst_metric or "None"

    def _analyze_resource_efficiency(
        self, runs_resources: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze resource loading efficiency across runs."""
        efficiency = {
            "compression_ratio": [],
            "cache_efficiency": [],
            "resource_distribution": {},
        }

        # Placeholder for future implementation
        # Would analyze compression ratios, cache hit rates, etc.

        return efficiency

    def _analyze_third_party_domains(self, runs_network: List[Dict]) -> Dict[str, Any]:
        """Analyze third-party domains across runs."""
        domains = {
            "consistent_domains": [],
            "variable_domains": [],
            "domain_frequency": {},
        }

        # Placeholder for future implementation
        # Would analyze which third-party domains appear consistently

        return domains

    def _rate_connection_reuse(self, reuse_rate: float) -> str:
        """Rate connection reuse efficiency."""
        if reuse_rate >= 80:
            return "Excellent"
        elif reuse_rate >= 60:
            return "Good"
        elif reuse_rate >= 40:
            return "Fair"
        else:
            return "Poor"
