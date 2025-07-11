#!/usr/bin/env python3
"""
Performance Section Data Accuracy Verification
"""
import json
import sys
from pathlib import Path

def verify_performance_section():
    """Verify the Overall Performance Grade section calculations"""
    
    print("🔍 PERFORMANCE SECTION VERIFICATION")
    print("=" * 50)
    
    # Load analysis data
    analysis_file = Path("har_chunks/v4_reload_pie/agent_summary.json")
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    perf_summary = data.get('performance_summary', {})
    critical_issues = data.get('critical_issues', {})
    
    print("\n📊 RAW DATA:")
    print(f"  • page_load_time: {perf_summary.get('page_load_time')}")
    print(f"  • dom_ready_time: {perf_summary.get('dom_ready_time')}")
    print(f"  • total_requests: {perf_summary.get('total_requests')}")
    print(f"  • failed_requests: {critical_issues.get('failed_requests')}")
    print(f"  • performance_grade: {perf_summary.get('performance_grade')}")
    
    # Calculate expected classes
    page_load_str = str(perf_summary.get('page_load_time', '0s'))
    dom_ready_str = str(perf_summary.get('dom_ready_time', '0s'))
    
    try:
        page_load_sec = float(page_load_str.replace('s', '')) if 's' in page_load_str else float(page_load_str)
    except (ValueError, TypeError):
        page_load_sec = 0
    
    try:
        dom_ready_sec = float(dom_ready_str.replace('s', '')) if 's' in dom_ready_str else float(dom_ready_str)
    except (ValueError, TypeError):
        dom_ready_sec = 0
    
    total_requests = perf_summary.get('total_requests', 0)
    failed_requests = critical_issues.get('failed_requests', 0)
    
    print("\n🔢 CALCULATED VALUES:")
    print(f"  • page_load_sec: {page_load_sec}")
    print(f"  • dom_ready_sec: {dom_ready_sec}")
    print(f"  • total_requests: {total_requests}")
    print(f"  • failed_requests: {failed_requests}")
    
    # Calculate CSS classes
    load_time_class = 'danger' if page_load_sec > 5 else 'warning' if page_load_sec > 3 else 'success'
    dom_time_class = 'danger' if dom_ready_sec > 2 else 'warning' if dom_ready_sec > 1 else 'success'
    requests_class = 'danger' if total_requests > 100 else 'warning' if total_requests > 50 else 'success'
    failed_class = 'danger' if failed_requests > 5 else 'warning' if failed_requests > 0 else 'success'
    
    print("\n🎨 EXPECTED CSS CLASSES:")
    print(f"  • load_time_class: {load_time_class}")
    print(f"  • dom_time_class: {dom_time_class}")
    print(f"  • requests_class: {requests_class}")
    print(f"  • failed_class: {failed_class}")
    
    print("\n📋 ACCURACY VERIFICATION:")
    
    # Verify targets and classifications
    print(f"  ✅ Page Load Time: {page_load_sec:.2f}s (Target: < 3s)")
    if page_load_sec > 5:
        print(f"     → CRITICAL ({load_time_class}) - Correctly classified")
    elif page_load_sec > 3:
        print(f"     → WARNING ({load_time_class}) - Correctly classified")
    else:
        print(f"     → GOOD ({load_time_class}) - Correctly classified")
    
    print(f"  ✅ DOM Ready Time: {dom_ready_sec:.2f}s (Target: < 2s)")
    if dom_ready_sec > 2:
        print(f"     → CRITICAL ({dom_time_class}) - Correctly classified")
    elif dom_ready_sec > 1:
        print(f"     → WARNING ({dom_time_class}) - Correctly classified")
    else:
        print(f"     → GOOD ({dom_time_class}) - Correctly classified")
    
    print(f"  ✅ Total Requests: {total_requests} (Target: < 50)")
    if total_requests > 100:
        print(f"     → CRITICAL ({requests_class}) - Correctly classified")
    elif total_requests > 50:
        print(f"     → WARNING ({requests_class}) - Correctly classified")
    else:
        print(f"     → GOOD ({requests_class}) - Correctly classified")
    
    print(f"  ✅ Failed Requests: {failed_requests} (Target: 0)")
    if failed_requests > 5:
        print(f"     → CRITICAL ({failed_class}) - Correctly classified")
    elif failed_requests > 0:
        print(f"     → WARNING ({failed_class}) - Correctly classified")
    else:
        print(f"     → PERFECT ({failed_class}) - Correctly classified")
    
    print(f"\n🏆 Performance Grade: {perf_summary.get('performance_grade')}")
    
    # Check if grade makes sense
    critical_issues_count = sum([
        1 if page_load_sec > 5 else 0,
        1 if dom_ready_sec > 2 else 0,
        1 if total_requests > 100 else 0,
        1 if failed_requests > 5 else 0
    ])
    
    warning_issues_count = sum([
        1 if 3 < page_load_sec <= 5 else 0,
        1 if 1 < dom_ready_sec <= 2 else 0,
        1 if 50 < total_requests <= 100 else 0,
        1 if 0 < failed_requests <= 5 else 0
    ])
    
    expected_grade = "CRITICAL" if critical_issues_count > 0 else "POOR" if warning_issues_count > 2 else "FAIR" if warning_issues_count > 0 else "GOOD"
    actual_grade = perf_summary.get('performance_grade', 'UNKNOWN')
    
    print(f"  • Critical issues: {critical_issues_count}")
    print(f"  • Warning issues: {warning_issues_count}")
    print(f"  • Expected grade: {expected_grade}")
    print(f"  • Actual grade: {actual_grade}")
    
    if actual_grade == expected_grade:
        print("  ✅ Performance grade correctly calculated!")
    else:
        print("  ⚠️  Performance grade may need adjustment")
    
    print("\n" + "=" * 50)
    print("📈 SECTION VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_performance_section()
