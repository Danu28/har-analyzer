#!/usr/bin/env python3
"""
Debug HAR Report Generation
"""
import json
import sys
import traceback
from pathlib import Path


def debug_report_generation():
    """Debug the report generation to find exact error location"""

    # Load the analysis data
    analysis_file = Path("har_chunks/v4_reload_pie/agent_summary.json")

    try:
        with open(analysis_file, "r", encoding="utf-8") as f:
            analysis_data = json.load(f)
    except Exception as e:
        print(f"ERROR loading analysis data: {e}")
        return

    # Import the report generator
    sys.path.append("scripts")
    from generate_single_har_report import generate_single_har_report

    try:
        # Try to generate the report with detailed error tracking
        output_file = generate_single_har_report(
            analysis_data=analysis_data,
            output_file="reports/debug_test.html",
            template_style="premium",
            open_browser=False,
        )
        print(f"✅ Report generated successfully: {output_file}")

    except Exception as e:
        print(f"❌ Error generating report: {e}")
        print("\n🔍 Full traceback:")
        traceback.print_exc()

        # Try to identify the specific problematic data
        print("\n🔍 Analyzing data types in analysis_data...")
        for key, value in analysis_data.items():
            print(f"  {key}: {type(value)}")
            if isinstance(value, dict):
                for subkey, subvalue in value.items():
                    print(f"    {subkey}: {type(subvalue)} = {subvalue}")
            elif isinstance(value, list) and len(value) > 0:
                print(f"    [0]: {type(value[0])} = {value[0]}")


if __name__ == "__main__":
    debug_report_generation()
