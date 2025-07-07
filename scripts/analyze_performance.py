"""
Python script equivalent of analyze_performance.ps1
- Reads HAR summary and header JSON files
- Analyzes and prints performance metrics, timing, errors, resource breakdown, third-party impact, and recommendations
- Uses only standard libraries
"""
import os
import sys
import json
from pathlib import Path

print("DEBUG: analyze_performance.py module being imported/executed")
print(f"DEBUG: __name__ = {__name__}")

# --- Helper functions ---
def print_info(msg):
    print(f"[INFO] {msg}")
def print_ok(msg):
    print(f"[OK] {msg}")
def print_warn(msg):
    print(f"[WARNING] {msg}")
def print_error(msg):
    print(f"[ERROR] {msg}")
def print_section(title):
    print(f"\n{'='*len(title)}\n{title}\n{'='*len(title)}")

def auto_detect_har_file(root_dir):
    # First check current directory
    har_files = list(Path(root_dir).glob('*.har'))
    
    # If no HAR files in current dir, check HAR-Files subdirectory
    if not har_files:
        har_files_dir = Path(root_dir) / "HAR-Files"
        if har_files_dir.exists():
            har_files = list(har_files_dir.glob('*.har'))
    
    if not har_files:
        print_error("No HAR files found in current directory or HAR-Files subdirectory!")
        sys.exit(1)
    elif len(har_files) == 1:
        print_ok(f"Auto-detected HAR file: {har_files[0].name}")
        return str(har_files[0])
    else:
        print_info("Multiple HAR files found:")
        for idx, f in enumerate(har_files, 1):
            print(f"  [{idx}] {f.name}")
        # For agent usage, automatically select the first one
        print_info("Auto-selecting first HAR file for agent usage...")
        return str(har_files[0])

def main(har_file=None, input_dir=None):
    print(f"DEBUG: Legacy analyze_performance.main called with har_file={har_file}, input_dir={input_dir}")
    print(f"DEBUG: __name__ = {__name__}")
    import traceback
    print("DEBUG: Call stack:")
    traceback.print_stack()
    print_info("Advanced HAR Analysis Starting...")
    print("==================================")
    # Auto-detect HAR file if not specified
    if not har_file:
        har_file = auto_detect_har_file(".")  # Work in current directory
    har_base = Path(har_file).stem
    if not input_dir:
        input_dir = os.path.join("har_chunks", har_base)  # Look in current directory
    print_info(f"Using input directory: {input_dir}")
    if not os.path.isdir(input_dir):
        print_error(f"Input directory '{input_dir}' not found!")
        print_warn("Run the HAR breakdown script first: break_har_file.ps1")
        sys.exit(1)
    # Load summary and header
    try:
        with open(os.path.join(input_dir, "02_requests_summary.json"), encoding="utf-8") as f:
            summary = json.load(f)
        with open(os.path.join(input_dir, "01_header_and_metadata.json"), encoding="utf-8") as f:
            header = json.load(f)
    except Exception as e:
        print_error(f"Failed to load summary/header: {e}")
        sys.exit(1)
    # --- PERFORMANCE OVERVIEW ---
    print("\n[METRICS] PERFORMANCE OVERVIEW\n------------------------")
    total_entries = summary.get('totalEntries', 0)
    page = header['log']['pages'][0]
    dom_ready = round(page['pageTimings']['onContentLoad']/1000, 2)
    page_load = round(page['pageTimings']['onLoad']/1000, 2)
    print(f"Total Requests: {total_entries}")
    print(f"DOM Ready Time: {dom_ready}s")
    print(f"Page Load Time: {page_load}s")
    print(f"Site: {page.get('title', '')}")
    # --- REQUEST TIMING ANALYSIS ---
    print("\n[TIMING] REQUEST TIMING ANALYSIS\n---------------------------")
    reqs = summary['requests']
    fast = [r for r in reqs if r['time'] < 200]
    medium = [r for r in reqs if 200 <= r['time'] < 500]
    slow = [r for r in reqs if 500 <= r['time'] < 1000]
    very_slow = [r for r in reqs if r['time'] >= 1000]
    def pct(n):
        return round(n/total_entries*100, 1) if total_entries else 0
    print(f"Fast requests (<200ms): {len(fast)} ({pct(len(fast))}%)")
    print(f"Medium requests (200-500ms): {len(medium)} ({pct(len(medium))}%)")
    print(f"Slow requests (500-1000ms): {len(slow)} ({pct(len(slow))}%)")
    print(f"Very Slow requests (>1000ms): {len(very_slow)} ({pct(len(very_slow))}%)")
    # --- CRITICAL PATH ---
    print("\n[CRITICAL] CRITICAL PATH ANALYSIS (First 10 requests)\n-----------------------------------------------")
    for req in reqs[:10]:
        time = round(req['time'])
        status = '[FAIL]' if req['status'] >= 400 else '[REDIR]' if req['status'] >= 300 else '[OK]'
        url = req['url'][:80]
        print(f"{str(req['entryNumber']).rjust(2)}. [{str(time).rjust(4)}ms] {status} {req['resourceType'].ljust(8)} - {url}")
    # --- FAILED REQUESTS ---
    print("\n[ERROR] FAILED REQUESTS ANALYSIS\n----------------------------")
    failed = [r for r in reqs if r['status'] >= 400]
    if not failed:
        print_ok("No failed requests found!")
    else:
        for r in failed:
            print_error(f"Status {r['status']}: {r['url']}")
    # --- LARGEST RESOURCES ---
    print("\n[SIZE] LARGEST RESOURCES (by response size)\n----------------------------------------")
    largest = sorted([r for r in reqs if r['size'] > 0], key=lambda x: -x['size'])[:10]
    for r in largest:
        size_kb = round(r['size']/1024, 1)
        print(f"{str(size_kb).rjust(6)}KB - {r['resourceType'].ljust(8)} - {r['url'][:80]}")
    # --- SLOWEST REQUESTS ---
    print("\n[SLOW] SLOWEST REQUESTS\n----------------------")
    slowest = sorted(reqs, key=lambda x: -x['time'])[:10]
    for r in slowest:
        time = round(r['time'])
        status = '[FAIL]' if r['status'] >= 400 else '[REDIR]' if r['status'] >= 300 else '[OK]'
        print(f"{str(r['entryNumber']).rjust(2)}. [{str(time).rjust(4)}ms] {status} {r['resourceType'].ljust(8)} - {r['url'][:80]}")
    # --- RESOURCE BREAKDOWN ---
    print("\n[RESOURCES] Resource Breakdown\n-----------------------------")
    from collections import defaultdict
    breakdown = defaultdict(list)
    for r in reqs:
        breakdown[r['resourceType']].append(r)
    stats = []
    for typ, group in breakdown.items():
        total_size = sum(x['size'] for x in group)
        avg_size = round(total_size/len(group)/1024, 1) if group else 0
        total_size_kb = round(total_size/1024, 1)
        stats.append((typ, len(group), total_size_kb, avg_size))
    stats.sort(key=lambda x: -x[2])
    for typ, count, total_kb, avg_kb in stats:
        print(f"{typ.ljust(10)} {str(count).rjust(2)} files | Total: {str(total_kb).rjust(6)}KB | Avg: {str(avg_kb).rjust(5)}KB")
    # --- THIRD-PARTY SERVICES ---
    print("\n[EXTERNAL] THIRD-PARTY SERVICES ANALYSIS\n---------------------------------")
    main_domain = "usecue.com"
    third_party = {}
    for r in reqs:
        try:
            domain = r['url'].split('/')[2]
        except Exception:
            continue
        if domain != main_domain and main_domain not in domain:
            if domain not in third_party:
                third_party[domain] = {'count':0, 'totalTime':0}
            third_party[domain]['count'] += 1
            third_party[domain]['totalTime'] += r['time']
    tp_analysis = []
    for domain, data in third_party.items():
        avg_time = round(data['totalTime']/data['count'], 0) if data['count'] else 0
        impact = data['totalTime'] * data['count']
        tp_analysis.append((domain, data['count'], round(data['totalTime'],0), avg_time, impact))
    tp_analysis.sort(key=lambda x: -x[4])
    for domain, count, total, avg, _ in tp_analysis[:10]:
        print(f"{domain.ljust(40)} {str(count).rjust(2)} req Avg: {str(avg).rjust(4)}ms Total: {str(total).rjust(5)}ms")
    # --- RESOURCE TYPE PERFORMANCE ---
    print("\n[STATS] RESOURCE TYPE PERFORMANCE\n-----------------------------")
    perf_stats = []
    for typ, group in breakdown.items():
        times = [x['time'] for x in group]
        avg_time = round(sum(times)/len(times), 0) if times else 0
        max_time = round(max(times), 0) if times else 0
        total_time = round(sum(times), 0) if times else 0
        perf_stats.append((typ, len(group), avg_time, max_time, total_time))
    perf_stats.sort(key=lambda x: -x[4])
    for typ, count, avg, maxv, total in perf_stats:
        print(f"{typ.ljust(10)} {str(count).rjust(2)} files Avg: {str(avg).rjust(4)}ms Max: {str(maxv).rjust(5)}ms Total: {str(total).rjust(6)}ms")
    # --- RECOMMENDATIONS ---
    print("\n[RECOMMENDATIONS] AUTOMATED RECOMMENDATIONS\n-----------------------------")
    if len(very_slow) > 5:
        print_error(f"{len(very_slow)} requests are taking >1000ms. Investigate and optimize slow resources.")
    if total_entries > 50:
        print_warn(f"{total_entries} total requests. Consider bundling resources (target: under 50).")
    script_count = len([r for r in reqs if r['resourceType'] == 'script'])
    if script_count > 15:
        print_warn(f"{script_count} JavaScript files. Implement bundling and code splitting.")
    if len(failed) > 0:
        print_error(f"{len(failed)} failed requests. Fix broken resources immediately.")
    if dom_ready > 3:
        print_error(f"DOM ready time is {dom_ready}s (target: under 3s). Optimize critical path.")
    if page_load > 5:
        print_error(f"Page load time is {page_load}s (target: under 5s). Major optimization needed.")
    if tp_analysis:
        slowest_tp = tp_analysis[0]
        print_warn(f"Third-party service '{slowest_tp[0]}' is impacting performance. Consider optimization.")
    print_ok("Analysis Complete!")
    print("Check Performance_Analysis_Report.md for detailed recommendations.")
    
    # Generate agent-friendly summary
    print("\n[AGENT SUMMARY] JSON Summary for Agent Consumption")
    print("="*50)
    agent_summary = generate_agent_summary(summary, header)
    print(json.dumps(agent_summary, indent=2))
    
    # Save agent summary to file
    with open(os.path.join(input_dir, "agent_summary.json"), "w", encoding="utf-8") as f:
        json.dump(agent_summary, f, indent=2)
    print_ok("Agent summary saved to agent_summary.json")

def generate_agent_summary(summary, header):
    """Generate a comprehensive summary for AI agent consumption"""
    try:
        reqs = summary['requests']
        total_entries = summary.get('totalEntries', 0)
        page = header['log']['pages'][0]
        dom_ready = round(page['pageTimings']['onContentLoad']/1000, 2)
        page_load = round(page['pageTimings']['onLoad']/1000, 2)
        
        # Performance categorization
        very_slow = [r for r in reqs if r['time'] >= 1000]
        slow = [r for r in reqs if 500 <= r['time'] < 1000]
        failed = [r for r in reqs if r['status'] >= 400]
        
        # Resource breakdown
        from collections import defaultdict
        breakdown = defaultdict(list)
        for r in reqs:
            breakdown[r['resourceType']].append(r)
        
        # Top largest assets
        largest = sorted([r for r in reqs if r['size'] > 0], key=lambda x: -x['size'])[:5]
        
        # Top slowest requests
        slowest = sorted(reqs, key=lambda x: -x['time'])[:5]
        
        return {
            "performance_summary": {
                "total_requests": total_entries,
                "dom_ready_time": f"{dom_ready}s",
                "page_load_time": f"{page_load}s",
                "performance_grade": "CRITICAL" if page_load > 10 else "POOR" if page_load > 5 else "FAIR" if page_load > 3 else "GOOD"
            },
            "critical_issues": {
                "very_slow_requests": len(very_slow),
                "slow_requests": len(slow),
                "failed_requests": len(failed),
                "excessive_requests": total_entries > 100
            },
            "resource_breakdown": {rtype: len(resources) for rtype, resources in breakdown.items()},
            "largest_assets": [{"url": r['url'][:80], "size_kb": round(r['size']/1024, 1)} for r in largest],
            "slowest_requests": [{"url": r['url'][:80], "time_ms": round(r['time'])} for r in slowest],
            "failed_requests": [{"url": r['url'], "status": r['status']} for r in failed]
        }
    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Advanced HAR Analysis (Python)")
    parser.add_argument('--har', dest='har_file', default=None, help='Path to HAR file')
    parser.add_argument('--input', dest='input_dir', default=None, help='Input directory (har_chunks/<basename>)')
    args = parser.parse_args()
    main(har_file=args.har_file, input_dir=args.input_dir)
