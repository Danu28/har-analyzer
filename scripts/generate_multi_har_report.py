"""
Multi-HAR Report Generator
==========================
Generates comprehensive HTML reports comparing multiple HAR files from the same website.
Creates executive, dashboard, and comprehensive report formats for multi-run analysis.

Purpose: Multi-HAR file report generation and visualization
Used to create professional reports showing performance trends across multiple sessions.
"""

import argparse
import json
import logging
import statistics
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the scripts directory to the path for imports
script_dir = Path(__file__).parent
sys.path.append(str(script_dir))

from analyze_multi_har_runs import MultiRunAnalyzer
from compare_multi_har_performance import PerformanceComparator

logger = logging.getLogger(__name__)


class MultiRunReportGenerator:
    """Generates comprehensive multi-run HAR analysis reports."""

    def __init__(self):
        self.multi_run_analyzer = MultiRunAnalyzer()
        self.performance_comparator = PerformanceComparator()
        self.template_dir = Path(__file__).parent.parent / "templates"

    def generate_report(
        self,
        har_files: List[Path],
        output_path: Path,
        report_type: str = "comprehensive",
    ) -> bool:
        """
        Generate a multi-run comparison report.

        Args:
            har_files: List of HAR file paths (2-10 files)
            output_path: Output HTML file path
            report_type: Type of report ('comprehensive', 'dashboard', 'executive')

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate inputs
            if not self._validate_inputs(har_files, report_type):
                return False

            logger.info(
                f"Generating {report_type} multi-run report for {len(har_files)} HAR files"
            )

            # Load and analyze HAR data
            runs_data = self._load_har_data(har_files)
            if not runs_data:
                logger.error("Failed to load HAR data")
                return False

            # Perform multi-run analysis
            analysis_results = self._perform_analysis(runs_data)

            # Generate HTML report
            html_content = self._generate_html_report(analysis_results, report_type)

            # Write report to file
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            logger.info(f"Multi-run report generated successfully: {output_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to generate multi-run report: {e}")
            return False

    def _validate_inputs(self, har_files: List[Path], report_type: str) -> bool:
        """Validate input parameters."""
        if len(har_files) < 2:
            logger.error("At least 2 HAR files are required for comparison")
            return False

        if len(har_files) > 10:
            logger.error("Maximum 10 HAR files supported for comparison")
            return False

        if report_type not in ["comprehensive", "dashboard", "executive"]:
            logger.error(f"Invalid report type: {report_type}")
            return False

        for har_file in har_files:
            if not har_file.exists():
                logger.error(f"HAR file not found: {har_file}")
                return False

            if not har_file.suffix.lower() == ".har":
                logger.error(f"Invalid file extension: {har_file}")
                return False

        return True

    def _load_har_data(self, har_files: List[Path]) -> List[Dict[str, Any]]:
        """Load HAR data from files using existing chunk structure."""
        runs_data = []

        for i, har_file in enumerate(har_files):
            try:
                logger.info(f"Loading HAR file: {har_file}")

                # Check if chunked data exists, if not create it
                chunk_dir = Path("har_chunks") / har_file.stem

                if not chunk_dir.exists():
                    logger.info(
                        f"Chunked data not found for {har_file.stem}, creating chunks..."
                    )
                    self._create_chunks_for_har(har_file)

                # Load chunked data using existing break_har_for_single_analysis.py structure
                processed_data = self._load_chunked_data(
                    chunk_dir, har_file.stem, i + 1
                )
                if processed_data:
                    runs_data.append(processed_data)
                else:
                    logger.warning(f"Failed to process chunked data from {chunk_dir}")

            except Exception as e:
                logger.error(f"Error loading HAR file {har_file}: {e}")
                continue

        return runs_data

    def _create_chunks_for_har(self, har_file: Path) -> bool:
        """Create chunks for HAR file using existing break_har_for_single_analysis.py logic."""
        try:
            # Import and use break_har_for_single_analysis.py logic
            import os
            import sys

            # Add scripts directory to path
            scripts_dir = Path(__file__).parent
            if str(scripts_dir) not in sys.path:
                sys.path.insert(0, str(scripts_dir))

            # Import break_har_for_single_analysis module
            import break_har_for_single_analysis

            # Use break_har_for_single_analysis main function
            chunk_dir = Path("har_chunks") / har_file.stem
            break_har_for_single_analysis.main(
                har_file=str(har_file), output_dir=str(chunk_dir)
            )

            return chunk_dir.exists()

        except Exception as e:
            logger.error(f"Failed to create chunks for {har_file}: {e}")
            return False

    def _load_chunked_data(
        self, chunk_dir: Path, run_name: str, run_id: int
    ) -> Dict[str, Any]:
        """Load data from chunked HAR structure created by break_har_for_single_analysis.py."""
        try:
            processed = {
                "run_id": run_id,
                "run_name": run_name,
                "timestamp": datetime.now().isoformat(),
                "header_data": None,
                "summary_data": None,
                "requests": [],
                "analysis_summary": {},
                "resource_analysis": {},
                "network_analysis": {},
                "timing_analysis": {},
            }

            # Load header data (contains page timing info)
            header_file = chunk_dir / "01_header_and_metadata.json"
            if header_file.exists():
                with open(header_file, "r", encoding="utf-8") as f:
                    processed["header_data"] = json.load(f)

            # Load summary data (contains all request info)
            summary_file = chunk_dir / "02_requests_summary.json"
            if summary_file.exists():
                with open(summary_file, "r", encoding="utf-8") as f:
                    processed["summary_data"] = json.load(f)

            # Extract basic analysis from loaded data
            if processed["summary_data"]:
                requests = processed["summary_data"].get("requests", [])
                processed["requests"] = requests

                # Calculate basic metrics
                total_size = sum(
                    max(0, req.get("size", 0)) for req in requests
                )  # Fix negative sizes
                total_requests = len(requests)

                processed["analysis_summary"] = {
                    "total_requests": total_requests,
                    "total_size": total_size,
                    "failed_requests": len(
                        [r for r in requests if r.get("status", 0) >= 400]
                    ),
                }

                # Extract timing from header if available
                if processed["header_data"]:
                    pages = processed["header_data"].get("log", {}).get("pages", [])
                    if pages:
                        page_timings = pages[0].get("pageTimings", {})
                        processed["analysis_summary"].update(
                            {
                                "page_load_time": page_timings.get("onLoad", 0),
                                "dom_ready_time": page_timings.get("onContentLoad", 0),
                            }
                        )

                # Group by resource type
                by_type = {}
                for req in requests:
                    resource_type = req.get("resourceType", "unknown")
                    size = max(0, req.get("size", 0))  # Fix negative sizes

                    if resource_type not in by_type:
                        by_type[resource_type] = {"count": 0, "size": 0}

                    by_type[resource_type]["count"] += 1
                    by_type[resource_type]["size"] += size

                processed["resource_analysis"] = {
                    "total_requests": total_requests,
                    "total_size": total_size,
                    "by_type": by_type,
                }

            return processed

        except Exception as e:
            logger.error(f"Failed to load chunked data from {chunk_dir}: {e}")
            return None

    def _process_har_data(
        self, har_data: Dict[str, Any], run_name: str, run_id: int
    ) -> Dict[str, Any]:
        """Process raw HAR data into analyzable format."""
        try:
            processed = {
                "run_id": run_id,
                "run_name": run_name,
                "timestamp": datetime.now().isoformat(),
                "requests": [],
                "analysis_summary": {},
                "resource_analysis": {},
                "network_analysis": {},
                "timing_analysis": {},
            }

            # Extract entries from HAR
            entries = har_data.get("log", {}).get("entries", [])

            # Process each entry
            total_size = 0
            resource_types = {}
            domain_stats = {}
            timing_data = {
                "page_load_time": 0,
                "dom_ready_time": 0,
                "total_requests": len(entries),
            }

            for entry in entries:
                request = entry.get("request", {})
                response = entry.get("response", {})
                timings = entry.get("timings", {})

                # Extract request data
                request_data = {
                    "url": request.get("url", ""),
                    "method": request.get("method", "GET"),
                    "status": response.get("status", 0),
                    "size": response.get("bodySize", 0)
                    + response.get("headersSize", 0),
                    "mime_type": response.get("content", {}).get("mimeType", ""),
                    "total_time": sum(timings.values()) if timings else 0,
                }

                processed["requests"].append(request_data)

                # Aggregate statistics
                total_size += request_data["size"]

                # Categorize by resource type
                mime_type = request_data["mime_type"].lower()
                resource_type = self._categorize_resource_type(
                    mime_type, request_data["url"]
                )
                resource_types[resource_type] = resource_types.get(
                    resource_type, {"count": 0, "size": 0}
                )
                resource_types[resource_type]["count"] += 1
                resource_types[resource_type]["size"] += request_data["size"]

                # Domain analysis
                domain = self._extract_domain(request_data["url"])
                if domain not in domain_stats:
                    domain_stats[domain] = {"requests": 0, "size": 0}
                domain_stats[domain]["requests"] += 1
                domain_stats[domain]["size"] += request_data["size"]

            # Calculate derived metrics
            processed["analysis_summary"] = {
                "page_load_time": self._calculate_page_load_time(entries),
                "dom_ready_time": self._calculate_dom_ready_time(har_data),
                "first_contentful_paint": self._calculate_fcp(entries),
                "largest_contentful_paint": self._calculate_lcp(entries),
                "total_blocking_time": self._calculate_tbt(entries),
                "total_requests": len(entries),
                "total_size": total_size,
            }

            processed["resource_analysis"] = {
                "total_requests": len(entries),
                "total_size": total_size,
                "by_type": resource_types,
                "unique_domains": len(domain_stats),
            }

            processed["network_analysis"] = {
                "connection_reuse_rate": self._calculate_connection_reuse_rate(entries),
                "third_party_requests": self._count_third_party_requests(entries),
                "third_party_size": self._calculate_third_party_size(entries),
                "unique_domains": len(domain_stats),
                "avg_ssl_time": self._calculate_avg_ssl_time(entries),
                "avg_dns_time": self._calculate_avg_dns_time(entries),
                "third_party_providers": self._analyze_third_party_providers(entries),
            }

            return processed

        except Exception as e:
            logger.error(f"Error processing HAR data for {run_name}: {e}")
            return None

    def _perform_analysis(self, runs_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Perform comprehensive multi-run analysis."""
        analysis_results = {
            "meta": {
                "total_runs": len(runs_data),
                "analysis_timestamp": datetime.now().isoformat(),
                "run_names": [run["run_name"] for run in runs_data],
            },
            "executive_summary": {},
            "performance_comparison": {},
            "resource_analysis": {},
            "network_analysis": {},
            "cross_run_patterns": {},
            "recommendations": [],
        }

        # Performance comparison analysis
        timing_comparison = self.performance_comparator.compare_timing_metrics(
            runs_data
        )
        resource_comparison = self.performance_comparator.compare_resource_metrics(
            runs_data
        )
        network_comparison = self.performance_comparator.compare_network_metrics(
            runs_data
        )

        analysis_results["performance_comparison"] = {
            "timing": timing_comparison,
            "resources": resource_comparison,
            "network": network_comparison,
        }

        # Cross-run pattern analysis
        analysis_results["cross_run_patterns"] = (
            self.multi_run_analyzer.analyze_cross_run_patterns(runs_data)
        )

        # Resource consistency analysis
        analysis_results["resource_analysis"] = (
            self.multi_run_analyzer.analyze_resource_consistency(runs_data)
        )

        # Third-party impact analysis
        analysis_results["network_analysis"] = (
            self.multi_run_analyzer.analyze_third_party_impact(runs_data)
        )

        # Performance bottleneck identification
        analysis_results["bottlenecks"] = (
            self.multi_run_analyzer.identify_performance_bottlenecks(runs_data)
        )

        # Generate recommendations
        analysis_results["recommendations"] = (
            self.performance_comparator.generate_recommendations(
                timing_comparison, resource_comparison, network_comparison
            )
        )

        # Generate executive summary
        analysis_results["executive_summary"] = self._generate_executive_summary(
            analysis_results
        )

        return analysis_results

    def _generate_html_report(
        self, analysis_results: Dict[str, Any], report_type: str
    ) -> str:
        """Generate HTML report based on analysis results."""
        template_file = f"har_multi_run_{report_type}.html"
        template_path = self.template_dir / template_file

        if not template_path.exists():
            # Use comprehensive template as fallback
            template_path = self.template_dir / "har_multi_run_comprehensive.html"

        if not template_path.exists():
            # Generate basic HTML if no template found
            return self._generate_basic_html_report(analysis_results)

        try:
            with open(template_path, "r", encoding="utf-8") as f:
                template = f.read()

            # Replace template variables
            html_content = self._populate_template(template, analysis_results)
            return html_content

        except Exception as e:
            logger.error(f"Error loading template {template_path}: {e}")
            return self._generate_basic_html_report(analysis_results)

    def _populate_template(
        self, template: str, analysis_results: Dict[str, Any]
    ) -> str:
        """Populate HTML template with analysis data."""
        # Convert analysis results to JSON for JavaScript consumption
        analysis_json = json.dumps(analysis_results, indent=2, default=str)

        # Basic template variable replacement
        replacements = {
            "{{ANALYSIS_DATA}}": analysis_json,
            "{{REPORT_TITLE}}": f"Multi-Run HAR Analysis Report",
            "{{GENERATION_TIME}}": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "{{TOTAL_RUNS}}": str(analysis_results["meta"]["total_runs"]),
            "{{RUN_NAMES}}": ", ".join(analysis_results["meta"]["run_names"]),
        }

        for placeholder, value in replacements.items():
            template = template.replace(placeholder, value)

        return template

    def _generate_basic_html_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate a basic HTML report when no template is available."""
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Multi-Run HAR Analysis Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ background: #f4f4f4; padding: 20px; margin-bottom: 20px; }}
                .section {{ margin-bottom: 30px; }}
                .metric {{ display: inline-block; margin: 10px; padding: 10px; border: 1px solid #ddd; }}
                .good {{ background-color: #d4edda; }}
                .fair {{ background-color: #fff3cd; }}
                .poor {{ background-color: #f8d7da; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>Multi-Run HAR Analysis Report</h1>
                <p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
                <p>Total Runs: {analysis_results["meta"]["total_runs"]}</p>
                <p>Runs: {", ".join(analysis_results["meta"]["run_names"])}</p>
            </div>
            
            <div class="section">
                <h2>Executive Summary</h2>
                <p>This is a basic HTML report generated due to missing template files.</p>
                <p>Performance consistency and resource analysis completed for {analysis_results["meta"]["total_runs"]} runs.</p>
            </div>
            
            <div class="section">
                <h2>Analysis Results</h2>
                <pre>{json.dumps(analysis_results, indent=2, default=str)}</pre>
            </div>
            
            <script>
                // Analysis data for potential JavaScript processing
                const analysisData = {json.dumps(analysis_results, indent=2, default=str)};
                console.log('Analysis data loaded:', analysisData);
            </script>
        </body>
        </html>
        """
        return html

    def _generate_executive_summary(
        self, analysis_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate executive summary from analysis results."""
        summary = {
            "overall_performance": "Good",
            "consistency_rating": "Good",
            "key_findings": [],
            "critical_issues": [],
            "performance_grade": "B",
            "top_recommendations": [],
        }

        # Analyze overall performance
        timing_data = analysis_results.get("performance_comparison", {}).get(
            "timing", {}
        )
        if timing_data.get("performance_scores"):
            avg_score = statistics.mean(
                [score["score"] for score in timing_data["performance_scores"]]
            )
            summary["performance_grade"] = self._score_to_grade(avg_score)

            if avg_score >= 90:
                summary["overall_performance"] = "Excellent"
            elif avg_score >= 80:
                summary["overall_performance"] = "Good"
            elif avg_score >= 70:
                summary["overall_performance"] = "Fair"
            else:
                summary["overall_performance"] = "Poor"

        # Analyze consistency
        consistency_ratings = []
        for metric_data in timing_data.get("metrics", {}).values():
            rating = metric_data.get("consistency_rating", "")
            if rating:
                consistency_ratings.append(rating)

        if consistency_ratings:
            # Convert ratings to scores for averaging
            rating_scores = {"Excellent": 4, "Good": 3, "Fair": 2, "Poor": 1}
            avg_consistency = statistics.mean(
                [rating_scores.get(r, 0) for r in consistency_ratings]
            )

            if avg_consistency >= 3.5:
                summary["consistency_rating"] = "Excellent"
            elif avg_consistency >= 2.5:
                summary["consistency_rating"] = "Good"
            elif avg_consistency >= 1.5:
                summary["consistency_rating"] = "Fair"
            else:
                summary["consistency_rating"] = "Poor"

        # Extract key findings
        summary["key_findings"] = [
            f"Analyzed {analysis_results['meta']['total_runs']} performance runs",
            f"Overall performance grade: {summary['performance_grade']}",
            f"Performance consistency: {summary['consistency_rating']}",
        ]

        # Extract top recommendations
        all_recommendations = analysis_results.get("recommendations", [])
        summary["top_recommendations"] = [
            rec["recommendation"] for rec in all_recommendations[:3]
        ]

        return summary

    # Helper methods for HAR data processing
    def _categorize_resource_type(self, mime_type: str, url: str) -> str:
        """Categorize resource type based on MIME type and URL."""
        if "text/html" in mime_type:
            return "html"
        elif "text/css" in mime_type:
            return "css"
        elif "javascript" in mime_type or "application/json" in mime_type:
            return "javascript"
        elif "image/" in mime_type:
            return "image"
        elif "font/" in mime_type or "application/font" in mime_type:
            return "font"
        elif "xmlhttprequest" in mime_type.lower():
            return "xhr"
        else:
            return "other"

    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL."""
        try:
            from urllib.parse import urlparse

            parsed = urlparse(url)
            return parsed.netloc.lower()
        except:
            return "unknown"

    def _calculate_page_load_time(self, entries: List[Dict]) -> float:
        """Calculate page load time from HAR entries."""
        if not entries:
            return 0

        # Find the last response end time
        max_time = 0
        for entry in entries:
            start_time = entry.get("startedDateTime", "")
            total_time = sum(entry.get("timings", {}).values())
            if total_time > max_time:
                max_time = total_time

        return max_time

    def _calculate_dom_ready_time(self, har_data: Dict) -> float:
        """Calculate DOM ready time."""
        # This would need to be extracted from browser timing data
        # For now, return a placeholder
        return 0

    def _calculate_fcp(self, entries: List[Dict]) -> float:
        """Calculate First Contentful Paint."""
        # Placeholder - would need browser timing data
        return 0

    def _calculate_lcp(self, entries: List[Dict]) -> float:
        """Calculate Largest Contentful Paint."""
        # Placeholder - would need browser timing data
        return 0

    def _calculate_tbt(self, entries: List[Dict]) -> float:
        """Calculate Total Blocking Time."""
        # Placeholder - would need browser timing data
        return 0

    def _calculate_connection_reuse_rate(self, entries: List[Dict]) -> float:
        """Calculate connection reuse rate."""
        # Simplified calculation - would need connection data
        return 75.0  # Placeholder

    def _count_third_party_requests(self, entries: List[Dict]) -> int:
        """Count third-party requests."""
        # Simplified - would need main domain identification
        return len(entries) // 3  # Placeholder

    def _calculate_third_party_size(self, entries: List[Dict]) -> int:
        """Calculate total size of third-party requests."""
        # Simplified calculation
        return (
            sum(entry.get("response", {}).get("bodySize", 0) for entry in entries) // 3
        )

    def _calculate_avg_ssl_time(self, entries: List[Dict]) -> float:
        """Calculate average SSL time."""
        ssl_times = []
        for entry in entries:
            ssl_time = entry.get("timings", {}).get("ssl", 0)
            if ssl_time > 0:
                ssl_times.append(ssl_time)

        return statistics.mean(ssl_times) if ssl_times else 0

    def _calculate_avg_dns_time(self, entries: List[Dict]) -> float:
        """Calculate average DNS time."""
        dns_times = []
        for entry in entries:
            dns_time = entry.get("timings", {}).get("dns", 0)
            if dns_time > 0:
                dns_times.append(dns_time)

        return statistics.mean(dns_times) if dns_times else 0

    def _analyze_third_party_providers(self, entries: List[Dict]) -> Dict[str, Any]:
        """Analyze third-party service providers."""
        providers = {}

        for entry in entries:
            url = entry.get("request", {}).get("url", "")
            domain = self._extract_domain(url)

            # Simplified third-party detection
            if self._is_likely_third_party(domain):
                if domain not in providers:
                    providers[domain] = {"requests": 0, "size": 0}

                providers[domain]["requests"] += 1
                providers[domain]["size"] += entry.get("response", {}).get(
                    "bodySize", 0
                )

        return providers

    def _is_likely_third_party(self, domain: str) -> bool:
        """Simple heuristic to identify third-party domains."""
        third_party_indicators = [
            "google",
            "facebook",
            "twitter",
            "linkedin",
            "youtube",
            "analytics",
            "tracking",
            "ads",
            "cdn",
            "cloudflare",
        ]

        return any(indicator in domain.lower() for indicator in third_party_indicators)

    def _score_to_grade(self, score: float) -> str:
        """Convert numeric score to letter grade."""
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


def main():
    """Main function for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Generate multi-run HAR analysis report"
    )
    parser.add_argument(
        "har_files", nargs="+", help="HAR files to analyze (2-10 files)"
    )
    parser.add_argument("-o", "--output", required=True, help="Output HTML file path")
    parser.add_argument(
        "-t",
        "--type",
        choices=["comprehensive", "dashboard", "executive"],
        default="comprehensive",
        help="Report type",
    )
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")

    args = parser.parse_args()

    # Setup logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        level=log_level, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Convert string paths to Path objects
    har_files = [Path(f) for f in args.har_files]
    output_path = Path(args.output)

    # Generate report
    generator = MultiRunReportGenerator()
    success = generator.generate_report(har_files, output_path, args.type)

    if success:
        print(f"Report generated successfully: {output_path}")
        sys.exit(0)
    else:
        print("Failed to generate report")
        sys.exit(1)


if __name__ == "__main__":
    main()
