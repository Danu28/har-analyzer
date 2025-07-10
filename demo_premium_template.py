#!/usr/bin/env python3
"""
Premium Template Demo for HAR Analysis Reports
=============================================
Demonstrates the new premium template with comprehensive styling and features
"""

import sys
import subprocess
from pathlib import Path
import time

def run_command(cmd, description):
    """Run a command and show progress"""
    print(f"\n🚀 {description}")
    print(f"Command: {' '.join(cmd)}")
    
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Demonstrate premium template generation"""
    print("=" * 80)
    print("🎨 HAR-ANALYZE Premium Template Demo")
    print("=" * 80)
    print()
    print("This demo showcases the new premium template for single HAR analysis reports.")
    print("The premium template includes:")
    print("• Elegant gradient designs and animations")
    print("• Comprehensive performance metrics")
    print("• Interactive expandable sections")
    print("• Detailed third-party analysis")
    print("• Enhanced network performance insights")
    print("• Priority action recommendations")
    print("• Professional styling and responsive design")
    print()
    
    # Check if analysis data exists
    analysis_file = "har_chunks/HAR_Test/agent_summary.json"
    if not Path(analysis_file).exists():
        print("❌ Analysis data not found. Please run the following commands first:")
        print("   python scripts/break_har_file.py --har HAR-Files/HAR_Test.har")
        print("   python scripts/analyze_performance.py --input har_chunks/HAR_Test")
        return 1
    
    print("📊 Analysis data found. Generating reports with all template styles...")
    
    # Template styles to demonstrate
    templates = [
        ("detailed", "Comprehensive detailed analysis"),
        ("summary", "Concise overview report"),
        ("dashboard", "Widget-based dashboard view"),
        ("premium", "Premium with advanced features")
    ]
    
    generated_reports = []
    
    for style, description in templates:
        output_file = f"reports/HAR_Test_{style}_premium_demo.html"
        
        cmd = [
            sys.executable,
            "scripts/generate_single_har_report.py",
            "--analysis-file", analysis_file,
            "--template-style", style,
            "--output", output_file,
            "--no-browser"
        ]
        
        success = run_command(cmd, f"Generating {style} template report - {description}")
        
        if success:
            generated_reports.append((style, output_file, description))
            time.sleep(0.5)  # Brief pause for visual effect
    
    # Summary
    print("\n" + "=" * 80)
    print("📋 REPORT GENERATION SUMMARY")
    print("=" * 80)
    
    if generated_reports:
        print(f"✅ Successfully generated {len(generated_reports)} reports:")
        print()
        
        for style, output_file, description in generated_reports:
            file_size = Path(output_file).stat().st_size / 1024 if Path(output_file).exists() else 0
            print(f"   🎨 {style.upper():12} | {file_size:6.1f} KB | {description}")
            print(f"      📁 {output_file}")
            print()
        
        print("🌟 PREMIUM TEMPLATE HIGHLIGHTS:")
        print("   • Modern gradient header with animation effects")
        print("   • Performance grade showcase with color-coded metrics")
        print("   • Comprehensive insights grid with issue categorization")
        print("   • Interactive expandable sections for detailed analysis")
        print("   • Enhanced third-party domain impact analysis")
        print("   • Network performance with DNS and SSL timing")
        print("   • Priority action plan with immediate recommendations")
        print("   • Professional styling with hover effects and transitions")
        print()
        
        print("💡 USAGE EXAMPLES:")
        print("   # Generate premium report")
        print("   python scripts/generate_single_har_report.py \\")
        print("     --analysis-file har_chunks/HAR_Test/agent_summary.json \\")
        print("     --template-style premium")
        print()
        print("   # Generate with custom template")
        print("   python scripts/generate_single_har_report.py \\")
        print("     --analysis-file har_chunks/HAR_Test/agent_summary.json \\")
        print("     --template-file templates/custom_template.html")
        print()
        
        print("🔗 OPENING PREMIUM REPORT...")
        
        # Find and open the premium report
        premium_report = None
        for style, output_file, _ in generated_reports:
            if style == "premium":
                premium_report = output_file
                break
        
        if premium_report and Path(premium_report).exists():
            import webbrowser
            try:
                webbrowser.open(f"file://{Path(premium_report).absolute()}")
                print(f"🌐 Premium report opened: {premium_report}")
            except Exception as e:
                print(f"⚠️  Could not open browser: {e}")
                print(f"   Please manually open: {premium_report}")
        
    else:
        print("❌ No reports were generated successfully.")
        return 1
    
    print("\n🎉 Premium template demo completed successfully!")
    print("   Check the reports/ directory for all generated files.")
    return 0

if __name__ == "__main__":
    exit(main())
