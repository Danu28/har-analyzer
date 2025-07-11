#!/usr/bin/env python3
"""
Single HAR Analysis Report Generator
===================================
This script generates comprehensive HTML reports from single HAR file analysis data.
Uses Jinja2 templating to create professional, interactive reports with charts and detailed insights.

Features:
- Template-based HTML report generation
- Multiple template styles (detailed, summary, dashboard)
- Interactive charts and visualizations
- Professional styling and responsive design
- Actionable performance insights
- Detailed resource analysis tables
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import webbrowser

def generate_single_har_report(analysis_data: Dict[str, Any], 
                             output_file: Optional[str] = None,
                             template_file: Optional[str] = None,
                             template_style: str = "detailed",
                             open_browser: bool = True) -> str:
    """
    Generate HTML report from single HAR analysis data
    
    Args:
        analysis_data: Analysis data dictionary from analyze_performance.py
        output_file: Output HTML file path (default: har_analysis_report.html)
        template_file: Custom template file path (default: uses built-in template)
        template_style: Template style - "detailed", "summary", or "dashboard" (default: detailed)
        open_browser: Whether to open report in browser
        
    Returns:
        Path to generated HTML report
    """
    print("Generating single HAR analysis report...")
    
    # Set default output file
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        har_name = analysis_data.get('metadata', {}).get('har_name', 'unknown')
        output_file = f"har_analysis_{har_name}_{timestamp}.html"
    
    # Ensure .html extension
    if not output_file.endswith('.html'):
        output_file += '.html'
    
    # Try to use external template first, then fall back to built-in
    if template_file and os.path.exists(template_file):
        print(f"Using custom template: {template_file}")
        template_content = _load_template_file(template_file)
    else:
        # Check for style-specific template in templates directory
        template_filename = f"har_single_{template_style}.html"
        default_template = Path(__file__).parent.parent / "templates" / template_filename
        
        if default_template.exists():
            print(f"Using {template_style} template: {default_template}")
            template_content = _load_template_file(str(default_template))
        else:
            print(f"Using built-in {template_style} template")
            template_content = _get_builtin_template(template_style)
    
    # Process and validate analysis data
    processed_data = _process_analysis_data(analysis_data)
    
    # Render template with data
    try:
        from jinja2 import Template, DebugUndefined
        template = Template(template_content, undefined=DebugUndefined)
        html_content = template.render(**processed_data)
    except ImportError:
        print("WARNING: Jinja2 not found, using simple template replacement")
        html_content = _render_simple_template(template_content, processed_data)
    except Exception as e:
        print(f"WARNING: Jinja2 template error: {e}")
        print("   Falling back to simple template replacement")
        html_content = _render_simple_template(template_content, processed_data)
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size = os.path.getsize(output_file) / 1024
    print(f"SUCCESS: Report generated: {output_file} ({file_size:.1f} KB)")
    
    # Open in browser if requested
    if open_browser:
        try:
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
            print("Report opened in browser")
        except Exception as e:
            print(f"WARNING: Could not open browser: {e}")
    
    return output_file

def _load_template_file(template_path: str) -> str:
    """Load template content from file"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"WARNING: Could not load template {template_path}: {e}")
        return _get_builtin_template("detailed")

def _process_analysis_data(analysis_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process and validate analysis data for template rendering"""
    
    # Ensure all required sections exist with defaults
    processed = {
        'metadata': analysis_data.get('metadata', {}),
        'performance_summary': analysis_data.get('performance_summary', {}),
        'critical_issues': analysis_data.get('critical_issues', {}),
        'resource_breakdown': analysis_data.get('resource_breakdown', {}),
        'largest_assets': analysis_data.get('largest_assets', []),
        'slowest_requests': analysis_data.get('slowest_requests', []),
        'failed_requests': analysis_data.get('failed_requests', []),
        'compression_analysis': analysis_data.get('compression_analysis', {}),
        'caching_analysis': analysis_data.get('caching_analysis', {}),
        'dns_connection_analysis': analysis_data.get('dns_connection_analysis', {}),
        'enhanced_third_party_analysis': analysis_data.get('enhanced_third_party_analysis', {}),
        'recommendations': analysis_data.get('recommendations', []),
        'timing_breakdown': analysis_data.get('timing_breakdown', {}),
        'domain_analysis': analysis_data.get('domain_analysis', {}),
        'status_codes': analysis_data.get('status_codes', {})
    }
    
    # Add current timestamp to metadata
    if 'report_timestamp' not in processed['metadata']:
        processed['metadata']['report_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Calculate performance grade if not present
    if 'performance_grade' not in processed['performance_summary']:
        processed['performance_summary']['performance_grade'] = _calculate_performance_grade(processed)
    
    # Generate performance insights
    processed['performance_insights'] = _generate_performance_insights(processed)
    
    # Generate chart data
    processed['chart_data'] = _generate_chart_data(processed)
    
    # Add template-specific variables for premium template
    processed['timestamp'] = processed['metadata']['report_timestamp']
    processed['performance_grade'] = processed['performance_summary'].get('performance_grade', 'UNKNOWN')
    processed['page_load_time'] = processed['performance_summary'].get('page_load_time', '0s')
    processed['dom_ready_time'] = processed['performance_summary'].get('dom_ready_time', '0s')
    processed['total_requests'] = processed['performance_summary'].get('total_requests', 0)
    processed['failed_requests_count'] = len(processed['failed_requests'])
    
    # Calculate performance classes
    page_load_time = processed['performance_summary'].get('page_load_time', '0s')
    dom_ready_time = processed['performance_summary'].get('dom_ready_time', '0s')
    
    # Extract numeric values from time strings
    try:
        page_load_sec = float(str(page_load_time).replace('s', '')) if 's' in str(page_load_time) else float(str(page_load_time))
    except (ValueError, TypeError):
        page_load_sec = 0
    
    try:
        dom_ready_sec = float(str(dom_ready_time).replace('s', '')) if 's' in str(dom_ready_time) else float(str(dom_ready_time))
    except (ValueError, TypeError):
        dom_ready_sec = 0
    
    processed['load_time_class'] = 'danger' if page_load_sec > 5 else 'warning' if page_load_sec > 3 else 'success'
    processed['dom_time_class'] = 'danger' if dom_ready_sec > 2 else 'warning' if dom_ready_sec > 1 else 'success'
    processed['requests_class'] = 'danger' if processed['total_requests'] > 100 else 'warning' if processed['total_requests'] > 50 else 'success'
    processed['failed_class'] = 'danger' if processed['failed_requests_count'] > 5 else 'warning' if processed['failed_requests_count'] > 0 else 'success'
    
    # Calculate max values for progress bars
    processed['max_asset_size'] = max([asset.get('size_kb', 0) for asset in processed['largest_assets']], default=1)
    processed['max_request_time'] = max([req.get('time_ms', 0) for req in processed['slowest_requests']], default=1)
    
    # Calculate summary metrics
    largest_assets = processed['largest_assets']
    total_asset_size = sum([asset.get('size_kb', 0) for asset in largest_assets])
    processed['total_size_mb'] = round(total_asset_size / 1024, 1) if total_asset_size > 0 else 0
    
    slowest_requests = processed['slowest_requests'] 
    avg_response_time = sum([req.get('time_ms', 0) for req in slowest_requests]) / len(slowest_requests) if slowest_requests else 0
    processed['avg_response_time'] = round(avg_response_time)
    
    # Third-party analysis
    third_party_analysis = processed['enhanced_third_party_analysis']
    processed['third_party_domains'] = third_party_analysis.get('total_third_party_domains', 0)
    processed['blocking_resources'] = len(third_party_analysis.get('blocking_third_parties', []))
    
    # Extract issues and recommendations from insights
    insights = processed['performance_insights']
    processed['issues'] = insights.get('issues', [])
    processed['recommendations'] = insights.get('recommendations', [])
    processed['strengths'] = insights.get('strengths', [])
    processed['priority_actions'] = insights.get('priority_actions', [])
    
    # Resource chart data
    processed['resource_chart_data'] = processed['chart_data'].get('resource_breakdown', [])
    
    # Caching analysis data
    caching_analysis = processed['caching_analysis']
    processed['no_cache_count'] = len(caching_analysis.get('no_cache_resources', []))
    processed['short_cache_count'] = len(caching_analysis.get('short_cache_resources', []))
    processed['well_cached_count'] = caching_analysis.get('well_cached_count', 0)
    processed['potential_savings'] = round(caching_analysis.get('total_potential_savings_kb', 0))
    processed['no_cache_resources'] = [
        {
            'url': res.get('url', ''),
            'type': res.get('resourceType', 'unknown'),
            'size_kb': round(res.get('size', 0) / 1024, 1)
        } for res in caching_analysis.get('no_cache_resources', [])
    ]
    
    # DNS analysis data
    dns_analysis = processed['dns_connection_analysis']
    processed['dns_analysis'] = dns_analysis
    
    # Handle avg_dns_time which might be "N/A" string
    avg_dns_raw = dns_analysis.get('avg_dns_time', 0)
    if isinstance(avg_dns_raw, str):
        processed['avg_dns_time'] = 0  # Convert "N/A" to 0
    else:
        processed['avg_dns_time'] = float(avg_dns_raw) if avg_dns_raw else 0
    
    # Handle avg_ssl_time 
    avg_ssl_raw = dns_analysis.get('avg_ssl_time', 0)
    processed['avg_ssl_time'] = float(avg_ssl_raw) if avg_ssl_raw else 0
    
    dns_class = 'danger' if processed['avg_dns_time'] > 100 else 'warning' if processed['avg_dns_time'] > 50 else 'success'
    ssl_class = 'danger' if processed['avg_ssl_time'] > 300 else 'warning' if processed['avg_ssl_time'] > 200 else 'success'
    processed['dns_class'] = dns_class
    processed['ssl_class'] = ssl_class
    
    # Domain performance data
    domain_performance = dns_analysis.get('domain_performance', [])
    processed['domain_performance'] = [
        {
            'name': domain.get('domain', 'unknown'),
            'requests': domain.get('requests', 0),
            'dns_time': f"{domain.get('avg_dns_ms', 0):.1f}",
            'ssl_time': f"{domain.get('avg_ssl_ms', 0):.1f}",
            'total_time': f"{domain.get('total_time_ms', 0):.1f}",
            'category': 'third-party'
        } for domain in domain_performance[:10]
    ]
    
    processed['unique_domains'] = len(domain_performance)
    processed['connection_reuse'] = 85  # Placeholder calculation
    
    # Enhanced third-party analysis
    processed['third_party_analysis'] = third_party_analysis
    processed['category_breakdown'] = third_party_analysis.get('category_breakdown', {})
    
    # High impact domains
    domain_impact = third_party_analysis.get('domain_impact', {})
    high_impact_domains = []
    for domain_name, stats in list(domain_impact.items())[:5]:
        high_impact_domains.append({
            'name': domain_name,
            'requests': stats.get('requests', 0),
            'total_time': stats.get('total_time', 0),
            'size_kb': stats.get('total_size_kb', 0),
            'category': stats.get('category', 'unknown')
        })
    processed['high_impact_domains'] = high_impact_domains
    
    return processed

def _calculate_performance_grade(data: Dict[str, Any]) -> str:
    """Calculate overall performance grade based on metrics"""
    performance_summary = data.get('performance_summary', {})
    
    # Extract timing values
    page_load_time = performance_summary.get('page_load_time', '0s')
    dom_ready_time = performance_summary.get('dom_ready_time', '0s')
    
    # Convert to seconds
    load_time_sec = float(page_load_time.replace('s', '')) if 's' in str(page_load_time) else 0
    dom_time_sec = float(dom_ready_time.replace('s', '')) if 's' in str(dom_ready_time) else 0
    
    # Get other metrics
    total_requests = performance_summary.get('total_requests', 0)
    failed_requests = len(data.get('failed_requests', []))
    
    # Calculate grade based on thresholds
    score = 100
    
    # Page load time penalty
    if load_time_sec > 10:
        score -= 40
    elif load_time_sec > 5:
        score -= 25
    elif load_time_sec > 3:
        score -= 15
    
    # DOM ready time penalty
    if dom_time_sec > 5:
        score -= 25
    elif dom_time_sec > 2:
        score -= 15
    elif dom_time_sec > 1:
        score -= 10
    
    # Request count penalty
    if total_requests > 100:
        score -= 20
    elif total_requests > 50:
        score -= 10
    
    # Failed requests penalty
    if failed_requests > 10:
        score -= 20
    elif failed_requests > 5:
        score -= 15
    elif failed_requests > 0:
        score -= 10
    
    # Determine grade
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 70:
        return "B"
    elif score >= 60:
        return "C"
    elif score >= 50:
        return "D"
    else:
        return "F"

def _generate_performance_insights(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate performance insights and recommendations"""
    performance_summary = data.get('performance_summary', {})
    critical_issues = data.get('critical_issues', {})
    
    insights = {
        'issues': [],
        'recommendations': [],
        'strengths': [],
        'priority_actions': []
    }
    
    # Extract timing values
    page_load_time = performance_summary.get('page_load_time', '0s')
    dom_ready_time = performance_summary.get('dom_ready_time', '0s')
    load_time_sec = float(page_load_time.replace('s', '')) if 's' in str(page_load_time) else 0
    dom_time_sec = float(dom_ready_time.replace('s', '')) if 's' in str(dom_ready_time) else 0
    
    total_requests = performance_summary.get('total_requests', 0)
    total_size = performance_summary.get('total_size_mb', 0)
    failed_requests = len(data.get('failed_requests', []))
    
    # Analyze load times
    if load_time_sec > 10:
        insights['issues'].append("Critical: Page load time exceeds 10 seconds")
        insights['priority_actions'].append("Implement aggressive code splitting and lazy loading")
    elif load_time_sec > 5:
        insights['issues'].append("Poor: Page load time exceeds 5 seconds")
        insights['recommendations'].append("Optimize bundle sizes and critical rendering path")
    elif load_time_sec < 3:
        insights['strengths'].append("Good: Page load time is under 3 seconds")
    
    # Analyze DOM ready time
    if dom_time_sec > 5:
        insights['issues'].append("Critical: DOM ready time exceeds 5 seconds")
        insights['priority_actions'].append("Minimize blocking JavaScript and CSS")
    elif dom_time_sec > 2:
        insights['issues'].append("Warning: DOM ready time exceeds 2 seconds")
        insights['recommendations'].append("Defer non-critical scripts and optimize CSS delivery")
    
    # Analyze request count
    if total_requests > 100:
        insights['issues'].append(f"Excessive requests: {total_requests} total requests")
        insights['priority_actions'].append("Bundle assets and implement resource consolidation")
    elif total_requests > 50:
        insights['issues'].append(f"High request count: {total_requests} requests")
        insights['recommendations'].append("Consider bundling smaller assets together")
    elif total_requests < 30:
        insights['strengths'].append("Good: Reasonable number of HTTP requests")
    
    # Analyze total size
    if total_size > 10:
        insights['issues'].append(f"Large page size: {total_size:.1f}MB total")
        insights['priority_actions'].append("Implement image optimization and code splitting")
    elif total_size > 5:
        insights['issues'].append(f"Heavy page: {total_size:.1f}MB total")
        insights['recommendations'].append("Optimize images and remove unused dependencies")
    
    # Analyze failed requests
    if failed_requests > 10:
        insights['issues'].append(f"Many failed requests: {failed_requests} failures")
        insights['priority_actions'].append("Fix or remove broken dependencies")
    elif failed_requests > 0:
        insights['issues'].append(f"Some failed requests: {failed_requests} failures")
        insights['recommendations'].append("Review and fix failing requests")
    else:
        insights['strengths'].append("Excellent: No failed requests")
    
    # Analyze compression opportunities
    compression_data = data.get('compression_analysis', {})
    compression_opportunities = compression_data.get('compression_opportunity_count', 0)
    if compression_opportunities > 5:
        insights['recommendations'].append(f"Enable compression for {compression_opportunities} resources")
    
    # Analyze caching opportunities
    caching_data = data.get('caching_analysis', {})
    no_cache_count = len(caching_data.get('no_cache_resources', []))
    if no_cache_count > 5:
        insights['recommendations'].append(f"Add cache headers to {no_cache_count} resources")
    
    return insights

def _generate_chart_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Generate data for charts and visualizations"""
    
    # Resource breakdown pie chart
    resource_breakdown = data.get('resource_breakdown', {})
    resource_chart = []
    colors = {
        'script': '#FF6B6B',
        'image': '#4ECDC4', 
        'document': '#45B7D1',
        'xhr': '#96CEB4',
        'fetch': '#FFEAA7',
        'font': '#DDA0DD',
        'ping': '#FFA07A',
        'other': '#D3D3D3'
    }
    
    for resource_type, count in resource_breakdown.items():
        resource_chart.append({
            'label': resource_type.title(),
            'value': count,
            'color': colors.get(resource_type, '#D3D3D3')
        })
    
    # Timing breakdown chart
    timing_breakdown = data.get('timing_breakdown', {})
    timing_chart = []
    timing_colors = {
        'dns': '#FF6B6B',
        'connect': '#4ECDC4',
        'ssl': '#45B7D1',
        'send': '#96CEB4',
        'wait': '#FFEAA7',
        'receive': '#DDA0DD'
    }
    
    for timing_type, value in timing_breakdown.items():
        if value > 0:
            timing_chart.append({
                'label': timing_type.replace('_', ' ').title(),
                'value': value,
                'color': timing_colors.get(timing_type, '#D3D3D3')
            })
    
    # Status codes chart
    status_codes = data.get('status_codes', {})
    status_chart = []
    status_colors = {
        '2xx': '#16a34a',
        '3xx': '#eab308',
        '4xx': '#ea580c',
        '5xx': '#dc2626'
    }
    
    for status_range, count in status_codes.items():
        if count > 0:
            status_chart.append({
                'label': f"{status_range} ({count})",
                'value': count,
                'color': status_colors.get(status_range, '#D3D3D3')
            })
    
    return {
        'resource_breakdown': sorted(resource_chart, key=lambda x: x['value'], reverse=True),
        'timing_breakdown': timing_chart,
        'status_codes': status_chart
    }

def _get_builtin_template(template_style: str = "detailed") -> str:
    """Get built-in HTML template based on style"""
    
    if template_style == "summary":
        return _get_summary_template()
    elif template_style == "dashboard":
        return _get_dashboard_template()
    else:
        return _get_detailed_template()

def _get_detailed_template() -> str:
    """Get detailed built-in template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAR Performance Analysis Report</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #16a34a;
            --warning-color: #ea580c;
            --danger-color: #dc2626;
            --info-color: #0891b2;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-200: #e5e7eb;
            --gray-300: #d1d5db;
            --gray-700: #374151;
            --gray-800: #1f2937;
            --gray-900: #111827;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--gray-800);
            background-color: var(--gray-50);
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .header {
            background: linear-gradient(135deg, var(--primary-color), var(--info-color));
            color: white;
            padding: 30px 0;
            margin-bottom: 30px;
            border-radius: 12px;
            text-align: center;
        }

        .header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            font-weight: 700;
        }

        .header p {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }

        .summary-card {
            background: white;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
        }

        .summary-card.grade-a {
            border-left-color: var(--success-color);
        }

        .summary-card.grade-b {
            border-left-color: var(--info-color);
        }

        .summary-card.grade-c {
            border-left-color: var(--warning-color);
        }

        .summary-card.grade-d, .summary-card.grade-f {
            border-left-color: var(--danger-color);
        }

        .summary-card h3 {
            font-size: 1.3rem;
            margin-bottom: 15px;
            color: var(--gray-800);
        }

        .performance-grade {
            font-size: 3rem;
            font-weight: 900;
            text-align: center;
            margin: 10px 0;
        }

        .grade-a { color: var(--success-color); }
        .grade-b { color: var(--info-color); }
        .grade-c { color: var(--warning-color); }
        .grade-d, .grade-f { color: var(--danger-color); }

        .metric-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px;
        }

        .metric-item {
            text-align: center;
            padding: 15px;
            background: var(--gray-50);
            border-radius: 8px;
        }

        .metric-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }

        .metric-value.success { color: var(--success-color); }
        .metric-value.warning { color: var(--warning-color); }
        .metric-value.danger { color: var(--danger-color); }
        .metric-value.info { color: var(--info-color); }

        .metric-label {
            font-size: 0.9rem;
            color: var(--gray-700);
        }

        .section {
            background: white;
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 30px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }

        .section h2 {
            font-size: 1.8rem;
            margin-bottom: 20px;
            color: var(--gray-800);
            border-bottom: 2px solid var(--gray-200);
            padding-bottom: 10px;
        }

        .insights-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }

        .insight-card {
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid;
        }

        .insight-card.issues {
            background: #fef2f2;
            border-left-color: var(--danger-color);
        }

        .insight-card.recommendations {
            background: #fefbeb;
            border-left-color: var(--warning-color);
        }

        .insight-card.strengths {
            background: #f0fdf4;
            border-left-color: var(--success-color);
        }

        .insight-card h4 {
            margin-bottom: 10px;
            color: var(--gray-800);
        }

        .insight-list {
            list-style: none;
            padding: 0;
        }

        .insight-list li {
            margin: 8px 0;
            padding-left: 20px;
            position: relative;
        }

        .insight-list li::before {
            content: "•";
            position: absolute;
            left: 0;
            color: var(--primary-color);
            font-weight: bold;
        }

        .table-container {
            overflow-x: auto;
            margin-top: 15px;
        }

        table {
            width: 100%;
            border-collapse: collapse;
            font-size: 0.9rem;
        }

        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid var(--gray-200);
        }

        th {
            background: var(--gray-100);
            font-weight: 600;
            color: var(--gray-700);
        }

        tr:hover {
            background: var(--gray-50);
        }

        .url-cell {
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
        }

        .url-cell:hover {
            color: var(--primary-color);
        }

        .status-badge {
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 0.8rem;
            font-weight: 600;
        }

        .status-2xx { background: #dcfce7; color: var(--success-color); }
        .status-3xx { background: #fef3c7; color: var(--warning-color); }
        .status-4xx { background: #fee2e2; color: var(--danger-color); }
        .status-5xx { background: #fecaca; color: #991b1b; }

        .chart-container {
            height: 300px;
            background: var(--gray-50);
            border-radius: 8px;
            display: flex;
            align-items: center;
            justify-content: center;
            color: var(--gray-700);
            margin: 20px 0;
        }

        .footer {
            text-align: center;
            padding: 30px 0;
            color: var(--gray-700);
            border-top: 1px solid var(--gray-200);
            margin-top: 40px;
        }

        @media (max-width: 768px) {
            .container {
                padding: 15px;
            }

            .header h1 {
                font-size: 2rem;
            }

            .summary-grid {
                grid-template-columns: 1fr;
            }

            .metric-grid {
                grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
            }

            .insights-grid {
                grid-template-columns: 1fr;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>📊 HAR Performance Analysis</h1>
            <p>{{ metadata.har_name or 'Performance Report' }}</p>
        </div>

        <!-- Summary Cards -->
        <div class="summary-grid">
            <div class="summary-card grade-{{ performance_summary.performance_grade.lower().replace('+', 'plus') }}">
                <h3>Overall Performance Grade</h3>
                <div class="performance-grade grade-{{ performance_summary.performance_grade.lower().replace('+', 'plus') }}">
                    {{ performance_summary.performance_grade }}
                </div>
                <p style="text-align: center; color: var(--gray-700);">
                    Based on loading times, request efficiency, and error rates
                </p>
            </div>

            <div class="summary-card">
                <h3>📈 Key Metrics</h3>
                <div class="metric-grid">
                    <div class="metric-item">
                        <div class="metric-value {{ 'success' if performance_summary.page_load_time|replace('s', '')|float < 3 else 'warning' if performance_summary.page_load_time|replace('s', '')|float < 5 else 'danger' }}">
                            {{ performance_summary.page_load_time or 'N/A' }}
                        </div>
                        <div class="metric-label">Page Load</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value {{ 'success' if performance_summary.dom_ready_time|replace('s', '')|float < 2 else 'warning' if performance_summary.dom_ready_time|replace('s', '')|float < 5 else 'danger' }}">
                            {{ performance_summary.dom_ready_time or 'N/A' }}
                        </div>
                        <div class="metric-label">DOM Ready</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value {{ 'success' if performance_summary.total_requests < 30 else 'warning' if performance_summary.total_requests < 50 else 'danger' }}">
                            {{ performance_summary.total_requests or 0 }}
                        </div>
                        <div class="metric-label">Requests</div>
                    </div>
                    <div class="metric-item">
                        <div class="metric-value {{ failed_class }}">
                            {{ failed_requests_count }}
                        </div>
                        <div class="metric-label">Failed</div>
                    </div>
                </div>
            </div>
        </div>

        <!-- Performance Insights -->
        <div class="section">
            <h2>🔍 Performance Insights</h2>
            <div class="insights-grid">
                {% if performance_insights.issues %}
                <div class="insight-card issues">
                    <h4>⚠️ Issues Found</h4>
                    <ul class="insight-list">
                        {% for issue in performance_insights.issues %}
                        <li>{{ issue }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}

                {% if performance_insights.recommendations %}
                <div class="insight-card recommendations">
                    <h4>💡 Recommendations</h4>
                    <ul class="insight-list">
                        {% for rec in performance_insights.recommendations %}
                        <li>{{ rec }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}

                {% if performance_insights.strengths %}
                <div class="insight-card strengths">
                    <h4>✅ Strengths</h4>
                    <ul class="insight-list">
                        {% for strength in performance_insights.strengths %}
                        <li>{{ strength }}</li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>

            {% if performance_insights.priority_actions %}
            <div style="background: #fef2f2; padding: 20px; border-radius: 8px; border-left: 4px solid var(--danger-color);">
                <h4 style="color: var(--danger-color); margin-bottom: 10px;">🚨 Priority Actions</h4>
                <ul class="insight-list">
                    {% for action in performance_insights.priority_actions %}
                    <li style="color: var(--danger-color);">{{ action }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>

        <!-- Resource Breakdown -->
        <div class="section">
            <h2>📦 Resource Breakdown</h2>
            <div class="chart-container">
                <div>
                    <h3>Resource Types</h3>
                    {% for item in chart_data.resource_breakdown %}
                    <div style="margin: 5px 0;">
                        <span style="display: inline-block; width: 20px; height: 20px; background: {{ item.color }}; margin-right: 10px;"></span>
                        {{ item.label }}: {{ item.value }}
                    </div>
                    {% endfor %}
                </div>
            </div>
        </div>

        <!-- Largest Assets -->
        {% if largest_assets %}
        <div class="section">
            <h2>📏 Largest Assets</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Asset</th>
                            <th>Size</th>
                            <th>Type</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for asset in largest_assets[:10] %}
                        <tr>
                            <td class="url-cell" title="{{ asset.url }}">{{ asset.url }}</td>
                            <td>{{ "%.1f"|format(asset.size_kb) }} KB</td>
                            <td>{{ asset.resource_type or 'unknown' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- Slowest Requests -->
        {% if slowest_requests %}
        <div class="section">
            <h2>🐌 Slowest Requests</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Request</th>
                            <th>Time</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for req in slowest_requests[:10] %}
                        <tr>
                            <td class="url-cell" title="{{ req.url }}">{{ req.url }}</td>
                            <td>{{ "%.0f"|format(req.time_ms) }} ms</td>
                            <td><span class="status-badge status-{{ (req.status_code // 100)|string }}xx">{{ req.status_code or 'N/A' }}</span></td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- Failed Requests -->
        {% if failed_requests %}
        <div class="section">
            <h2>❌ Failed Requests</h2>
            <div class="table-container">
                <table>
                    <thead>
                        <tr>
                            <th>Request</th>
                            <th>Status</th>
                            <th>Error</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for req in failed_requests %}
                        <tr>
                            <td class="url-cell" title="{{ req.url }}">{{ req.url }}</td>
                            <td><span class="status-badge status-{{ (req.status_code // 100)|string }}xx">{{ req.status_code or 'N/A' }}</span></td>
                            <td>{{ req.error_type or 'Network Error' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
        {% endif %}

        <!-- Footer -->
        <div class="footer">
            <p>Generated by HAR-ANALYZE Performance Analysis Tool</p>
            <p style="font-size: 0.9rem; margin-top: 5px; color: var(--gray-700);">
                Report generated on {{ metadata.report_timestamp }}
            </p>
        </div>
    </div>
</body>
</html>"""

def _get_summary_template() -> str:
    """Get summary built-in template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAR Performance Summary</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #16a34a;
            --warning-color: #ea580c;
            --danger-color: #dc2626;
            --gray-50: #f9fafb;
            --gray-700: #374151;
            --gray-800: #1f2937;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--gray-800);
            background-color: var(--gray-50);
            padding: 20px;
        }

        .container { max-width: 800px; margin: 0 auto; }

        .header {
            background: linear-gradient(135deg, var(--primary-color), #0891b2);
            color: white;
            padding: 20px;
            border-radius: 12px;
            text-align: center;
            margin-bottom: 20px;
        }

        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-bottom: 20px;
        }

        .summary-card {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
        }

        .grade { font-size: 2.5rem; font-weight: 900; margin: 10px 0; }
        .grade-a { color: var(--success-color); }
        .grade-b { color: #0891b2; }
        .grade-c { color: var(--warning-color); }
        .grade-d, .grade-f { color: var(--danger-color); }

        .metric-value { font-size: 1.5rem; font-weight: 700; }
        .metric-label { font-size: 0.9rem; color: var(--gray-700); }

        .insights {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }

        .insight-section { margin-bottom: 15px; }
        .insight-section h4 { margin-bottom: 8px; }
        .insight-list { list-style: none; padding-left: 0; }
        .insight-list li { margin: 5px 0; padding-left: 15px; position: relative; }
        .insight-list li::before { content: "•"; position: absolute; left: 0; color: var(--primary-color); }

        .footer {
            text-align: center;
            margin-top: 20px;
            color: var(--gray-700);
            font-size: 0.9rem;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Performance Summary</h1>
            <p>{{ metadata.har_name or 'HAR Analysis' }}</p>
        </div>

        <div class="summary-grid">
            <div class="summary-card">
                <div class="grade grade-{{ performance_summary.performance_grade.lower().replace('+', 'plus') }}">
                    {{ performance_summary.performance_grade }}
                </div>
                <div class="metric-label">Overall Grade</div>
            </div>

            <div class="summary-card">
                <div class="metric-value">{{ performance_summary.page_load_time or 'N/A' }}</div>
                <div class="metric-label">Page Load Time</div>
            </div>

            <div class="summary-card">
                <div class="metric-value">{{ performance_summary.total_requests or 0 }}</div>
                <div class="metric-label">Total Requests</div>
            </div>

            <div class="summary-card">
                <div class="metric-value">{{ failed_requests|length }}</div>
                <div class="metric-label">Failed Requests</div>
            </div>
        </div>

        <div class="insights">
            <h3>🔍 Key Insights</h3>
            
            {% if performance_insights.priority_actions %}
            <div class="insight-section">
                <h4 style="color: var(--danger-color);">🚨 Priority Actions</h4>
                <ul class="insight-list">
                    {% for action in performance_insights.priority_actions %}
                    <li>{{ action }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}

            {% if performance_insights.issues %}
            <div class="insight-section">
                <h4 style="color: var(--warning-color);">⚠️ Issues</h4>
                <ul class="insight-list">
                    {% for issue in performance_insights.issues[:3] %}
                    <li>{{ issue }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}

            {% if performance_insights.strengths %}
            <div class="insight-section">
                <h4 style="color: var(--success-color);">✅ Strengths</h4>
                <ul class="insight-list">
                    {% for strength in performance_insights.strengths[:3] %}
                    <li>{{ strength }}</li>
                    {% endfor %}
                </ul>
            </div>
            {% endif %}
        </div>

        <div class="footer">
            <p>Generated by HAR-ANALYZE • {{ metadata.report_timestamp }}</p>
        </div>
    </div>
</body>
</html>"""

def _get_dashboard_template() -> str:
    """Get dashboard built-in template"""
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAR Performance Dashboard</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --success-color: #16a34a;
            --warning-color: #ea580c;
            --danger-color: #dc2626;
            --info-color: #0891b2;
            --gray-50: #f9fafb;
            --gray-100: #f3f4f6;
            --gray-700: #374151;
            --gray-800: #1f2937;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: var(--gray-800);
            background-color: var(--gray-50);
        }

        .dashboard {
            display: grid;
            grid-template-columns: 1fr 1fr;
            grid-template-rows: auto auto auto;
            gap: 20px;
            padding: 20px;
            min-height: 100vh;
        }

        .header {
            grid-column: 1 / -1;
            background: linear-gradient(135deg, var(--primary-color), var(--info-color));
            color: white;
            padding: 30px;
            border-radius: 12px;
            text-align: center;
        }

        .widget {
            background: white;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
            border-left: 4px solid var(--primary-color);
        }

        .widget.danger { border-left-color: var(--danger-color); }
        .widget.warning { border-left-color: var(--warning-color); }
        .widget.success { border-left-color: var(--success-color); }

        .widget h3 {
            margin-bottom: 15px;
            color: var(--gray-800);
            font-size: 1.2rem;
        }

        .metric-display {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 900;
        }

        .metric-label {
            font-size: 0.9rem;
            color: var(--gray-700);
        }

        .grade { font-size: 3rem; font-weight: 900; text-align: center; }
        .grade-a { color: var(--success-color); }
        .grade-b { color: var(--info-color); }
        .grade-c { color: var(--warning-color); }
        .grade-d, .grade-f { color: var(--danger-color); }

        .mini-chart {
            height: 100px;
            background: var(--gray-100);
            border-radius: 6px;
            display: flex;
            align-items: center;
            justify-content: center;
            margin-top: 10px;
        }

        .status-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 10px;
        }

        .status-item {
            text-align: center;
            padding: 10px;
            background: var(--gray-100);
            border-radius: 6px;
        }

        .alert-list {
            list-style: none;
            max-height: 200px;
            overflow-y: auto;
        }

        .alert-list li {
            padding: 8px;
            margin: 5px 0;
            background: #fef2f2;
            border-left: 3px solid var(--danger-color);
            border-radius: 4px;
            font-size: 0.9rem;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
                padding: 10px;
            }
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <!-- Header -->
        <div class="header">
            <h1>📊 Performance Dashboard</h1>
            <p>{{ metadata.har_name or 'HAR Analysis' }} • {{ metadata.report_timestamp }}</p>
        </div>

        <!-- Performance Grade Widget -->
        <div class="widget success">
            <h3>Overall Performance</h3>
            <div class="grade grade-{{ performance_summary.performance_grade.lower().replace('+', 'plus') }}">
                {{ performance_summary.performance_grade }}
            </div>
            <div style="text-align: center; color: var(--gray-700);">
                Performance Grade
            </div>
        </div>

        <!-- Key Metrics Widget -->
        <div class="widget">
            <h3>📈 Key Metrics</h3>
            <div class="metric-display">
                <div>
                    <div class="metric-value">{{ performance_summary.page_load_time or 'N/A' }}</div>
                    <div class="metric-label">Page Load Time</div>
                </div>
            </div>
            <div class="metric-display">
                <div>
                    <div class="metric-value">{{ performance_summary.total_requests or 0 }}</div>
                    <div class="metric-label">Total Requests</div>
                </div>
            </div>
            <div class="metric-display">
                <div>
                    <div class="metric-value">{{ failed_requests|length }}</div>
                    <div class="metric-label">Failed Requests</div>
                </div>
            </div>
        </div>

        <!-- Resource Breakdown Widget -->
        <div class="widget">
            <h3>📦 Resource Types</h3>
            {% for item in chart_data.resource_breakdown[:5] %}
            <div style="display: flex; justify-content: space-between; margin: 8px 0;">
                <span>{{ item.label }}</span>
                <span style="font-weight: 600;">{{ item.value }}</span>
            </div>
            {% endfor %}
        </div>

        <!-- Alerts Widget -->
        <div class="widget {{ 'danger' if performance_insights.priority_actions else 'warning' if performance_insights.issues else 'success' }}">
            <h3>🚨 Alerts & Issues</h3>
            {% if performance_insights.priority_actions %}
            <ul class="alert-list">
                {% for action in performance_insights.priority_actions %}
                <li>{{ action }}</li>
                {% endfor %}
            </ul>
            {% elif performance_insights.issues %}
            <ul class="alert-list">
                {% for issue in performance_insights.issues[:3] %}
                <li>{{ issue }}</li>
                {% endfor %}
            </ul>
            {% else %}
            <p style="color: var(--success-color); text-align: center; padding: 20px;">
                ✅ No critical issues detected
            </p>
            {% endif %}
        </div>
    </div>
</body>
</html>"""

def _render_simple_template(template_content: str, data: Dict[str, Any]) -> str:
    """Simple template replacement fallback when Jinja2 is not available"""
    html = template_content
    
    # Replace basic variables
    replacements = {
        '{{ metadata.har_name }}': data.get('metadata', {}).get('har_name', 'HAR Analysis'),
        '{{ metadata.report_timestamp }}': data.get('metadata', {}).get('report_timestamp', ''),
        '{{ performance_summary.performance_grade }}': data.get('performance_summary', {}).get('performance_grade', 'N/A'),
        '{{ performance_summary.page_load_time }}': data.get('performance_summary', {}).get('page_load_time', 'N/A'),
        '{{ performance_summary.total_requests }}': str(data.get('performance_summary', {}).get('total_requests', 0)),
        '{{ failed_requests|length }}': str(len(data.get('failed_requests', [])))
    }
    
    for placeholder, value in replacements.items():
        html = html.replace(placeholder, value)
    
    return html

def main():
    """Main function for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate single HAR analysis HTML report")
    parser.add_argument('--analysis-file', required=True, help='Path to analysis JSON file (e.g., agent_summary.json)')
    parser.add_argument('--output', help='Output HTML file path')
    parser.add_argument('--template-file', help='Custom template file path')
    parser.add_argument('--template-style', choices=['detailed', 'summary', 'dashboard', 'premium'], 
                        default='detailed', help='Report template style (detailed, summary, dashboard, premium)')
    parser.add_argument('--no-browser', action='store_true', help='Don\'t open report in browser')
    
    args = parser.parse_args()
    
    # Load analysis data
    try:
        with open(args.analysis_file, 'r', encoding='utf-8') as f:
            analysis_data = json.load(f)
    except Exception as e:
        print(f"ERROR: Error loading analysis file: {e}")
        return 1
    
    # Generate report
    try:
        output_file = generate_single_har_report(
            analysis_data=analysis_data,
            output_file=args.output,
            template_file=args.template_file,
            template_style=args.template_style,
            open_browser=not args.no_browser
        )
        print(f"SUCCESS: Report generated successfully: {output_file}")
        return 0
    except Exception as e:
        print(f"ERROR: Error generating report: {e}")
        return 1

if __name__ == "__main__":
    exit(main())
