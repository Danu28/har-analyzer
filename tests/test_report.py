#!/usr/bin/env python3
"""
Test script for the HTML report generator
"""

import os
import json
from generate_html_report import HARHtmlReportGenerator

def test_report_generation():
    """Test the HTML report generation"""
    print("🧪 Testing HTML Report Generator")
    print("=" * 40)
    
    # Test with existing HAR data
    har_name = "v3_Pie_LP_reload_private_tab"
    
    generator = HARHtmlReportGenerator()
    
    try:
        # Test data loading
        print("📁 Loading HAR analysis data...")
        data = generator.load_analysis_data(har_name)
        print(f"✅ Loaded {len(data)} data sections")
        
        # Test analysis
        print("🔍 Analyzing performance issues...")
        analysis = generator.analyze_performance_issues()
        print(f"✅ Found {len(analysis['issues'])} issues")
        print(f"✅ Generated {len(analysis['recommendations'])} recommendations")
        
        # Test chart data
        print("📊 Generating chart data...")
        chart_data = generator.generate_resource_breakdown_chart()
        print(f"✅ Generated chart with {len(chart_data)} resource types")
        
        # Test HTML generation
        print("🌐 Generating HTML report...")
        report_file = generator.generate_html_report(har_name, "test_report.html")
        
        # Verify file exists and has content
        if os.path.exists(report_file):
            file_size = os.path.getsize(report_file)
            print(f"✅ HTML report generated: {report_file}")
            print(f"📏 File size: {file_size:,} bytes")
            
            # Check if it's a valid HTML file
            with open(report_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if content.startswith('<!DOCTYPE html>'):
                    print("✅ Valid HTML structure")
                else:
                    print("❌ Invalid HTML structure")
        else:
            print("❌ Report file not created")
            
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_report_generation()
