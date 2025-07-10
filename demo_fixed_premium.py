#!/usr/bin/env python3
"""
Demo script to showcase the fixed premium template
Demonstrates that failed requests are now displayed as counts instead of raw data
"""
import subprocess
import sys
import webbrowser
import os
from pathlib import Path

def main():
    """Generate and open the fixed premium report"""
    
    print("=" * 60)
    print("🎯 HAR Analysis Premium Template - Fixed Version Demo")
    print("=" * 60)
    print()
    
    # Paths
    base_dir = Path(__file__).parent
    analysis_file = base_dir / "har_chunks" / "HAR_Test" / "agent_summary.json"
    output_file = base_dir / "reports" / "HAR_Test_premium_fixed_demo.html"
    template_file = base_dir / "templates" / "har_single_premium.html"
    
    if not analysis_file.exists():
        print("❌ Error: Analysis file not found!")
        print(f"   Expected: {analysis_file}")
        print("   Please run the analysis first:")
        print("   python scripts/break_har_file.py HAR-Files/HAR_Test.har")
        print("   python scripts/analyze_performance.py har_chunks/HAR_Test")
        return 1
    
    # Generate report
    print("📊 Generating premium report with fixed failed requests display...")
    
    cmd = [
        sys.executable, 
        "scripts/generate_single_har_report.py",
        "--analysis-file", str(analysis_file),
        "--output", str(output_file),
        "--template-file", str(template_file),
        "--no-browser"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
        
        if result.returncode == 0:
            print("✅ Report generated successfully!")
            print(f"   Output: {output_file}")
            print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB")
            print()
            
            # Open in browser
            print("🌐 Opening report in browser...")
            webbrowser.open(f"file:///{output_file.resolve()}")
            print()
            
            print("🎉 SUCCESS: Premium template fixed!")
            print("   The 'Failed Requests' metric now displays as a clean count")
            print("   instead of raw data that caused UI overflow.")
            print()
            
            print("📋 Key fixes applied:")
            print("   • Failed requests metric shows count (integer)")
            print("   • Clean, professional appearance in metrics grid")
            print("   • Consistent use of failed_requests_count variable")
            print("   • Fixed both inline and external template versions")
            print()
            
            return 0
        else:
            print("❌ Error generating report:")
            print(result.stderr)
            return 1
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
