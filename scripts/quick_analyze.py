#!/usr/bin/env python3
"""
Quick HAR Analysis Tool for AI Agents
- Automatically detects and analyzes HAR files
- Provides structured JSON output for easy parsing
- Minimal dependencies, maximum efficiency
"""

import os
import sys
import json
from pathlib import Path

def find_har_files():
    """Find HAR files in current directory and subdirectories"""
    har_files = []
    
    # Check current directory
    har_files.extend(Path(".").glob("*.har"))
    
    # Check HAR-Files subdirectory
    har_files_dir = Path("HAR-Files")
    if har_files_dir.exists():
        har_files.extend(har_files_dir.glob("*.har"))
    
    return har_files

def analyze_har_quick(har_file):
    """Quick analysis of HAR file without breaking it down"""
    try:
        with open(har_file, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data['log']['entries']
        pages = har_data['log']['pages']
        
        # Basic metrics
        total_requests = len(entries)
        page_load_time = pages[0]['pageTimings']['onLoad'] / 1000 if pages else 0
        dom_ready_time = pages[0]['pageTimings']['onContentLoad'] / 1000 if pages else 0
        
        # Request analysis
        failed_requests = [e for e in entries if e['response']['status'] >= 400]
        slow_requests = [e for e in entries if e['time'] > 1000]
        
        # Size analysis
        total_size = sum(e['response']['content'].get('size', 0) for e in entries)
        largest_assets = sorted(
            [(e['request']['url'], e['response']['content'].get('size', 0)) 
             for e in entries if e['response']['content'].get('size', 0) > 0],
            key=lambda x: x[1], reverse=True
        )[:5]
        
        # Resource type breakdown
        resource_types = {}
        for entry in entries:
            rtype = entry.get('_resourceType', 'unknown')
            if rtype not in resource_types:
                resource_types[rtype] = 0
            resource_types[rtype] += 1
        
        # Performance grade
        if page_load_time > 10:
            grade = "CRITICAL"
        elif page_load_time > 5:
            grade = "POOR"
        elif page_load_time > 3:
            grade = "FAIR"
        else:
            grade = "GOOD"
        
        return {
            "file": os.path.basename(har_file),
            "summary": {
                "total_requests": total_requests,
                "page_load_time": f"{page_load_time:.2f}s",
                "dom_ready_time": f"{dom_ready_time:.2f}s",
                "performance_grade": grade,
                "total_size_mb": f"{total_size / (1024*1024):.2f}MB"
            },
            "issues": {
                "failed_requests": len(failed_requests),
                "slow_requests": len(slow_requests),
                "excessive_requests": total_requests > 100
            },
            "resources": resource_types,
            "largest_assets": [
                {"url": url[:80] + "..." if len(url) > 80 else url, "size_kb": f"{size/1024:.1f}KB"}
                for url, size in largest_assets
            ],
            "failed_requests": [
                {"url": req['request']['url'], "status": req['response']['status']}
                for req in failed_requests
            ]
        }
    
    except Exception as e:
        return {"error": f"Failed to analyze HAR file: {str(e)}"}

def main():
    """Main function for quick HAR analysis"""
    print("🔍 Quick HAR Analysis Tool")
    print("=" * 30)
    
    # Find HAR files
    har_files = find_har_files()
    
    if not har_files:
        print("❌ No HAR files found in current directory or HAR-Files subdirectory")
        return
    
    # Analyze each HAR file
    for har_file in har_files:
        print(f"\n📊 Analyzing: {har_file.name}")
        print("-" * 50)
        
        result = analyze_har_quick(har_file)
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            continue
        
        # Print summary
        summary = result['summary']
        print(f"📈 Performance Grade: {summary['performance_grade']}")
        print(f"⏱️  Page Load Time: {summary['page_load_time']}")
        print(f"🌐 DOM Ready Time: {summary['dom_ready_time']}")
        print(f"📊 Total Requests: {summary['total_requests']}")
        print(f"💾 Total Size: {summary['total_size_mb']}")
        
        # Print issues
        issues = result['issues']
        if issues['failed_requests'] > 0:
            print(f"❌ Failed Requests: {issues['failed_requests']}")
        if issues['slow_requests'] > 0:
            print(f"🐌 Slow Requests (>1s): {issues['slow_requests']}")
        if issues['excessive_requests']:
            print(f"⚠️  Excessive Requests: {summary['total_requests']} (target: <100)")
        
        # Print largest assets
        if result['largest_assets']:
            print("\n🏋️  Largest Assets:")
            for asset in result['largest_assets'][:3]:
                print(f"   • {asset['size_kb']} - {asset['url']}")
        
        # Save detailed JSON for agent consumption
        output_file = f"quick_analysis_{har_file.stem}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2)
        print(f"\n💾 Detailed analysis saved to: {output_file}")

if __name__ == "__main__":
    main()
