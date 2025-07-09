#!/usr/bin/env python3
"""
HAR Comparison Template Test
============================
This script tests both the side-by-side and detailed templates to ensure they work correctly.
"""

import os
import sys
import json
from pathlib import Path
import subprocess
import webbrowser

def test_har_comparison_templates():
    """Test both HAR comparison templates"""
    print("🧪 Testing HAR Comparison Templates")
    print("=" * 50)
    
    # Ensure we have HAR files to work with
    har_files_dir = Path("HAR-Files")
    if not har_files_dir.exists():
        print("❌ HAR-Files directory not found")
        return False
    
    har_files = list(har_files_dir.glob("*.har"))
    if len(har_files) < 2:
        print("❌ Need at least 2 HAR files for comparison")
        return False
    
    base_har = har_files[0]
    target_har = har_files[1]
    
    print(f"📋 Base HAR: {base_har.name}")
    print(f"🎯 Target HAR: {target_har.name}")
    
    test_results = {
        "side-by-side": {"success": False, "file": None, "size": None},
        "detailed": {"success": False, "file": None, "size": None}
    }
    
    # Test both templates
    for template_style in ["side-by-side", "detailed"]:
        print(f"\n🔄 Testing {template_style} template...")
        
        try:
            # Run comparison with specific template
            output_dir = f"template_test_{template_style.replace('-', '_')}"
            
            cmd = [
                sys.executable, "demo_har_comparison.py",
                "--base", str(base_har),
                "--target", str(target_har),
                "--output", output_dir,
                "--template-style", template_style
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode == 0:
                # Check if report was generated
                report_file = Path(output_dir) / "comparison_report.html"
                if report_file.exists():
                    file_size = report_file.stat().st_size / 1024  # KB
                    test_results[template_style] = {
                        "success": True,
                        "file": str(report_file),
                        "size": f"{file_size:.1f} KB"
                    }
                    print(f"✅ {template_style} template: SUCCESS ({file_size:.1f} KB)")
                else:
                    print(f"❌ {template_style} template: Report file not found")
            else:
                print(f"❌ {template_style} template: Command failed")
                print(f"   Error: {result.stderr}")
                
        except Exception as e:
            print(f"❌ {template_style} template: Exception - {e}")
    
    # Summary
    print(f"\n📊 Test Results Summary")
    print("=" * 30)
    
    all_passed = True
    for template_style, result in test_results.items():
        status = "✅ PASS" if result["success"] else "❌ FAIL"
        size = result["size"] if result["success"] else "N/A"
        print(f"{template_style:12} | {status} | {size}")
        
        if not result["success"]:
            all_passed = False
    
    # Validate template content structure
    if all_passed:
        print(f"\n🔍 Validating template content...")
        
        for template_style, result in test_results.items():
            if result["success"]:
                report_file = result["file"]
                with open(report_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Basic validation checks
                checks = [
                    ("HTML structure", "<html" in content and "</html>" in content),
                    ("CSS styles", "<style>" in content or "stylesheet" in content),
                    ("Performance data", "Performance" in content),
                    ("Template variables rendered", "{{" not in content),  # No unrendered Jinja2
                ]
                
                print(f"\n   {template_style} template validation:")
                template_valid = True
                for check_name, check_result in checks:
                    status = "✅" if check_result else "❌"
                    print(f"   {status} {check_name}")
                    if not check_result:
                        template_valid = False
                
                if template_valid:
                    print(f"   ✅ {template_style} template is valid")
                else:
                    print(f"   ❌ {template_style} template has issues")
                    all_passed = False
    
    # Open reports for visual inspection
    if all_passed:
        print(f"\n🌐 Opening reports for visual inspection...")
        for template_style, result in test_results.items():
            if result["success"]:
                try:
                    webbrowser.open(f"file://{os.path.abspath(result['file'])}")
                    print(f"   Opened {template_style} report in browser")
                except Exception as e:
                    print(f"   Could not open {template_style} report: {e}")
    
    print(f"\n{'🎉 All tests passed!' if all_passed else '⚠️  Some tests failed'}")
    return all_passed

if __name__ == "__main__":
    test_har_comparison_templates()
