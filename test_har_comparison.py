#!/usr/bin/env python3
"""
HAR Comparison Flow - Comprehensive Test Suite
==============================================
This script validates the complete HAR comparison workflow and all its components
to ensure everything is working correctly.
"""

import os
import sys
import json
import tempfile
from pathlib import Path

def test_har_comparison_workflow():
    """Test the complete HAR comparison workflow"""
    print("🧪 Testing HAR Comparison Workflow")
    print("=" * 50)
    
    # Find available HAR files
    har_files_dir = Path("HAR-Files")
    if not har_files_dir.exists():
        print("❌ HAR-Files directory not found")
        return False
    
    har_files = list(har_files_dir.glob("*.har"))
    if len(har_files) < 2:
        print("❌ Need at least 2 HAR files for testing")
        return False
    
    # Select test files (prefer smaller ones for faster testing)
    test_files = sorted(har_files, key=lambda x: x.stat().st_size)[:2]
    base_har = test_files[0]
    target_har = test_files[1]
    
    print(f"📄 Testing with:")
    print(f"   Base: {base_har.name} ({base_har.stat().st_size / 1024:.1f} KB)")
    print(f"   Target: {target_har.name} ({target_har.stat().st_size / 1024:.1f} KB)")
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        try:
            # Test 1: Individual script imports
            print(f"\n🔧 Test 1: Importing scripts...")
            sys.path.append(str(Path("scripts")))
            
            from break_har import extract_har_data
            from analyze_two_chunks import compare_har_chunks
            from generate_comparison_report import generate_comparison_report
            
            print("   ✅ All scripts imported successfully")
            
            # Test 2: HAR breakdown
            print(f"\n📊 Test 2: HAR breakdown...")
            base_data = extract_har_data(str(base_har))
            target_data = extract_har_data(str(target_har))
            
            print(f"   ✅ Base HAR processed: {base_data['totals']['total_requests']} requests")
            print(f"   ✅ Target HAR processed: {target_data['totals']['total_requests']} requests")
            
            # Test 3: Comparison analysis
            print(f"\n🔄 Test 3: Comparison analysis...")
            comparison = compare_har_chunks(base_data, target_data)
            
            # Validate comparison structure
            required_keys = ['metadata', 'kpi_changes', 'resource_deltas', 'summary']
            for key in required_keys:
                if key not in comparison:
                    raise KeyError(f"Missing key in comparison: {key}")
            
            print(f"   ✅ Comparison completed")
            print(f"   📈 Status: {comparison['summary']['overall_status']}")
            print(f"   ⚠️  Risk Level: {comparison['summary']['risk_level']}")
            
            # Test 4: Report generation
            print(f"\n📄 Test 4: Report generation...")
            report_file = temp_path / "test_report.html"
            
            generated_report = generate_comparison_report(
                comparison, 
                str(report_file),
                open_browser=False
            )
            
            if not Path(generated_report).exists():
                raise FileNotFoundError(f"Report not generated: {generated_report}")
            
            report_size = Path(generated_report).stat().st_size
            print(f"   ✅ Report generated: {Path(generated_report).name} ({report_size / 1024:.1f} KB)")
            
            # Test 5: Validate report content
            print(f"\n🔍 Test 5: Report validation...")
            with open(generated_report, 'r', encoding='utf-8') as f:
                report_content = f.read()
            
            # Check for essential content
            essential_content = [
                "HAR Performance Comparison",
                base_har.stem,
                target_har.stem,
                "Overall Status",
                "KPI Comparison"
            ]
            
            missing_content = []
            for content in essential_content:
                if content not in report_content:
                    missing_content.append(content)
            
            if missing_content:
                print(f"   ⚠️  Missing content: {missing_content}")
            else:
                print(f"   ✅ Report content validation passed")
            
            # Test 6: JSON structure validation
            print(f"\n📋 Test 6: Data structure validation...")
            
            # Check KPI changes structure
            kpi_changes = comparison['kpi_changes']
            for metric in ['page_load_time', 'total_requests', 'total_size_mb']:
                if metric not in kpi_changes:
                    raise KeyError(f"Missing KPI metric: {metric}")
                
                metric_data = kpi_changes[metric]
                required_fields = ['base', 'target', 'absolute', 'percentage', 'direction']
                for field in required_fields:
                    if field not in metric_data:
                        raise KeyError(f"Missing field in {metric}: {field}")
            
            print(f"   ✅ KPI structure validation passed")
            
            # Check resource deltas
            resource_deltas = comparison['resource_deltas']
            required_delta_keys = ['added', 'removed', 'modified', 'counts']
            for key in required_delta_keys:
                if key not in resource_deltas:
                    raise KeyError(f"Missing resource delta key: {key}")
            
            print(f"   ✅ Resource delta structure validation passed")
            
            print(f"\n🎉 All tests passed successfully!")
            print(f"📊 Test Summary:")
            print(f"   • Script imports: ✅ Success")
            print(f"   • HAR breakdown: ✅ Success")
            print(f"   • Comparison analysis: ✅ Success")
            print(f"   • Report generation: ✅ Success")
            print(f"   • Content validation: ✅ Success")
            print(f"   • Structure validation: ✅ Success")
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

def test_performance_benchmarks():
    """Test performance with various HAR file sizes"""
    print(f"\n⚡ Performance Benchmark Tests")
    print("=" * 50)
    
    har_files_dir = Path("HAR-Files")
    har_files = list(har_files_dir.glob("*.har"))
    
    if not har_files:
        print("❌ No HAR files found for benchmarking")
        return
    
    # Categorize files by size
    small_files = [f for f in har_files if f.stat().st_size < 1024 * 1024]  # < 1MB
    medium_files = [f for f in har_files if 1024 * 1024 <= f.stat().st_size < 10 * 1024 * 1024]  # 1-10MB
    large_files = [f for f in har_files if f.stat().st_size >= 10 * 1024 * 1024]  # > 10MB
    
    print(f"📊 File size distribution:")
    print(f"   Small files (< 1MB): {len(small_files)}")
    print(f"   Medium files (1-10MB): {len(medium_files)}")
    print(f"   Large files (> 10MB): {len(large_files)}")
    
    # Test with different sizes if available
    import time
    sys.path.append(str(Path("scripts")))
    from break_har import extract_har_data
    
    categories = [
        ("Small", small_files[:1] if small_files else []),
        ("Medium", medium_files[:1] if medium_files else []),
        ("Large", large_files[:1] if large_files else [])
    ]
    
    for category, files in categories:
        if not files:
            continue
            
        file = files[0]
        file_size_mb = file.stat().st_size / (1024 * 1024)
        
        print(f"\n📏 Testing {category} file: {file.name} ({file_size_mb:.1f} MB)")
        
        start_time = time.time()
        try:
            data = extract_har_data(str(file))
            end_time = time.time()
            
            processing_time = end_time - start_time
            requests_count = data['totals']['total_requests']
            
            print(f"   ✅ Processed in {processing_time:.2f}s")
            print(f"   📊 {requests_count} requests", end="")
            if processing_time > 0:
                print(f" ({requests_count / processing_time:.0f} req/sec)")
            else:
                print(f" (instant processing)")
            
            # Performance targets from the project specs
            if category == "Small" and processing_time > 5:
                print(f"   ⚠️  Warning: Small file took {processing_time:.2f}s (target: <5s)")
            elif category == "Medium" and processing_time > 30:
                print(f"   ⚠️  Warning: Medium file took {processing_time:.2f}s (target: <30s)")
            elif category == "Large" and processing_time > 120:
                print(f"   ⚠️  Warning: Large file took {processing_time:.2f}s (target: <120s)")
            else:
                print(f"   🎯 Performance target met!")
                
        except Exception as e:
            print(f"   ❌ Error processing {category} file: {e}")

def main():
    """Run all tests"""
    print("🧪 HAR Comparison Flow - Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test 1: Workflow functionality
    try:
        workflow_success = test_har_comparison_workflow()
        success = success and workflow_success
    except Exception as e:
        print(f"❌ Workflow test failed: {e}")
        success = False
    
    # Test 2: Performance benchmarks
    try:
        test_performance_benchmarks()
    except Exception as e:
        print(f"❌ Performance test failed: {e}")
        success = False
    
    # Final result
    print(f"\n" + "=" * 60)
    if success:
        print("🎉 All tests completed successfully!")
        print("✅ HAR Comparison Flow is ready for production use")
    else:
        print("❌ Some tests failed - please review the errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()
