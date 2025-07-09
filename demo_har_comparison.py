#!/usr/bin/env python3
"""
HAR Comparison Flow Demonstration Script
=======================================
This script demonstrates the complete HAR comparison workflow:
1. Break down two HAR files using break_har.py
2. Compare the structured data using analyze_two_chunks.py
3. Generate an HTML comparison report using generate_comparison_report.py

Usage:
    python demo_har_comparison.py --base base.har --target target.har
"""

import os
import sys
import json
import argparse
from pathlib import Path

# Add scripts directory to path for imports
sys.path.append(str(Path(__file__).parent / "scripts"))

try:
    from break_har import extract_har_data
    from analyze_two_chunks import compare_har_chunks, save_comparison_analysis
    from generate_comparison_report import generate_comparison_report
except ImportError as e:
    print(f"❌ Error importing HAR analysis modules: {e}")
    print("Make sure all required scripts are in the scripts/ directory")
    sys.exit(1)

def run_har_comparison_flow(base_har_path: str, target_har_path: str, output_dir: str = None, template_style: str = "side-by-side") -> dict:
    """
    Run the complete HAR comparison flow
    
    Args:
        base_har_path: Path to the base/baseline HAR file
        target_har_path: Path to the target/comparison HAR file
        output_dir: Optional output directory for results
        template_style: Report template style ('side-by-side' or 'detailed')
        
    Returns:
        Dictionary containing all generated file paths and results
    """
    print("🚀 Starting HAR Comparison Flow")
    print("=" * 50)
    
    # Validate input files
    base_path = Path(base_har_path)
    target_path = Path(target_har_path)
    
    if not base_path.exists():
        raise FileNotFoundError(f"Base HAR file not found: {base_har_path}")
    if not target_path.exists():
        raise FileNotFoundError(f"Target HAR file not found: {target_har_path}")
    
    # Set up output directory
    if not output_dir:
        timestamp = Path().cwd().name  # Use current directory as timestamp reference
        output_dir = f"har_comparison_{base_path.stem}_vs_{target_path.stem}"
    
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    results = {
        'base_har': str(base_path),
        'target_har': str(target_path),
        'output_dir': str(output_path),
        'generated_files': {}
    }
    
    try:
        # Step 1: Break down base HAR file
        print(f"\n📊 Step 1: Breaking down base HAR file")
        print(f"   File: {base_path.name}")
        base_data = extract_har_data(str(base_path))
        
        base_breakdown_file = output_path / "base_har_breakdown.json"
        with open(base_breakdown_file, 'w', encoding='utf-8') as f:
            json.dump(base_data, f, indent=2)
        results['generated_files']['base_breakdown'] = str(base_breakdown_file)
        
        # Step 2: Break down target HAR file
        print(f"\n📊 Step 2: Breaking down target HAR file")
        print(f"   File: {target_path.name}")
        target_data = extract_har_data(str(target_path))
        
        target_breakdown_file = output_path / "target_har_breakdown.json"
        with open(target_breakdown_file, 'w', encoding='utf-8') as f:
            json.dump(target_data, f, indent=2)
        results['generated_files']['target_breakdown'] = str(target_breakdown_file)
        
        # Step 3: Compare the two breakdowns
        print(f"\n🔄 Step 3: Analyzing differences between HAR files")
        comparison_data = compare_har_chunks(base_data, target_data)
        
        comparison_file = output_path / "comparison_analysis.json"
        save_comparison_analysis(comparison_data, str(comparison_file))
        results['generated_files']['comparison_analysis'] = str(comparison_file)
        
        # Step 4: Generate HTML comparison report
        print(f"\n📄 Step 4: Generating HTML comparison report")
        report_file = output_path / "comparison_report.html"
        generated_report = generate_comparison_report(
            comparison_data, 
            str(report_file),
            template_style=template_style,  # Use the specified template style
            open_browser=False  # Don't auto-open in demo
        )
        results['generated_files']['html_report'] = generated_report
        
        # Print summary
        print(f"\n✅ HAR Comparison Flow Complete!")
        print(f"📁 Output directory: {output_path}")
        print(f"📊 Base HAR: {base_data['totals']['total_requests']} requests, {base_data['totals']['total_size_mb']:.2f} MB")
        print(f"📊 Target HAR: {target_data['totals']['total_requests']} requests, {target_data['totals']['total_size_mb']:.2f} MB")
        
        # Show key findings
        summary = comparison_data['summary']
        print(f"\n🎯 Key Findings:")
        print(f"   Overall Status: {summary['overall_status'].upper()}")
        print(f"   Risk Level: {summary['risk_level'].upper()}")
        for finding in summary['key_findings'][:3]:  # Show top 3 findings
            print(f"   • {finding}")
        
        # Show generated files
        print(f"\n📄 Generated Files:")
        for file_type, file_path in results['generated_files'].items():
            file_size = Path(file_path).stat().st_size / 1024  # KB
            print(f"   • {file_type}: {Path(file_path).name} ({file_size:.1f} KB)")
        
        results['success'] = True
        results['summary'] = summary
        
        return results
        
    except Exception as e:
        print(f"\n❌ Error in HAR comparison flow: {e}")
        results['success'] = False
        results['error'] = str(e)
        return results

def list_available_har_files():
    """List available HAR files in the HAR-Files directory"""
    har_files_dir = Path("HAR-Files")
    if not har_files_dir.exists():
        print("❌ HAR-Files directory not found")
        return []
    
    har_files = list(har_files_dir.glob("*.har"))
    if not har_files:
        print("❌ No HAR files found in HAR-Files directory")
        return []
    
    print(f"📁 Available HAR files in {har_files_dir}:")
    for i, har_file in enumerate(har_files, 1):
        file_size = har_file.stat().st_size / (1024 * 1024)  # MB
        print(f"   [{i}] {har_file.name} ({file_size:.2f} MB)")
    
    return har_files

def main():
    parser = argparse.ArgumentParser(description="Demonstrate HAR comparison flow")
    parser.add_argument('--base', help='Base HAR file path')
    parser.add_argument('--target', help='Target HAR file path')
    parser.add_argument('--output', help='Output directory for results')
    parser.add_argument('--template-style', choices=['side-by-side', 'detailed'], 
                       default='side-by-side', help='Report template style (default: side-by-side)')
    parser.add_argument('--list', action='store_true', help='List available HAR files')
    parser.add_argument('--demo', action='store_true', help='Run demo with first two available HAR files')
    
    args = parser.parse_args()
    
    # List available files if requested
    if args.list:
        list_available_har_files()
        return
    
    # Auto-demo mode
    if args.demo:
        har_files = list_available_har_files()
        if len(har_files) < 2:
            print("❌ Need at least 2 HAR files for demo")
            return
        
        print(f"\n🎬 Running demo comparison:")
        print(f"   Base: {har_files[0].name}")
        print(f"   Target: {har_files[1].name}")
        
        results = run_har_comparison_flow(str(har_files[0]), str(har_files[1]), template_style=args.template_style)
        
        if results['success']:
            print(f"\n🎉 Demo completed successfully!")
            print(f"   View the report: {results['generated_files']['html_report']}")
        else:
            print(f"❌ Demo failed: {results['error']}")
        
        return
    
    # Manual mode - require both base and target files
    if not args.base or not args.target:
        print("❌ Please provide both --base and --target HAR files")
        print("   Or use --demo to run with available files")
        print("   Or use --list to see available HAR files")
        parser.print_help()
        return
    
    # Run comparison flow
    try:
        results = run_har_comparison_flow(args.base, args.target, args.output, args.template_style)
        
        if results['success']:
            print(f"\n🎉 Comparison completed successfully!")
            print(f"   View the report: {results['generated_files']['html_report']}")
        else:
            print(f"❌ Comparison failed: {results['error']}")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
