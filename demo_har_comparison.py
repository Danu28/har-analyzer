#!/usr/bin/env python3
"""
Demo: HAR File Comparison Tool
==============================
Interactive demo script that allows users to select two HAR files for comparison
and generates a comprehensive comparison report.

Usage:
    python demo_har_comparison.py

Features:
- Interactive file selection for baseline and target HAR files
- Automated workflow: breakdown -> comparison -> HTML report
- Professional report generation with charts and insights
"""

import json
import os
import subprocess
import sys
from datetime import datetime
from pathlib import Path


def print_header():
    """Print demo header"""
    print("=" * 60)
    print("HAR FILE COMPARISON DEMO")
    print("=" * 60)
    print("This demo compares two HAR files and generates a detailed")
    print("comparison report showing performance differences.\n")


def find_har_files():
    """Find all available HAR files"""
    har_files = []

    # Check current directory
    current_dir = Path(".")
    har_files.extend(current_dir.glob("*.har"))

    # Check HAR-Files subdirectory
    har_files_dir = Path("HAR-Files")
    if har_files_dir.exists():
        har_files.extend(har_files_dir.glob("*.har"))

    return sorted(har_files)


def select_har_file(prompt, available_files, exclude_file=None):
    """Interactive HAR file selection"""
    if exclude_file:
        available_files = [f for f in available_files if f != exclude_file]

    if not available_files:
        print("No additional HAR files available!")
        return None

    print(f"\n{prompt}")
    print("-" * 40)

    for i, har_file in enumerate(available_files, 1):
        file_size = har_file.stat().st_size / (1024 * 1024)  # MB
        print(f"[{i}] {har_file.name} ({file_size:.1f} MB)")

    while True:
        try:
            choice = input(f"\nSelect HAR file (1-{len(available_files)}): ").strip()
            index = int(choice) - 1

            if 0 <= index < len(available_files):
                selected = available_files[index]
                print(f"Selected: {selected.name}")
                return selected
            else:
                print(f"Please enter a number between 1 and {len(available_files)}")

        except (ValueError, KeyboardInterrupt):
            print("Invalid input. Please enter a number.")
        except EOFError:
            return None


def run_har_breakdown(har_file, output_dir):
    """Run HAR breakdown using scripts/break_har_for_comparison.py"""
    print(f"\nBreaking down {har_file.name}...")

    cmd = [
        sys.executable,
        "scripts/break_har_for_comparison.py",
        "--har",
        str(har_file),
        "--output",
        output_dir,
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"Breakdown complete: {output_dir}")
        return os.path.join(output_dir, "har_breakdown.json")
    except subprocess.CalledProcessError as e:
        print(f"Breakdown failed: {e.stderr}")
        return None


def run_comparison_analysis(base_json, target_json, output_file):
    """Run comparison analysis using scripts/compare_har_analysis.py"""
    print(f"\nComparing HAR analyses...")

    cmd = [
        sys.executable,
        "scripts/compare_har_analysis.py",
        "--base",
        base_json,
        "--target",
        target_json,
        "--output",
        output_file,
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, encoding="utf-8"
        )
        print(f"Comparison complete: {output_file}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Comparison failed:")
        print(f"   Return code: {e.returncode}")
        print(f"   STDERR: {e.stderr}")
        print(f"   STDOUT: {e.stdout}")
        return False
    except Exception as e:
        print(f"Comparison error: {e}")
        return False


def generate_html_report(comparison_json, output_html):
    """Generate HTML report using scripts/generate_har_comparison_report.py"""
    print(f"\nGenerating HTML report...")

    cmd = [
        sys.executable,
        "scripts/generate_har_comparison_report.py",
        "report",
        "--comparison",
        comparison_json,
        "--output",
        output_html,
        "--template-style",
        "side-by-side",
        "--no-browser",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"HTML report generated: {output_html}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Report generation failed: {e.stderr}")
        print(f"Command output: {e.stdout}")
        return False


def open_report_in_browser(report_path):
    """Open the generated report in browser"""
    import webbrowser

    try:
        full_path = os.path.abspath(report_path)
        webbrowser.open(f"file://{full_path}")
        print(f"Report opened in browser: {report_path}")
        return True
    except Exception as e:
        print(f"Could not open browser: {e}")
        print(f"Report saved at: {os.path.abspath(report_path)}")
        return False


def show_comparison_summary(comparison_json):
    """Show a quick summary of the comparison results"""
    try:
        with open(comparison_json, "r", encoding="utf-8") as f:
            data = json.load(f)

        print(f"\nCOMPARISON SUMMARY")
        print("=" * 40)

        # Basic info
        metadata = data.get("metadata", {})
        print(f"Base File: {metadata.get('base_file', 'Unknown')}")
        print(f"Target File: {metadata.get('target_file', 'Unknown')}")

        # KPI changes
        kpi = data.get("kpi_changes", {})
        if "page_load_time" in kpi:
            plt = kpi["page_load_time"]
            direction = (
                "[UP]"
                if plt.get("direction") == "increased"
                else "[DOWN]" if plt.get("direction") == "decreased" else "[SAME]"
            )
            print(
                f"Page Load Time: {plt.get('base', 0):.1f}s → {plt.get('target', 0):.1f}s {direction} ({plt.get('percentage', 0):+.1f}%)"
            )

        if "total_requests" in kpi:
            tr = kpi["total_requests"]
            direction = (
                "[UP]"
                if tr.get("direction") == "increased"
                else "[DOWN]" if tr.get("direction") == "decreased" else "[SAME]"
            )
            print(
                f"Total Requests: {tr.get('base', 0)} → {tr.get('target', 0)} {direction} ({tr.get('percentage', 0):+.1f}%)"
            )

        if "total_size_mb" in kpi:
            ts = kpi["total_size_mb"]
            direction = (
                "[UP]"
                if ts.get("direction") == "increased"
                else "[DOWN]" if ts.get("direction") == "decreased" else "[SAME]"
            )
            print(
                f"Total Size: {ts.get('base', 0):.1f}MB → {ts.get('target', 0):.1f}MB {direction} ({ts.get('percentage', 0):+.1f}%)"
            )

        # Overall assessment
        summary = data.get("summary", {})
        overall_status = summary.get("overall_status", "Unknown")
        risk_level = summary.get("risk_level", "Unknown")

        status_icon = {
            "improved": "[OK]",
            "regressed": "[WARN]",
            "stable": "[SAME]",
        }.get(overall_status.lower(), "[?]")

        print(f"\nOverall Status: {status_icon} {overall_status.upper()}")
        print(f"Risk Level: {risk_level.upper()}")

    except Exception as e:
        print(f"Could not read comparison summary: {e}")


def main():
    """Main demo function"""
    print_header()

    # Find available HAR files
    har_files = find_har_files()

    if len(har_files) < 2:
        print("Need at least 2 HAR files for comparison!")
        print("Available HAR files:")
        for har in har_files:
            print(f"   - {har}")
        print("\nAdd more HAR files to the current directory or HAR-Files/ folder")
        return

    print(f"Found {len(har_files)} HAR files")

    # Select baseline HAR file
    baseline_har = select_har_file(
        "SELECT BASELINE HAR FILE (reference point):", har_files
    )
    if not baseline_har:
        print("No baseline file selected. Exiting.")
        return

    # Select target HAR file
    target_har = select_har_file(
        "SELECT TARGET HAR FILE (to compare against baseline):", har_files, baseline_har
    )
    if not target_har:
        print("No target file selected. Exiting.")
        return

    # Create output directory inside har_chunks
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    har_chunks_dir = "har_chunks"
    os.makedirs(har_chunks_dir, exist_ok=True)
    output_dir = os.path.join(har_chunks_dir, f"comparison_temp_{timestamp}")
    os.makedirs(output_dir, exist_ok=True)

    print(f"\nPROCESSING WORKFLOW")
    print(f"Output directory: {output_dir}")

    # Step 1: Break down baseline HAR
    baseline_breakdown_dir = os.path.join(output_dir, "baseline_breakdown")
    baseline_json = run_har_breakdown(baseline_har, baseline_breakdown_dir)
    if not baseline_json or not os.path.exists(baseline_json):
        print("Failed to process baseline HAR file")
        return

    # Step 2: Break down target HAR
    target_breakdown_dir = os.path.join(output_dir, "target_breakdown")
    target_json = run_har_breakdown(target_har, target_breakdown_dir)
    if not target_json or not os.path.exists(target_json):
        print("Failed to process target HAR file")
        return

    # Step 3: Perform comparison analysis
    comparison_json = os.path.join(output_dir, "comparison_analysis.json")
    if not run_comparison_analysis(baseline_json, target_json, comparison_json):
        print("Failed to perform comparison analysis")
        return

    # Step 4: Generate HTML report
    report_name = (
        f"comparison_report_{baseline_har.stem}_vs_{target_har.stem}_{timestamp}.html"
    )
    output_html = os.path.join("reports", report_name)
    os.makedirs("reports", exist_ok=True)

    if not generate_html_report(comparison_json, output_html):
        print("Failed to generate HTML report")
        return

    # Show summary
    show_comparison_summary(comparison_json)

    # Open in browser
    print(f"\nCOMPARISON COMPLETE!")
    print("=" * 40)
    open_report_in_browser(output_html)

    print(f"\nAll files saved in: {output_dir}")
    print(f"Final report: {output_html}")
    print("\nReview the HTML report for detailed performance comparison insights!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nDemo cancelled by user")
    except Exception as e:
        print(f"\nDemo failed: {e}")
        import traceback

        traceback.print_exc()
