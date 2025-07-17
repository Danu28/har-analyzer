"""
Multi-HAR Analysis Module
=========================
Multi-run analysis module for HAR files.
Analyzes resource consistency, URL patterns, and cross-run insights across multiple HAR files.

Purpose: Multi-HAR file analysis and pattern detection
Used to identify trends and patterns across multiple performance sessions.
"""

import json
import logging
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


class MultiRunAnalyzer:
    """Analyzes patterns and consistency across multiple HAR runs."""

    def __init__(self):
        self.url_patterns = {}
        self.domain_analysis = {}
        self.resource_consistency = {}

    def analyze_cross_run_patterns(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Perform comprehensive cross-run pattern analysis."""
        analysis = {
            "url_consistency": self._analyze_url_consistency(runs_data),
            "resource_patterns": self._analyze_resource_patterns(runs_data),
            "third_party_analysis": self._analyze_third_party_consistency(runs_data),
            "timing_patterns": self._analyze_timing_patterns(runs_data),
            "error_analysis": self._analyze_error_patterns(runs_data),
            "cache_behavior": self._analyze_cache_behavior(runs_data),
        }

        return analysis

    def analyze_resource_consistency(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze consistency of resources loaded across runs."""
        consistency_analysis = {
            "core_resources": {},
            "variable_resources": {},
            "missing_resources": {},
            "consistency_score": 0,
            "resource_stability": {},
        }

        # Collect all URLs from all runs
        all_urls_by_run = []
        for i, run_data in enumerate(runs_data):
            urls = self._extract_urls_from_run(run_data)
            all_urls_by_run.append(
                {
                    "run_id": i + 1,
                    "run_name": run_data.get("run_name", f"Run {i + 1}"),
                    "urls": urls,
                }
            )

        # Find URLs that appear in all runs (core resources)
        all_urls = [set(run["urls"]) for run in all_urls_by_run]
        if all_urls:
            core_urls = set.intersection(*all_urls)
            all_unique_urls = set.union(*all_urls)

            consistency_analysis["core_resources"] = {
                "count": len(core_urls),
                "percentage": (
                    (len(core_urls) / len(all_unique_urls) * 100)
                    if all_unique_urls
                    else 0
                ),
                "urls": list(core_urls),
            }

            # Find variable resources (appear in some but not all runs)
            variable_urls = all_unique_urls - core_urls
            consistency_analysis["variable_resources"] = {
                "count": len(variable_urls),
                "percentage": (
                    (len(variable_urls) / len(all_unique_urls) * 100)
                    if all_unique_urls
                    else 0
                ),
                "urls": list(variable_urls),
            }

            # Calculate consistency score
            consistency_analysis["consistency_score"] = (
                (len(core_urls) / len(all_unique_urls) * 100)
                if all_unique_urls
                else 100
            )

        # Analyze resource stability by domain
        consistency_analysis["resource_stability"] = (
            self._analyze_resource_stability_by_domain(all_urls_by_run)
        )

        return consistency_analysis

    def analyze_third_party_impact(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze third-party resource impact across runs."""
        third_party_analysis = {
            "consistent_providers": {},
            "variable_providers": {},
            "impact_analysis": {},
            "recommendations": [],
        }

        # Extract third-party data from each run
        third_party_by_run = []
        for i, run_data in enumerate(runs_data):
            third_party = self._extract_third_party_data(run_data)
            third_party["run_id"] = i + 1
            third_party["run_name"] = run_data.get("run_name", f"Run {i + 1}")
            third_party_by_run.append(third_party)

        # Analyze provider consistency
        all_providers = set()
        for run in third_party_by_run:
            all_providers.update(run["providers"].keys())

        consistent_providers = set()
        variable_providers = set()

        for provider in all_providers:
            appearances = sum(
                1 for run in third_party_by_run if provider in run["providers"]
            )
            if appearances == len(runs_data):
                consistent_providers.add(provider)
            else:
                variable_providers.add(provider)

        third_party_analysis["consistent_providers"] = {
            "count": len(consistent_providers),
            "providers": list(consistent_providers),
            "impact": self._calculate_provider_impact(
                consistent_providers, third_party_by_run
            ),
        }

        third_party_analysis["variable_providers"] = {
            "count": len(variable_providers),
            "providers": list(variable_providers),
            "impact": self._calculate_provider_impact(
                variable_providers, third_party_by_run
            ),
        }

        # Generate third-party optimization recommendations
        third_party_analysis["recommendations"] = (
            self._generate_third_party_recommendations(
                consistent_providers, variable_providers, third_party_by_run
            )
        )

        return third_party_analysis

    def identify_performance_bottlenecks(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Identify consistent performance bottlenecks across runs."""
        bottlenecks = {
            "slow_resources": [],
            "blocking_resources": [],
            "large_resources": [],
            "inefficient_domains": [],
            "recommendations": [],
        }

        # Analyze slow resources across all runs
        slow_resources_by_run = []
        for run_data in runs_data:
            slow_resources = self._identify_slow_resources(run_data)
            slow_resources_by_run.append(slow_resources)

        # Find consistently slow resources
        all_slow_urls = {}
        for run_slow in slow_resources_by_run:
            for url, timing in run_slow.items():
                if url not in all_slow_urls:
                    all_slow_urls[url] = []
                all_slow_urls[url].append(timing)

        # Filter for resources that are consistently slow
        consistent_slow = {}
        for url, timings in all_slow_urls.items():
            if len(timings) >= len(runs_data) * 0.7:  # Appears slow in 70%+ of runs
                avg_time = sum(timings) / len(timings)
                consistent_slow[url] = avg_time

        bottlenecks["slow_resources"] = [
            {"url": url, "avg_time": time, "impact": "High"}
            for url, time in sorted(
                consistent_slow.items(), key=lambda x: x[1], reverse=True
            )[:10]
        ]

        # Analyze large resources
        bottlenecks["large_resources"] = self._identify_large_resources_across_runs(
            runs_data
        )

        # Analyze inefficient domains
        bottlenecks["inefficient_domains"] = self._identify_inefficient_domains(
            runs_data
        )

        # Generate bottleneck recommendations
        bottlenecks["recommendations"] = self._generate_bottleneck_recommendations(
            bottlenecks
        )

        return bottlenecks

    def _analyze_url_consistency(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze URL loading consistency across runs."""
        url_analysis = {
            "total_unique_urls": 0,
            "consistent_urls": 0,
            "variable_urls": 0,
            "consistency_percentage": 0,
            "url_patterns": {},
        }

        # Extract URLs from all runs
        all_run_urls = []
        for i, run_data in enumerate(runs_data):
            urls = self._extract_urls_from_run(run_data)
            all_run_urls.append(set(urls))

        if all_run_urls:
            # Calculate URL consistency
            all_unique = set.union(*all_run_urls)
            consistent = set.intersection(*all_run_urls)

            url_analysis.update(
                {
                    "total_unique_urls": len(all_unique),
                    "consistent_urls": len(consistent),
                    "variable_urls": len(all_unique) - len(consistent),
                    "consistency_percentage": (
                        (len(consistent) / len(all_unique) * 100) if all_unique else 100
                    ),
                }
            )

            # Analyze URL patterns
            url_analysis["url_patterns"] = self._analyze_url_patterns(all_unique)

        return url_analysis

    def _analyze_resource_patterns(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze resource loading patterns across runs."""
        patterns = {"by_type": {}, "by_domain": {}, "by_size": {}, "loading_order": {}}

        # Analyze resource types
        type_consistency = defaultdict(list)
        for run_data in runs_data:
            if "resource_analysis" in run_data:
                by_type = run_data["resource_analysis"].get("by_type", {})
                for res_type, data in by_type.items():
                    type_consistency[res_type].append(data.get("count", 0))

        for res_type, counts in type_consistency.items():
            patterns["by_type"][res_type] = {
                "counts": counts,
                "avg_count": sum(counts) / len(counts) if counts else 0,
                "consistency": self._calculate_consistency_score(counts),
            }

        return patterns

    def _analyze_third_party_consistency(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze third-party service consistency."""
        third_party = {
            "provider_consistency": {},
            "request_patterns": {},
            "size_patterns": {},
        }

        # Extract third-party providers from each run
        all_providers = defaultdict(list)
        for run_data in runs_data:
            providers = self._extract_third_party_providers(run_data)
            for provider, count in providers.items():
                all_providers[provider].append(count)

        # Analyze provider consistency
        for provider, counts in all_providers.items():
            consistency_score = self._calculate_consistency_score(counts)
            third_party["provider_consistency"][provider] = {
                "appearances": len(counts),
                "total_runs": len(runs_data),
                "avg_requests": sum(counts) / len(counts) if counts else 0,
                "consistency": consistency_score,
            }

        return third_party

    def _analyze_timing_patterns(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze timing patterns across runs."""
        timing_patterns = {
            "load_time_distribution": {},
            "critical_path_consistency": {},
            "resource_timing_patterns": {},
        }

        # Analyze load time distribution
        load_times = []
        for run_data in runs_data:
            if "analysis_summary" in run_data:
                load_time = run_data["analysis_summary"].get("page_load_time", 0)
                if load_time > 0:
                    load_times.append(load_time)

        if load_times:
            timing_patterns["load_time_distribution"] = {
                "times": load_times,
                "min": min(load_times),
                "max": max(load_times),
                "avg": sum(load_times) / len(load_times),
                "consistency": self._calculate_consistency_score(load_times),
            }

        return timing_patterns

    def _analyze_error_patterns(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze error patterns across runs."""
        error_analysis = {
            "consistent_errors": [],
            "intermittent_errors": [],
            "error_rate_by_run": [],
            "common_error_types": {},
        }

        # Extract errors from each run
        errors_by_run = []
        for i, run_data in enumerate(runs_data):
            errors = self._extract_errors_from_run(run_data)
            errors_by_run.append(
                {
                    "run_id": i + 1,
                    "run_name": run_data.get("run_name", f"Run {i + 1}"),
                    "errors": errors,
                    "error_count": len(errors),
                }
            )

        # Analyze error consistency
        all_error_urls = set()
        for run_errors in errors_by_run:
            error_urls = {error["url"] for error in run_errors["errors"]}
            all_error_urls.update(error_urls)

        # Find consistently failing URLs
        for url in all_error_urls:
            appearances = sum(
                1
                for run in errors_by_run
                if any(error["url"] == url for error in run["errors"])
            )
            if appearances == len(runs_data):
                error_analysis["consistent_errors"].append(url)
            elif appearances > 1:
                error_analysis["intermittent_errors"].append(
                    {"url": url, "frequency": f"{appearances}/{len(runs_data)}"}
                )

        # Calculate error rates
        error_analysis["error_rate_by_run"] = [
            {
                "run_name": run["run_name"],
                "error_count": run["error_count"],
                "run_id": run["run_id"],
            }
            for run in errors_by_run
        ]

        return error_analysis

    def _analyze_cache_behavior(
        self, runs_data: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze caching behavior across runs."""
        cache_analysis = {
            "cache_hit_patterns": {},
            "cacheable_resources": {},
            "cache_efficiency": {},
        }

        # Placeholder for cache analysis implementation
        # Would analyze cache headers, 304 responses, etc.

        return cache_analysis

    def _extract_urls_from_run(self, run_data: Dict[str, Any]) -> List[str]:
        """Extract all URLs from a single run's data."""
        urls = []

        # Try to get from different possible data structures
        if "requests" in run_data:
            for request in run_data["requests"]:
                url = request.get("url", "")
                if url:
                    urls.append(url)
        elif "entries" in run_data:
            for entry in run_data["entries"]:
                url = entry.get("request", {}).get("url", "")
                if url:
                    urls.append(url)

        return urls

    def _extract_third_party_data(self, run_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract third-party provider data from a run."""
        third_party = {"providers": {}, "total_requests": 0, "total_size": 0}

        if "network_analysis" in run_data:
            net_analysis = run_data["network_analysis"]
            third_party.update(
                {
                    "providers": net_analysis.get("third_party_providers", {}),
                    "total_requests": net_analysis.get("third_party_requests", 0),
                    "total_size": net_analysis.get("third_party_size", 0),
                }
            )

        return third_party

    def _extract_third_party_providers(
        self, run_data: Dict[str, Any]
    ) -> Dict[str, int]:
        """Extract third-party providers and their request counts."""
        providers = {}

        urls = self._extract_urls_from_run(run_data)
        for url in urls:
            domain = self._extract_domain(url)
            if self._is_third_party_domain(domain):
                providers[domain] = providers.get(domain, 0) + 1

        return providers

    def _extract_errors_from_run(
        self, run_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Extract error information from a run."""
        errors = []

        if "requests" in run_data:
            for request in run_data["requests"]:
                status = request.get("status", 200)
                if status >= 400:
                    errors.append(
                        {
                            "url": request.get("url", ""),
                            "status": status,
                            "error_type": "HTTP Error",
                        }
                    )

        return errors

    def _identify_slow_resources(self, run_data: Dict[str, Any]) -> Dict[str, float]:
        """Identify slow resources in a run."""
        slow_resources = {}
        threshold = 2000  # 2 seconds threshold

        if "requests" in run_data:
            for request in run_data["requests"]:
                total_time = request.get("total_time", 0)
                if total_time > threshold:
                    url = request.get("url", "")
                    slow_resources[url] = total_time

        return slow_resources

    def _identify_large_resources_across_runs(
        self, runs_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify consistently large resources across runs."""
        large_resources = []
        size_threshold = 1024 * 1024  # 1MB threshold

        # Collect resource sizes across all runs
        resource_sizes = defaultdict(list)

        for run_data in runs_data:
            if "requests" in run_data:
                for request in run_data["requests"]:
                    url = request.get("url", "")
                    size = request.get("size", 0)
                    if size > size_threshold:
                        resource_sizes[url].append(size)

        # Find consistently large resources
        for url, sizes in resource_sizes.items():
            if len(sizes) >= len(runs_data) * 0.7:  # Appears large in 70%+ of runs
                avg_size = sum(sizes) / len(sizes)
                large_resources.append(
                    {
                        "url": url,
                        "avg_size": avg_size,
                        "appearances": len(sizes),
                        "impact": "High" if avg_size > size_threshold * 5 else "Medium",
                    }
                )

        return sorted(large_resources, key=lambda x: x["avg_size"], reverse=True)[:10]

    def _identify_inefficient_domains(
        self, runs_data: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Identify domains with poor performance patterns."""
        domain_performance = defaultdict(list)

        for run_data in runs_data:
            if "requests" in run_data:
                for request in run_data["requests"]:
                    url = request.get("url", "")
                    domain = self._extract_domain(url)
                    total_time = request.get("total_time", 0)
                    if total_time > 0:
                        domain_performance[domain].append(total_time)

        inefficient_domains = []
        for domain, times in domain_performance.items():
            if len(times) >= 5:  # Domain with enough requests to analyze
                avg_time = sum(times) / len(times)
                if avg_time > 1000:  # Average > 1 second
                    inefficient_domains.append(
                        {
                            "domain": domain,
                            "avg_response_time": avg_time,
                            "request_count": len(times),
                            "impact": "High" if avg_time > 3000 else "Medium",
                        }
                    )

        return sorted(
            inefficient_domains, key=lambda x: x["avg_response_time"], reverse=True
        )[:10]

    def _analyze_url_patterns(self, urls: Set[str]) -> Dict[str, Any]:
        """Analyze patterns in URLs."""
        patterns = {
            "file_types": defaultdict(int),
            "domains": defaultdict(int),
            "paths": defaultdict(int),
        }

        for url in urls:
            # Analyze file extensions
            if "." in url:
                ext = url.split(".")[-1].split("?")[0].lower()
                patterns["file_types"][ext] += 1

            # Analyze domains
            domain = self._extract_domain(url)
            patterns["domains"][domain] += 1

            # Analyze path patterns
            parsed = urlparse(url)
            path_parts = [part for part in parsed.path.split("/") if part]
            if path_parts:
                patterns["paths"][path_parts[0]] += 1

        return {
            "file_types": dict(patterns["file_types"]),
            "domains": dict(patterns["domains"]),
            "paths": dict(patterns["paths"]),
        }

    def _analyze_resource_stability_by_domain(
        self, all_urls_by_run: List[Dict]
    ) -> Dict[str, Any]:
        """Analyze resource stability grouped by domain."""
        domain_stability = {}

        # Group URLs by domain for each run
        domains_by_run = []
        for run in all_urls_by_run:
            domain_urls = defaultdict(set)
            for url in run["urls"]:
                domain = self._extract_domain(url)
                domain_urls[domain].add(url)
            domains_by_run.append(dict(domain_urls))

        # Analyze stability for each domain
        all_domains = set()
        for run_domains in domains_by_run:
            all_domains.update(run_domains.keys())

        for domain in all_domains:
            domain_urls_all_runs = []
            for run_domains in domains_by_run:
                domain_urls_all_runs.append(run_domains.get(domain, set()))

            if domain_urls_all_runs:
                # Calculate domain stability
                all_domain_urls = set.union(*domain_urls_all_runs)
                consistent_urls = (
                    set.intersection(*domain_urls_all_runs)
                    if len(domain_urls_all_runs) > 1
                    else all_domain_urls
                )

                stability_score = (
                    (len(consistent_urls) / len(all_domain_urls) * 100)
                    if all_domain_urls
                    else 100
                )

                domain_stability[domain] = {
                    "total_urls": len(all_domain_urls),
                    "consistent_urls": len(consistent_urls),
                    "stability_score": stability_score,
                    "stability_rating": self._get_stability_rating(stability_score),
                }

        return domain_stability

    def _calculate_provider_impact(
        self, providers: Set[str], third_party_by_run: List[Dict]
    ) -> Dict[str, Any]:
        """Calculate the impact of third-party providers."""
        impact = {"total_requests": 0, "total_size": 0, "avg_requests_per_run": 0}

        total_requests = 0
        total_size = 0

        for run in third_party_by_run:
            for provider in providers:
                if provider in run["providers"]:
                    provider_data = run["providers"][provider]
                    total_requests += provider_data.get("requests", 0)
                    total_size += provider_data.get("size", 0)

        impact.update(
            {
                "total_requests": total_requests,
                "total_size": total_size,
                "avg_requests_per_run": (
                    total_requests / len(third_party_by_run)
                    if third_party_by_run
                    else 0
                ),
            }
        )

        return impact

    def _generate_third_party_recommendations(
        self,
        consistent_providers: Set[str],
        variable_providers: Set[str],
        third_party_by_run: List[Dict],
    ) -> List[str]:
        """Generate recommendations for third-party optimization."""
        recommendations = []

        if len(consistent_providers) > 10:
            recommendations.append(
                "Consider consolidating third-party providers to reduce DNS lookups and connection overhead"
            )

        if len(variable_providers) > len(consistent_providers):
            recommendations.append(
                "High variability in third-party services may indicate A/B testing or conditional loading"
            )

        # Calculate average impact
        total_third_party_requests = sum(
            run["total_requests"] for run in third_party_by_run
        )
        avg_requests = (
            total_third_party_requests / len(third_party_by_run)
            if third_party_by_run
            else 0
        )

        if avg_requests > 50:
            recommendations.append(
                "High third-party request volume - consider lazy loading or request prioritization"
            )

        return recommendations

    def _generate_bottleneck_recommendations(
        self, bottlenecks: Dict[str, Any]
    ) -> List[str]:
        """Generate recommendations based on identified bottlenecks."""
        recommendations = []

        if bottlenecks["slow_resources"]:
            recommendations.append(
                "Optimize consistently slow resources through compression, CDN, or caching"
            )

        if bottlenecks["large_resources"]:
            recommendations.append("Implement progressive loading for large resources")

        if bottlenecks["inefficient_domains"]:
            recommendations.append(
                "Consider self-hosting or finding alternatives for slow third-party domains"
            )

        return recommendations

    def _calculate_consistency_score(self, values: List[float]) -> str:
        """Calculate consistency score for a list of values."""
        if not values or len(values) <= 1:
            return "Insufficient Data"

        mean_val = sum(values) / len(values)
        if mean_val == 0:
            return "Perfect"

        # Calculate coefficient of variation
        variance = sum((x - mean_val) ** 2 for x in values) / len(values)
        std_dev = variance**0.5
        cv = (std_dev / mean_val) * 100

        if cv < 10:
            return "Excellent"
        elif cv < 20:
            return "Good"
        elif cv < 30:
            return "Fair"
        else:
            return "Poor"

    def _get_stability_rating(self, score: float) -> str:
        """Convert stability score to rating."""
        if score >= 90:
            return "Very Stable"
        elif score >= 75:
            return "Stable"
        elif score >= 60:
            return "Moderately Stable"
        elif score >= 40:
            return "Unstable"
        else:
            return "Very Unstable"

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"

    def _is_third_party_domain(self, domain: str) -> bool:
        """Determine if a domain is third-party (simplified logic)."""
        # This is a simplified implementation
        # In practice, you'd compare against the main site domain
        common_first_party = ["localhost", "127.0.0.1", "0.0.0.0"]
        return domain not in common_first_party and domain != ""
