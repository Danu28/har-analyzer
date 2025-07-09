#!/usr/bin/env python3
"""
HAR Breaking Logic - Reusable Component for HAR Analysis
========================================================
This module provides reusable functions to break down HAR files into structured data
suitable for comparison analysis and performance evaluation.

Features:
- Extract requests with timings, sizes, and resource types
- Organize data by resource type (JS, CSS, images, etc.)
- Calculate key performance metrics
- Prepare data for comparison analysis
"""

import json
import os
from pathlib import Path
from urllib.parse import urlparse
from typing import Dict, List, Any, Optional

def extract_har_data(har_file_path: str) -> Dict[str, Any]:
    """
    Extract and structure HAR data for analysis
    
    Args:
        har_file_path: Path to the HAR file
        
    Returns:
        Dictionary containing structured HAR data with metrics
    """
    print(f"🔍 Breaking down HAR: {Path(har_file_path).name}")
    
    try:
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
    except Exception as e:
        raise ValueError(f"Failed to read HAR file: {e}")
    
    log = har_data.get('log', {})
    entries = log.get('entries', [])
    pages = log.get('pages', [])
    
    # Basic metadata
    metadata = {
        'version': log.get('version', '1.2'),
        'creator': log.get('creator', {}),
        'pages': pages,
        'total_entries': len(entries),
        'file_path': har_file_path,
        'file_name': Path(har_file_path).name
    }
    
    # Extract page timing info
    page_timings = {}
    if pages:
        page = pages[0]
        page_timings = {
            'onContentLoad': page.get('pageTimings', {}).get('onContentLoad', 0),
            'onLoad': page.get('pageTimings', {}).get('onLoad', 0),
            'title': page.get('title', ''),
            'started_date_time': page.get('startedDateTime', '')
        }
    
    # Process all requests
    requests = []
    resource_types = {}
    total_size = 0
    failed_requests = []
    slow_requests = []
    
    for i, entry in enumerate(entries):
        request = entry.get('request', {})
        response = entry.get('response', {})
        timings = entry.get('timings', {})
        
        # Extract core request data
        url = request.get('url', '')
        method = request.get('method', 'GET')
        status = response.get('status', 0)
        size = response.get('content', {}).get('size', 0)
        mime_type = response.get('content', {}).get('mimeType', '')
        time = entry.get('time', 0)
        started_date_time = entry.get('startedDateTime', '')
        
        # Determine resource type
        resource_type = _determine_resource_type(url, mime_type, entry.get('_resourceType'))
        
        # Extract detailed timings
        request_timings = {
            'blocked': timings.get('blocked', -1),
            'dns': timings.get('dns', -1),
            'connect': timings.get('connect', -1),
            'send': timings.get('send', -1),
            'wait': timings.get('wait', -1),
            'receive': timings.get('receive', -1),
            'ssl': timings.get('ssl', -1),
            'total': time
        }
        
        # Build request object
        request_obj = {
            'index': i,
            'url': url,
            'domain': urlparse(url).netloc,
            'method': method,
            'status': status,
            'status_text': response.get('statusText', ''),
            'size': size,
            'mime_type': mime_type,
            'resource_type': resource_type,
            'time': time,
            'started_date_time': started_date_time,
            'timings': request_timings,
            'headers': {
                'request': request.get('headers', []),
                'response': response.get('headers', [])
            }
        }
        
        requests.append(request_obj)
        
        # Categorize by resource type
        if resource_type not in resource_types:
            resource_types[resource_type] = []
        resource_types[resource_type].append(request_obj)
        
        # Track totals and issues
        total_size += size
        if status >= 400:
            failed_requests.append(request_obj)
        if time > 1000:  # Slow requests > 1 second
            slow_requests.append(request_obj)
    
    # Calculate performance metrics
    metrics = _calculate_performance_metrics(requests, page_timings, total_size)
    
    # Build final structured data
    structured_data = {
        'metadata': metadata,
        'page_timings': page_timings,
        'metrics': metrics,
        'requests': requests,
        'resource_types': resource_types,
        'failed_requests': failed_requests,
        'slow_requests': slow_requests,
        'totals': {
            'total_requests': len(requests),
            'total_size': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'failed_count': len(failed_requests),
            'slow_count': len(slow_requests)
        }
    }
    
    print(f"✅ Processed {len(requests)} requests across {len(resource_types)} resource types")
    return structured_data

def _determine_resource_type(url: str, mime_type: str, har_resource_type: Optional[str] = None) -> str:
    """Determine resource type from URL, MIME type, and HAR data"""
    
    # Use HAR resource type if available
    if har_resource_type and har_resource_type != 'other':
        return har_resource_type
    
    # Check MIME type
    if mime_type:
        if 'javascript' in mime_type or 'application/json' in mime_type:
            return 'script'
        elif 'text/css' in mime_type:
            return 'stylesheet'
        elif 'image/' in mime_type:
            return 'image'
        elif 'font/' in mime_type or 'application/font' in mime_type:
            return 'font'
        elif 'text/html' in mime_type:
            return 'document'
        elif 'video/' in mime_type:
            return 'media'
        elif 'audio/' in mime_type:
            return 'media'
    
    # Check URL extension
    url_lower = url.lower()
    if any(ext in url_lower for ext in ['.js', '.jsx', '.ts', '.tsx']):
        return 'script'
    elif any(ext in url_lower for ext in ['.css', '.scss', '.sass']):
        return 'stylesheet'
    elif any(ext in url_lower for ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp', '.ico']):
        return 'image'
    elif any(ext in url_lower for ext in ['.woff', '.woff2', '.ttf', '.eot', '.otf']):
        return 'font'
    elif any(ext in url_lower for ext in ['.html', '.htm']):
        return 'document'
    elif any(ext in url_lower for ext in ['.mp4', '.avi', '.mov', '.wmv', '.mp3', '.wav']):
        return 'media'
    
    return 'other'

def _calculate_performance_metrics(requests: List[Dict], page_timings: Dict, total_size: int) -> Dict[str, Any]:
    """Calculate key performance metrics from requests data"""
    
    if not requests:
        return {}
    
    # Timing metrics
    dom_ready_time = page_timings.get('onContentLoad', 0) / 1000  # Convert to seconds
    page_load_time = page_timings.get('onLoad', 0) / 1000
    
    # Request timing analysis
    request_times = [req['time'] for req in requests if req['time'] > 0]
    avg_request_time = sum(request_times) / len(request_times) if request_times else 0
    max_request_time = max(request_times) if request_times else 0
    
    # DNS/Connection timing analysis
    dns_times = [req['timings']['dns'] for req in requests if req['timings']['dns'] > 0]
    ssl_times = [req['timings']['ssl'] for req in requests if req['timings']['ssl'] > 0]
    connect_times = [req['timings']['connect'] for req in requests if req['timings']['connect'] > 0]
    
    avg_dns_time = sum(dns_times) / len(dns_times) if dns_times else 0
    avg_ssl_time = sum(ssl_times) / len(ssl_times) if ssl_times else 0
    avg_connect_time = sum(connect_times) / len(connect_times) if connect_times else 0
    
    # Performance grade calculation
    performance_grade = _calculate_performance_grade(page_load_time, len(requests))
    
    # Resource type breakdown
    resource_breakdown = {}
    for req in requests:
        rtype = req['resource_type']
        if rtype not in resource_breakdown:
            resource_breakdown[rtype] = {'count': 0, 'size': 0, 'time': 0}
        resource_breakdown[rtype]['count'] += 1
        resource_breakdown[rtype]['size'] += req['size']
        resource_breakdown[rtype]['time'] += req['time']
    
    return {
        'dom_ready_time': dom_ready_time,
        'page_load_time': page_load_time,
        'performance_grade': performance_grade,
        'avg_request_time': round(avg_request_time, 2),
        'max_request_time': round(max_request_time, 2),
        'avg_dns_time': round(avg_dns_time, 2),
        'avg_ssl_time': round(avg_ssl_time, 2),
        'avg_connect_time': round(avg_connect_time, 2),
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'resource_breakdown': resource_breakdown
    }

def _calculate_performance_grade(page_load_time: float, total_requests: int) -> str:
    """Calculate performance grade based on load time and request count"""
    
    if page_load_time < 3.0 and total_requests < 50:
        return 'EXCELLENT'
    elif page_load_time < 3.0:
        return 'GOOD'
    elif page_load_time < 5.0:
        return 'FAIR'
    elif page_load_time < 10.0:
        return 'POOR'
    else:
        return 'CRITICAL'

def save_broken_har_data(broken_data: Dict[str, Any], output_dir: str) -> str:
    """
    Save broken HAR data to structured JSON files
    
    Args:
        broken_data: Structured HAR data from extract_har_data()
        output_dir: Directory to save the broken down data
        
    Returns:
        Path to the output directory
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # Save main breakdown
    breakdown_file = os.path.join(output_dir, 'har_breakdown.json')
    with open(breakdown_file, 'w', encoding='utf-8') as f:
        json.dump(broken_data, f, indent=2, ensure_ascii=False)
    
    # Save individual components for easy access
    components = {
        'metadata.json': broken_data['metadata'],
        'page_timings.json': broken_data['page_timings'],
        'metrics.json': broken_data['metrics'],
        'requests.json': broken_data['requests'][:100],  # Limit for readability
        'resource_types.json': {k: v[:10] for k, v in broken_data['resource_types'].items()},  # Limit per type
        'failed_requests.json': broken_data['failed_requests'],
        'slow_requests.json': broken_data['slow_requests'],
        'totals.json': broken_data['totals']
    }
    
    for filename, data in components.items():
        filepath = os.path.join(output_dir, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saved broken HAR data to: {output_dir}")
    return output_dir

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Break down HAR files for analysis")
    parser.add_argument('--har', required=True, help='Path to HAR file')
    parser.add_argument('--output', help='Output directory (default: har_breakdown_<filename>)')
    
    args = parser.parse_args()
    
    # Determine output directory
    if not args.output:
        har_name = Path(args.har).stem
        args.output = f"har_breakdown_{har_name}"
    
    try:
        # Break down HAR file
        broken_data = extract_har_data(args.har)
        
        # Save to files
        output_dir = save_broken_har_data(broken_data, args.output)
        
        print(f"✅ HAR breakdown complete!")
        print(f"📊 Total requests: {broken_data['totals']['total_requests']}")
        print(f"📁 Output: {output_dir}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        exit(1)
