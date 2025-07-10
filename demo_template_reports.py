#!/usr/bin/env python3
"""
Template-Based HAR Report Generation Demo
========================================
Demonstrates the new template-based approach for generating single HAR analysis reports
with multiple template styles (detailed, summary, dashboard).
"""

import sys
import os
from pathlib import Path
import subprocess

def main():
    """Demonstrate template-based report generation"""
    
    print("🚀 HAR-ANALYZE Template-Based Report Generation Demo")
    print("=" * 60)
    
    # Check if we have analysis data
    test_analysis_file = "har_chunks/HAR_Test/agent_summary.json"
    if not os.path.exists(test_analysis_file):
        print("❌ Analysis data not found!")
        print(f"   Looking for: {test_analysis_file}")
        print("\n💡 To generate analysis data, run:")
        print("   1. python scripts/break_har_file.py --har HAR-Files/HAR_Test.har")
        print("   2. python scripts/analyze_performance.py --input har_chunks/HAR_Test")
        return
    
    print(f"✅ Found analysis data: {test_analysis_file}")
    
    # Demo different template styles
    template_styles = ["detailed", "summary", "dashboard"]
    
    for style in template_styles:
        print(f"\n📊 Generating {style.upper()} report...")
        
        output_file = f"reports/HAR_Test_{style}_demo.html"
        
        # Run the generation script
        cmd = [
            sys.executable, 
            "scripts/generate_single_har_report.py",
            "--analysis-file", test_analysis_file,
            "--template-style", style,
            "--output", output_file,
            "--no-browser"
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"   ✅ Generated: {output_file}")
            
            # Get file size
            if os.path.exists(output_file):
                size_kb = os.path.getsize(output_file) / 1024
                print(f"   📁 Size: {size_kb:.1f} KB")
        except subprocess.CalledProcessError as e:
            print(f"   ❌ Error generating {style} report:")
            print(f"   {e.stderr}")
    
    print("\n🎯 Template Style Comparison:")
    print("─" * 40)
    print("• DETAILED  - Comprehensive analysis with all sections")
    print("• SUMMARY   - Concise overview with key metrics")
    print("• DASHBOARD - Widget-based visualization layout")
    
    print("\n📂 Generated Reports:")
    reports_dir = Path("reports")
    if reports_dir.exists():
        demo_reports = list(reports_dir.glob("HAR_Test_*_demo.html"))
        for report in demo_reports:
            size_kb = report.stat().st_size / 1024
            print(f"   📄 {report.name} ({size_kb:.1f} KB)")
    
    print("\n🌐 To view reports, open them in a web browser:")
    print("   file:///c:/Users/KaDh550/Desktop/HAR-analyze/reports/")
    
    print("\n🔧 Advanced Usage:")
    print("   # Custom template")
    print("   python scripts/generate_single_har_report.py \\")
    print("     --analysis-file har_chunks/MyHAR/agent_summary.json \\")
    print("     --template-file my_custom_template.html \\")
    print("     --output my_report.html")
    
    print("\n   # Different styles")
    print("   python scripts/generate_single_har_report.py \\")
    print("     --analysis-file har_chunks/MyHAR/agent_summary.json \\")
    print("     --template-style summary")
    
    print("\n🎊 Template-based report generation demo complete!")
    print("   The new approach provides:")
    print("   • Jinja2 templating with fallback to simple substitution")
    print("   • Multiple professional template styles")
    print("   • Responsive design and interactive elements")
    print("   • Easy customization and extension")
    print("   • Consistent with HAR comparison report approach")

if __name__ == "__main__":
    # Change to script directory for relative paths
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    main()
