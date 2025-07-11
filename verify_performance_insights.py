#!/usr/bin/env python3
"""
Performance Insights Section Verification
"""
import json
import sys
from pathlib import Path

def verify_performance_insights():
    """Verify the Performance Insights section calculations"""
    
    print("🔍 PERFORMANCE INSIGHTS SECTION VERIFICATION")
    print("=" * 55)
    
    # Load analysis data
    analysis_file = Path("har_chunks/v4_reload_pie/agent_summary.json")
    with open(analysis_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    perf_summary = data.get('performance_summary', {})
    critical_issues = data.get('critical_issues', {})
    caching_analysis = data.get('caching_analysis', {})
    third_party_analysis = data.get('enhanced_third_party_analysis', {})
    
    print("\n📊 RAW DATA FOR INSIGHTS:")
    print(f"  • page_load_time: {perf_summary.get('page_load_time')}")
    print(f"  • dom_ready_time: {perf_summary.get('dom_ready_time')}")
    print(f"  • total_requests: {perf_summary.get('total_requests')}")
    print(f"  • failed_requests: {critical_issues.get('failed_requests')}")
    print(f"  • very_slow_requests: {critical_issues.get('very_slow_requests')}")
    print(f"  • no_cache_resources: {len(caching_analysis.get('no_cache_resources', []))}")
    print(f"  • third_party_domains: {third_party_analysis.get('total_third_party_domains')}")
    print(f"  • blocking_third_parties: {len(third_party_analysis.get('blocking_third_parties', []))}")
    
    # Calculate summary metrics
    largest_assets = data.get('largest_assets', [])
    total_asset_size = sum([asset.get('size_kb', 0) for asset in largest_assets])
    total_size_mb = round(total_asset_size / 1024, 1) if total_asset_size > 0 else 0
    
    slowest_requests = data.get('slowest_requests', [])
    avg_response_time = sum([req.get('time_ms', 0) for req in slowest_requests]) / len(slowest_requests) if slowest_requests else 0
    avg_response_time = round(avg_response_time)
    
    third_party_domains = third_party_analysis.get('total_third_party_domains', 0)
    blocking_resources = len(third_party_analysis.get('blocking_third_parties', []))
    
    print("\n📈 CALCULATED PERFORMANCE SUMMARY:")
    print(f"  • Total data transferred: {total_size_mb} MB")
    print(f"  • Average response time: {avg_response_time} ms")
    print(f"  • Third-party domains: {third_party_domains}")
    print(f"  • Blocking resources: {blocking_resources}")
    
    # Extract timing values
    page_load_str = str(perf_summary.get('page_load_time', '0s'))
    dom_ready_str = str(perf_summary.get('dom_ready_time', '0s'))
    
    try:
        load_time_sec = float(page_load_str.replace('s', '')) if 's' in page_load_str else float(page_load_str)
    except (ValueError, TypeError):
        load_time_sec = 0
    
    try:
        dom_time_sec = float(dom_ready_str.replace('s', '')) if 's' in dom_ready_str else float(dom_ready_str)
    except (ValueError, TypeError):
        dom_time_sec = 0
    
    total_requests = perf_summary.get('total_requests', 0)
    failed_requests = critical_issues.get('failed_requests', 0)
    very_slow_requests = critical_issues.get('very_slow_requests', 0)
    
    print("\n⚠️  EXPECTED CRITICAL ISSUES:")
    issues = []
    if load_time_sec > 10:
        issues.append(f"Critical: Page load time exceeds 10 seconds")
        print(f"  ✅ Critical: Page load time exceeds 10 seconds ({load_time_sec:.1f}s)")
    elif load_time_sec > 5:
        issues.append(f"Warning: Page load time exceeds 5 seconds")
        print(f"  ✅ Warning: Page load time exceeds 5 seconds ({load_time_sec:.1f}s)")
    
    if dom_time_sec > 5:
        issues.append(f"Critical: DOM ready time exceeds 5 seconds")
        print(f"  ✅ Critical: DOM ready time exceeds 5 seconds ({dom_time_sec:.1f}s)")
    elif dom_time_sec > 2:
        issues.append(f"Warning: DOM ready time exceeds 2 seconds")
        print(f"  ✅ Warning: DOM ready time exceeds 2 seconds ({dom_time_sec:.1f}s)")
    
    if total_requests > 100:
        issues.append(f"Critical request count: {total_requests} requests")
        print(f"  ✅ Critical request count: {total_requests} requests")
    elif total_requests > 50:
        issues.append(f"High request count: {total_requests} requests")
        print(f"  ✅ High request count: {total_requests} requests")
    
    if failed_requests > 0:
        issues.append(f"Some failed requests: {failed_requests} failures")
        print(f"  ✅ Some failed requests: {failed_requests} failures")
    
    print("\n💡 EXPECTED RECOMMENDATIONS:")
    recommendations = []
    if total_requests > 50:
        recommendations.append("Consider bundling smaller assets together")
        print("  ✅ Consider bundling smaller assets together")
    
    if failed_requests > 0:
        recommendations.append("Review and fix failing requests")
        print("  ✅ Review and fix failing requests")
    
    no_cache_count = len(caching_analysis.get('no_cache_resources', []))
    if no_cache_count > 0:
        recommendations.append(f"Add cache headers to {no_cache_count} resources")
        print(f"  ✅ Add cache headers to {no_cache_count} resources")
    
    print("\n🚨 EXPECTED PRIORITY ACTIONS:")
    priority_actions = []
    large_assets = [asset for asset in largest_assets if asset.get('size_kb', 0) > 1000]
    if load_time_sec > 10 and len(large_assets) > 0:
        priority_actions.append("Implement aggressive code splitting and lazy loading")
        print(f"  ✅ Implement aggressive code splitting and lazy loading ({len(large_assets)} large assets)")
    
    if blocking_resources > 5:
        priority_actions.append("Minimize blocking JavaScript and CSS")
        print(f"  ✅ Minimize blocking JavaScript and CSS ({blocking_resources} blocking resources)")
    
    print(f"\n📊 Issues: {len(issues)}, Recommendations: {len(recommendations)}, Priority Actions: {len(priority_actions)}")
    print("\n" + "=" * 55)
    print("📈 PERFORMANCE INSIGHTS VERIFICATION COMPLETE")

if __name__ == "__main__":
    verify_performance_insights()
