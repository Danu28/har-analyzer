#!/usr/bin/env python3
"""
HAR Comparison Analysis - Compare Two HAR Chunks
================================================
This script analyzes two structured HAR breakdowns (base vs target) to identify
performance changes, resource deltas, and generate comparison insights.

Features:
- Resource deltas (added/removed/modified URLs)
- KPI changes (load time, size, request count)
- Endpoint timing comparisons
- Resource type aggregations
- Performance regression detection
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from urllib.parse import urlparse

def compare_har_chunks(base_data: Dict[str, Any], target_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Compare two HAR chunk structures and generate comparison analysis
    
    Args:
        base_data: Baseline HAR structured data
        target_data: Target HAR structured data for comparison
        
    Returns:
        Dictionary containing comprehensive comparison analysis
    """
    print("🔄 Analyzing HAR comparison...")
    
    # Extract basic info
    base_name = base_data['metadata']['file_name']
    target_name = target_data['metadata']['file_name']
    
    print(f"📊 Base: {base_name} ({base_data['totals']['total_requests']} requests)")
    print(f"📊 Target: {target_name} ({target_data['totals']['total_requests']} requests)")
    
    # Perform comprehensive comparison
    comparison = {
        'metadata': {
            'base_file': base_name,
            'target_file': target_name,
            'comparison_timestamp': Path().cwd().name,  # Use current time as reference
        },
        'kpi_changes': _compare_kpis(base_data, target_data),
        'resource_deltas': _analyze_resource_deltas(base_data, target_data),
        'endpoint_timing_diffs': _compare_endpoint_timings(base_data, target_data),
        'resource_type_aggregates': _compare_resource_types(base_data, target_data),
        'performance_regression': _detect_performance_regression(base_data, target_data),
        'third_party_changes': _analyze_third_party_changes(base_data, target_data),
        'size_changes': _analyze_size_changes(base_data, target_data),
        'failed_requests_comparison': _compare_failed_requests(base_data, target_data)
    }
    
    # Generate summary
    comparison['summary'] = _generate_comparison_summary(comparison)
    
    return comparison

def _compare_kpis(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Compare key performance indicators between base and target"""
    
    base_metrics = base_data['metrics']
    target_metrics = target_data['metrics']
    base_totals = base_data['totals']
    target_totals = target_data['totals']
    
    def calculate_change(base_val, target_val, is_percentage=False):
        if base_val == 0:
            return {
                'base': base_val,
                'target': target_val,
                'absolute': target_val, 
                'percentage': 'N/A', 
                'direction': 'new'
            }
        
        absolute_change = target_val - base_val
        percentage_change = (absolute_change / base_val) * 100
        direction = 'increased' if absolute_change > 0 else 'decreased' if absolute_change < 0 else 'unchanged'
        
        return {
            'base': base_val,
            'target': target_val,
            'absolute': absolute_change,
            'percentage': round(percentage_change, 2),
            'direction': direction
        }
    
    return {
        'page_load_time': calculate_change(
            base_metrics.get('page_load_time', 0),
            target_metrics.get('page_load_time', 0)
        ),
        'dom_ready_time': calculate_change(
            base_metrics.get('dom_ready_time', 0),
            target_metrics.get('dom_ready_time', 0)
        ),
        'total_requests': calculate_change(
            base_totals['total_requests'],
            target_totals['total_requests']
        ),
        'total_size_mb': calculate_change(
            base_totals['total_size_mb'],
            target_totals['total_size_mb']
        ),
        'failed_requests': calculate_change(
            base_totals['failed_count'],
            target_totals['failed_count']
        ),
        'slow_requests': calculate_change(
            base_totals['slow_count'],
            target_totals['slow_count']
        ),
        'avg_request_time': calculate_change(
            base_metrics.get('avg_request_time', 0),
            target_metrics.get('avg_request_time', 0)
        ),
        'max_request_time': calculate_change(
            base_metrics.get('max_request_time', 0),
            target_metrics.get('max_request_time', 0)
        ),
        'performance_grade_change': {
            'base': base_metrics.get('performance_grade', 'UNKNOWN'),
            'target': target_metrics.get('performance_grade', 'UNKNOWN'),
            'improved': _is_grade_improved(
                base_metrics.get('performance_grade', 'UNKNOWN'),
                target_metrics.get('performance_grade', 'UNKNOWN')
            )
        }
    }

def _analyze_resource_deltas(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Analyze added, removed, and modified resources"""
    
    base_urls = {req['url']: req for req in base_data['requests']}
    target_urls = {req['url']: req for req in target_data['requests']}
    
    base_url_set = set(base_urls.keys())
    target_url_set = set(target_urls.keys())
    
    added_urls = target_url_set - base_url_set
    removed_urls = base_url_set - target_url_set
    common_urls = base_url_set & target_url_set
    
    # Analyze modified resources (same URL, different properties)
    modified_resources = []
    for url in common_urls:
        base_req = base_urls[url]
        target_req = target_urls[url]
        
        changes = {}
        if base_req['size'] != target_req['size']:
            changes['size'] = {
                'base': base_req['size'],
                'target': target_req['size'],
                'delta': target_req['size'] - base_req['size']
            }
        
        if base_req['time'] != target_req['time']:
            changes['time'] = {
                'base': base_req['time'],
                'target': target_req['time'],
                'delta': target_req['time'] - base_req['time']
            }
        
        if base_req['status'] != target_req['status']:
            changes['status'] = {
                'base': base_req['status'],
                'target': target_req['status']
            }
        
        if changes:
            modified_resources.append({
                'url': url,
                'domain': target_req['domain'],
                'resource_type': target_req['resource_type'],
                'changes': changes
            })
    
    return {
        'added': [
            {
                'url': url,
                'domain': target_urls[url]['domain'],
                'resource_type': target_urls[url]['resource_type'],
                'size': target_urls[url]['size'],
                'time': target_urls[url]['time']
            }
            for url in added_urls
        ],
        'removed': [
            {
                'url': url,
                'domain': base_urls[url]['domain'],
                'resource_type': base_urls[url]['resource_type'],
                'size': base_urls[url]['size'],
                'time': base_urls[url]['time']
            }
            for url in removed_urls
        ],
        'modified': modified_resources,
        'counts': {
            'added': len(added_urls),
            'removed': len(removed_urls),
            'modified': len(modified_resources),
            'unchanged': len(common_urls) - len(modified_resources)
        }
    }

def _compare_endpoint_timings(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Compare timing differences for common endpoints"""
    
    base_urls = {req['url']: req for req in base_data['requests']}
    target_urls = {req['url']: req for req in target_data['requests']}
    
    common_urls = set(base_urls.keys()) & set(target_urls.keys())
    
    timing_comparisons = []
    for url in common_urls:
        base_req = base_urls[url]
        target_req = target_urls[url]
        
        # Compare total time
        time_delta = target_req['time'] - base_req['time']
        
        # Compare individual timing components
        timing_deltas = {}
        for timing_key in ['dns', 'connect', 'ssl', 'send', 'wait', 'receive']:
            base_timing = base_req['timings'].get(timing_key, 0)
            target_timing = target_req['timings'].get(timing_key, 0)
            if base_timing > 0 and target_timing > 0:
                timing_deltas[timing_key] = target_timing - base_timing
        
        # Only include if there's a significant change (>10ms or >10% change)
        if abs(time_delta) > 10 or (base_req['time'] > 0 and abs(time_delta / base_req['time']) > 0.1):
            timing_comparisons.append({
                'url': url,
                'domain': target_req['domain'],
                'resource_type': target_req['resource_type'],
                'base_time': base_req['time'],
                'target_time': target_req['time'],
                'time_delta': time_delta,
                'percentage_change': round((time_delta / base_req['time']) * 100, 2) if base_req['time'] > 0 else 'N/A',
                'timing_deltas': timing_deltas
            })
    
    # Sort by absolute time delta (worst regressions first)
    timing_comparisons.sort(key=lambda x: abs(x['time_delta']), reverse=True)
    
    return {
        'comparisons': timing_comparisons[:20],  # Top 20 changes
        'summary': {
            'total_compared': len(common_urls),
            'with_changes': len(timing_comparisons),
            'improved_count': len([c for c in timing_comparisons if c['time_delta'] < 0]),
            'regressed_count': len([c for c in timing_comparisons if c['time_delta'] > 0])
        }
    }

def _compare_resource_types(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Compare resource type aggregations between base and target"""
    
    base_breakdown = base_data['metrics'].get('resource_breakdown', {})
    target_breakdown = target_data['metrics'].get('resource_breakdown', {})
    
    all_types = set(base_breakdown.keys()) | set(target_breakdown.keys())
    
    comparisons = {}
    for resource_type in all_types:
        base_stats = base_breakdown.get(resource_type, {'count': 0, 'size': 0, 'time': 0})
        target_stats = target_breakdown.get(resource_type, {'count': 0, 'size': 0, 'time': 0})
        
        comparisons[resource_type] = {
            'count': {
                'base': base_stats['count'],
                'target': target_stats['count'],
                'delta': target_stats['count'] - base_stats['count']
            },
            'size': {
                'base': base_stats['size'],
                'target': target_stats['size'],
                'delta': target_stats['size'] - base_stats['size'],
                'delta_mb': round((target_stats['size'] - base_stats['size']) / (1024 * 1024), 2)
            },
            'time': {
                'base': base_stats['time'],
                'target': target_stats['time'],
                'delta': target_stats['time'] - base_stats['time']
            }
        }
    
    return comparisons

def _detect_performance_regression(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Detect performance regressions and improvements"""
    
    base_metrics = base_data['metrics']
    target_metrics = target_data['metrics']
    
    regressions = []
    improvements = []
    
    # Check load time regression
    base_load = base_metrics.get('page_load_time', 0)
    target_load = target_metrics.get('page_load_time', 0)
    load_delta = target_load - base_load
    
    if load_delta > 0.5:  # >500ms regression
        regressions.append({
            'type': 'page_load_time',
            'description': f"Page load time increased by {load_delta:.2f}s",
            'severity': 'high' if load_delta > 2.0 else 'medium'
        })
    elif load_delta < -0.5:  # >500ms improvement
        improvements.append({
            'type': 'page_load_time',
            'description': f"Page load time improved by {abs(load_delta):.2f}s"
        })
    
    # Check request count increase
    base_requests = base_data['totals']['total_requests']
    target_requests = target_data['totals']['total_requests']
    request_delta = target_requests - base_requests
    
    if request_delta > 10:  # >10 new requests
        regressions.append({
            'type': 'request_count',
            'description': f"Request count increased by {request_delta} requests",
            'severity': 'medium' if request_delta > 50 else 'low'
        })
    
    # Check total size increase
    base_size = base_data['totals']['total_size_mb']
    target_size = target_data['totals']['total_size_mb']
    size_delta = target_size - base_size
    
    if size_delta > 1.0:  # >1MB increase
        regressions.append({
            'type': 'total_size',
            'description': f"Total size increased by {size_delta:.2f}MB",
            'severity': 'high' if size_delta > 5.0 else 'medium'
        })
    
    # Check failed requests
    base_failed = base_data['totals']['failed_count']
    target_failed = target_data['totals']['failed_count']
    failed_delta = target_failed - base_failed
    
    if failed_delta > 0:
        regressions.append({
            'type': 'failed_requests',
            'description': f"Failed requests increased by {failed_delta}",
            'severity': 'high'
        })
    elif failed_delta < 0:
        improvements.append({
            'type': 'failed_requests',
            'description': f"Failed requests decreased by {abs(failed_delta)}"
        })
    
    return {
        'regressions': regressions,
        'improvements': improvements,
        'overall_status': 'regression' if regressions else 'improvement' if improvements else 'stable'
    }

def _analyze_third_party_changes(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Analyze changes in third-party domain usage"""
    
    def get_domains(data):
        domains = {}
        for req in data['requests']:
            domain = req['domain']
            if domain not in domains:
                domains[domain] = {'count': 0, 'size': 0, 'time': 0}
            domains[domain]['count'] += 1
            domains[domain]['size'] += req['size']
            domains[domain]['time'] += req['time']
        return domains
    
    base_domains = get_domains(base_data)
    target_domains = get_domains(target_data)
    
    added_domains = set(target_domains.keys()) - set(base_domains.keys())
    removed_domains = set(base_domains.keys()) - set(target_domains.keys())
    
    return {
        'added_domains': list(added_domains),
        'removed_domains': list(removed_domains),
        'domain_changes': {
            domain: {
                'base': base_domains.get(domain, {'count': 0, 'size': 0, 'time': 0}),
                'target': target_domains.get(domain, {'count': 0, 'size': 0, 'time': 0})
            }
            for domain in set(base_domains.keys()) | set(target_domains.keys())
        }
    }

def _analyze_size_changes(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Analyze size changes in detail"""
    
    base_requests = {req['url']: req for req in base_data['requests']}
    target_requests = {req['url']: req for req in target_data['requests']}
    
    common_urls = set(base_requests.keys()) & set(target_requests.keys())
    
    size_changes = []
    for url in common_urls:
        base_size = base_requests[url]['size']
        target_size = target_requests[url]['size']
        size_delta = target_size - base_size
        
        if abs(size_delta) > 1024:  # >1KB change
            size_changes.append({
                'url': url,
                'resource_type': target_requests[url]['resource_type'],
                'base_size': base_size,
                'target_size': target_size,
                'size_delta': size_delta,
                'size_delta_kb': round(size_delta / 1024, 2)
            })
    
    size_changes.sort(key=lambda x: abs(x['size_delta']), reverse=True)
    
    return {
        'significant_changes': size_changes[:20],  # Top 20 size changes
        'total_size_delta': sum(change['size_delta'] for change in size_changes),
        'largest_increase': max(size_changes, key=lambda x: x['size_delta']) if size_changes else None,
        'largest_decrease': min(size_changes, key=lambda x: x['size_delta']) if size_changes else None
    }

def _compare_failed_requests(base_data: Dict, target_data: Dict) -> Dict[str, Any]:
    """Compare failed requests between base and target"""
    
    base_failed_urls = {req['url'] for req in base_data['failed_requests']}
    target_failed_urls = {req['url'] for req in target_data['failed_requests']}
    
    newly_failed = target_failed_urls - base_failed_urls
    fixed_requests = base_failed_urls - target_failed_urls
    still_failing = base_failed_urls & target_failed_urls
    
    return {
        'newly_failed': list(newly_failed),
        'fixed_requests': list(fixed_requests),
        'still_failing': list(still_failing),
        'counts': {
            'newly_failed': len(newly_failed),
            'fixed': len(fixed_requests),
            'still_failing': len(still_failing)
        }
    }

def _generate_comparison_summary(comparison: Dict) -> Dict[str, Any]:
    """Generate high-level summary of the comparison"""
    
    kpi_changes = comparison['kpi_changes']
    resource_deltas = comparison['resource_deltas']
    regression = comparison['performance_regression']
    
    # Determine overall status
    load_time_change = kpi_changes['page_load_time']['direction']
    request_count_change = kpi_changes['total_requests']['direction']
    size_change = kpi_changes['total_size_mb']['direction']
    
    status_score = 0
    if load_time_change == 'decreased':
        status_score += 2
    elif load_time_change == 'increased':
        status_score -= 2
    
    if request_count_change == 'decreased':
        status_score += 1
    elif request_count_change == 'increased':
        status_score -= 1
    
    if size_change == 'decreased':
        status_score += 1
    elif size_change == 'increased':
        status_score -= 1
    
    overall_status = 'improved' if status_score > 0 else 'regressed' if status_score < 0 else 'mixed'
    
    return {
        'overall_status': overall_status,
        'key_findings': [
            f"Load time {kpi_changes['page_load_time']['direction']} by {abs(kpi_changes['page_load_time']['absolute']):.2f}s",
            f"{resource_deltas['counts']['added']} resources added, {resource_deltas['counts']['removed']} removed",
            f"Total size {size_change} by {abs(kpi_changes['total_size_mb']['absolute']):.2f}MB",
            f"{len(regression['regressions'])} regressions, {len(regression['improvements'])} improvements detected"
        ],
        'risk_level': 'high' if len(regression['regressions']) > 3 else 'medium' if len(regression['regressions']) > 0 else 'low'
    }

def _is_grade_improved(base_grade: str, target_grade: str) -> bool:
    """Check if performance grade improved"""
    grade_order = ['CRITICAL', 'POOR', 'FAIR', 'GOOD', 'EXCELLENT']
    base_index = grade_order.index(base_grade) if base_grade in grade_order else 0
    target_index = grade_order.index(target_grade) if target_grade in grade_order else 0
    return target_index > base_index

def save_comparison_analysis(comparison: Dict[str, Any], output_file: str = None) -> str:
    """Save comparison analysis to JSON file"""
    
    if not output_file:
        output_file = "har_comparison_analysis.json"
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(comparison, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Comparison analysis saved to: {output_file}")
    return output_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compare two HAR chunk analyses")
    parser.add_argument('--base', required=True, help='Base HAR breakdown JSON file')
    parser.add_argument('--target', required=True, help='Target HAR breakdown JSON file')
    parser.add_argument('--output', help='Output comparison JSON file')
    
    args = parser.parse_args()
    
    try:
        # Load base data
        with open(args.base, 'r', encoding='utf-8') as f:
            base_data = json.load(f)
        
        # Load target data
        with open(args.target, 'r', encoding='utf-8') as f:
            target_data = json.load(f)
        
        # Perform comparison
        comparison = compare_har_chunks(base_data, target_data)
        
        # Save results
        output_file = save_comparison_analysis(comparison, args.output)
        
        # Print summary
        summary = comparison['summary']
        print(f"\n🎯 Comparison Summary:")
        print(f"   Status: {summary['overall_status'].upper()}")
        print(f"   Risk Level: {summary['risk_level'].upper()}")
        for finding in summary['key_findings']:
            print(f"   • {finding}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
