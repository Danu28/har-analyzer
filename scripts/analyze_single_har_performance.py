"""
Single HAR Performance Analysis
===============================
Analyzes performance metrics from a single HAR file breakdown.
Reads HAR summary and header JSON files to generate comprehensive performance insights.

Purpose: Single HAR file analysis workflow (not comparison)
Generates agent_summary.json for report generation.
Uses only standard libraries for maximum compatibility.
"""

import json
import os
import sys
from pathlib import Path
import re
from urllib.parse import urlparse
from collections import defaultdict

# Optional dependency for enhanced HTML parsing
try:
    from bs4 import BeautifulSoup
    HAS_BEAUTIFULSOUP = True
except ImportError:
    HAS_BEAUTIFULSOUP = False


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
    har_files = list(Path(root_dir).glob("*.har"))

    # If no HAR files in current dir, check HAR-Files subdirectory
    if not har_files:
        har_files_dir = Path(root_dir) / "HAR-Files"
        if har_files_dir.exists():
            har_files = list(har_files_dir.glob("*.har"))

    if not har_files:
        print_error(
            "No HAR files found in current directory or HAR-Files subdirectory!"
        )
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
    print(
        f"DEBUG: Legacy analyze_performance.main called with har_file={har_file}, input_dir={input_dir}"
    )
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
        print_warn("Run the HAR breakdown script first: break_har_file.py")
        sys.exit(1)
    # Load summary and header
    try:
        with open(
            os.path.join(input_dir, "02_requests_summary.json"), encoding="utf-8"
        ) as f:
            summary = json.load(f)
        with open(
            os.path.join(input_dir, "01_header_and_metadata.json"), encoding="utf-8"
        ) as f:
            header = json.load(f)
    except Exception as e:
        print_error(f"Failed to load summary/header: {e}")
        sys.exit(1)
    # --- PERFORMANCE OVERVIEW ---
    print("\n[METRICS] PERFORMANCE OVERVIEW\n------------------------")
    total_entries = summary.get("totalEntries", 0)
    page = header["log"]["pages"][0]
    
    # Safely extract timing data with null checks
    page_timings = page.get("pageTimings", {})
    on_content_load = page_timings.get("onContentLoad")
    on_load = page_timings.get("onLoad")
    
    # Convert to seconds with null safety
    dom_ready = round(on_content_load / 1000, 2) if on_content_load is not None else None
    page_load = round(on_load / 1000, 2) if on_load is not None else None
    
    print(f"Total Requests: {total_entries}")
    print(f"DOM Ready Time: {dom_ready}s" if dom_ready is not None else "DOM Ready Time: Not available")
    print(f"Page Load Time: {page_load}s" if page_load is not None else "Page Load Time: Not available")
    print(f"Site: {page.get('title', '')}")
    # --- REQUEST TIMING ANALYSIS ---
    print("\n[TIMING] REQUEST TIMING ANALYSIS\n---------------------------")
    reqs = summary["requests"]
    fast = [r for r in reqs if r["time"] < 200]
    medium = [r for r in reqs if 200 <= r["time"] < 500]
    slow = [r for r in reqs if r["time"] >= 500]
    very_slow = [r for r in reqs if r["time"] >= 1000]

    def pct(n):
        return round(n / total_entries * 100, 1) if total_entries else 0

    print(f"Fast requests (<200ms): {len(fast)} ({pct(len(fast))}%)")
    print(f"Medium requests (200-500ms): {len(medium)} ({pct(len(medium))}%)")
    print(f"Slow requests (500-1000ms): {len(slow)} ({pct(len(slow))}%)")
    print(f"Very Slow requests (>1000ms): {len(very_slow)} ({pct(len(very_slow))}%)")
    # --- CRITICAL PATH ---
    print(
        "\n[CRITICAL] CRITICAL PATH ANALYSIS (First 10 requests)\n-----------------------------------------------"
    )
    for req in reqs[:10]:
        time = round(req["time"])
        status = (
            "[FAIL]"
            if req["status"] >= 400
            else "[REDIR]" if req["status"] >= 300 else "[OK]"
        )
        url = req["url"][:80]
        print(
            f"{str(req['entryNumber']).rjust(2)}. [{str(time).rjust(4)}ms] {status} {req['resourceType'].ljust(8)} - {url}"
        )
    # --- FAILED REQUESTS ---
    print("\n[ERROR] FAILED REQUESTS ANALYSIS\n----------------------------")
    failed = [r for r in reqs if r["status"] >= 400]
    if not failed:
        print_ok("No failed requests found!")
    else:
        for r in failed:
            print_error(f"Status {r['status']}: {r['url']}")
    # --- LARGEST RESOURCES ---
    print(
        "\n[SIZE] LARGEST RESOURCES (by response size)\n----------------------------------------"
    )
    largest = sorted([r for r in reqs if r["size"] > 0], key=lambda x: -x["size"])[:10]
    for r in largest:
        size_kb = round(r["size"] / 1024, 1)
        print(
            f"{str(size_kb).rjust(6)}KB - {r['resourceType'].ljust(8)} - {r['url'][:80]}"
        )
    # --- SLOWEST REQUESTS ---
    print("\n[SLOW] SLOWEST REQUESTS\n----------------------")
    slowest = sorted(reqs, key=lambda x: -x["time"])[:10]
    for r in slowest:
        time = round(r["time"])
        status = (
            "[FAIL]"
            if r["status"] >= 400
            else "[REDIR]" if r["status"] >= 300 else "[OK]"
        )
        print(
            f"{str(r['entryNumber']).rjust(2)}. [{str(time).rjust(4)}ms] {status} {r['resourceType'].ljust(8)} - {r['url'][:80]}"
        )
    # --- RESOURCE BREAKDOWN ---
    print("\n[RESOURCES] Resource Breakdown\n-----------------------------")
    from collections import defaultdict

    breakdown = defaultdict(list)
    for r in reqs:
        breakdown[r["resourceType"]].append(r)
    stats = []
    for typ, group in breakdown.items():
        total_size = sum(x["size"] for x in group)
        avg_size = round(total_size / len(group) / 1024, 1) if group else 0
        total_size_kb = round(total_size / 1024, 1)
        stats.append((typ, len(group), total_size_kb, avg_size))
    stats.sort(key=lambda x: -x[2])
    for typ, count, total_kb, avg_kb in stats:
        print(
            f"{typ.ljust(10)} {str(count).rjust(2)} files | Total: {str(total_kb).rjust(6)}KB | Avg: {str(avg_kb).rjust(5)}KB"
        )
    # --- THIRD-PARTY SERVICES ---
    print(
        "\n[EXTERNAL] THIRD-PARTY SERVICES ANALYSIS\n---------------------------------"
    )
    main_domain = "usecue.com"
    third_party = {}
    for r in reqs:
        try:
            domain = r["url"].split("/")[2]
        except Exception:
            continue
        if domain != main_domain and main_domain not in domain:
            if domain not in third_party:
                third_party[domain] = {"count": 0, "totalTime": 0}
            third_party[domain]["count"] += 1
            third_party[domain]["totalTime"] += r["time"]
    tp_analysis = []
    for domain, data in third_party.items():
        avg_time = round(data["totalTime"] / data["count"], 0) if data["count"] else 0
        impact = data["totalTime"] * data["count"]
        tp_analysis.append(
            (domain, data["count"], round(data["totalTime"], 0), avg_time, impact)
        )
    tp_analysis.sort(key=lambda x: -x[4])
    for domain, count, total, avg, _ in tp_analysis[:10]:
        print(
            f"{domain.ljust(40)} {str(count).rjust(2)} req Avg: {str(avg).rjust(4)}ms Total: {str(total).rjust(5)}ms"
        )
    # --- RESOURCE TYPE PERFORMANCE ---
    print("\n[STATS] RESOURCE TYPE PERFORMANCE\n-----------------------------")
    perf_stats = []
    for typ, group in breakdown.items():
        times = [x["time"] for x in group]
        avg_time = round(sum(times) / len(times), 0) if times else 0
        max_time = round(max(times), 0) if times else 0
        total_time = round(sum(times), 0) if times else 0
        perf_stats.append((typ, len(group), avg_time, max_time, total_time))
    perf_stats.sort(key=lambda x: -x[4])
    for typ, count, avg, maxv, total in perf_stats:
        print(
            f"{typ.ljust(10)} {str(count).rjust(2)} files Avg: {str(avg).rjust(4)}ms Max: {str(maxv).rjust(5)}ms Total: {str(total).rjust(6)}ms"
        )
    # --- RECOMMENDATIONS ---
    print(
        "\n[RECOMMENDATIONS] AUTOMATED RECOMMENDATIONS\n-----------------------------"
    )
    if len(very_slow) > 5:
        print_error(
            f"{len(very_slow)} requests are taking >1000ms. Investigate and optimize slow resources."
        )
    if total_entries > 50:
        print_warn(
            f"{total_entries} total requests. Consider bundling resources (target: under 50)."
        )
    script_count = len([r for r in reqs if r["resourceType"] == "script"])
    if script_count > 15:
        print_warn(
            f"{script_count} JavaScript files. Implement bundling and code splitting."
        )
    if len(failed) > 0:
        print_error(f"{len(failed)} failed requests. Fix broken resources immediately.")
    if dom_ready is not None and dom_ready > 3:
        print_error(
            f"DOM ready time is {dom_ready}s (target: under 3s). Optimize critical path."
        )
    if page_load is not None and page_load > 5:
        print_error(
            f"Page load time is {page_load}s (target: under 5s). Major optimization needed."
        )
    if tp_analysis:
        slowest_tp = tp_analysis[0]
        print_warn(
            f"Third-party service '{slowest_tp[0]}' is impacting performance. Consider optimization."
        )

    # --- PHASE 1 ENHANCEMENTS ---
    print("\n[COMPRESSION] COMPRESSION ANALYSIS\n-----------------------------")
    compression_analysis = analyze_compression(reqs)
    if compression_analysis["compression_opportunity_count"] > 0:
        print_error(
            f"Found {compression_analysis['compression_opportunity_count']} uncompressed text resources"
        )
        print_warn(
            f"Potential savings: {compression_analysis['total_potential_savings_kb']}KB"
        )
        print("Top uncompressed resources:")
        for resource in compression_analysis["uncompressed_resources"][:5]:
            print(f"  - {resource['url'][:60]} ({round(resource['size']/1024, 1)}KB)")
    else:
        print_ok("Good compression usage detected!")

    print("\n[CACHING] CACHE ANALYSIS\n-----------------------")
    cache_analysis = analyze_caching(reqs)
    if cache_analysis["cache_optimization_count"] > 0:
        print_error(
            f"Found {len(cache_analysis['no_cache_resources'])} resources without cache headers"
        )
        print_warn(
            f"Found {len(cache_analysis['short_cache_resources'])} resources with short cache duration"
        )
        print("Resources needing cache optimization:")
        for resource in cache_analysis["no_cache_resources"][:3]:
            print(f"  - {resource['url'][:60]} ({resource['resourceType']})")
    else:
        print_ok("Good caching strategy detected!")

    print(
        "\n[DNS/CONNECTION] NETWORK TIMING ANALYSIS\n---------------------------------------"
    )
    dns_analysis = analyze_dns_connection_timing(reqs)
    # Handle N/A case for DNS/SSL timings
    avg_dns = dns_analysis["avg_dns_time"]
    avg_ssl = dns_analysis["avg_ssl_time"]
    if avg_dns == "N/A":
        print_warn("Average DNS time: N/A (no valid timing data)")
    elif avg_dns > 50:
        print_warn(f"Average DNS time: {avg_dns}ms (target: <50ms)")
    else:
        print_ok(f"Average DNS time: {avg_dns}ms")
    if avg_ssl == "N/A":
        print_warn("Average SSL time: N/A (no valid timing data)")
    elif avg_ssl > 200:
        print_warn(f"Average SSL time: {avg_ssl}ms (target: <200ms)")
    else:
        print_ok(f"Average SSL time: {avg_ssl}ms")

    print("Top domains by performance impact:")
    for domain_stat in dns_analysis["domain_performance"][:5]:
        print(
            f"  - {domain_stat['domain'][:40]} ({domain_stat['requests']} req, {domain_stat['total_time_ms']}ms total)"
        )

    print(
        "\n[THIRD-PARTY] ENHANCED THIRD-PARTY ANALYSIS\n------------------------------------------"
    )
    enhanced_tp_analysis = analyze_enhanced_third_party(reqs)
    print(
        f"Total third-party domains: {enhanced_tp_analysis['total_third_party_domains']}"
    )

    print("\nThird-party impact by category:")
    for category, stats in enhanced_tp_analysis["category_breakdown"].items():
        print(
            f"  {category.ljust(12)}: {stats['domains']} domains, {stats['requests']} requests, {round(stats['total_time'])}ms total"
        )

    if enhanced_tp_analysis["blocking_third_parties"]:
        print_error(
            f"Blocking third-parties detected: {', '.join(enhanced_tp_analysis['blocking_third_parties'])}"
        )

    print(
        "\n[CRITICAL PATH] CRITICAL RENDERING PATH ANALYSIS\n-----------------------------------------------"
    )
    
    # Reconstruct full HAR data for critical path analysis
    full_har_data = None
    try:
        # Start with header data
        full_har_data = dict(header)
        
        # Load and combine all request chunks to get entries
        entries = []
        chunk_files = sorted([f for f in os.listdir(input_dir) if f.startswith("03_requests_chunk_")])
        
        for chunk_file in chunk_files:
            chunk_path = os.path.join(input_dir, chunk_file)
            try:
                with open(chunk_path, 'r', encoding='utf-8') as f:
                    chunk_data = json.load(f)
                    entries.extend(chunk_data.get('entries', []))
            except Exception as e:
                print_warn(f"Failed to load chunk {chunk_file}: {e}")
        
        # Add entries to the full HAR data
        if 'log' not in full_har_data:
            full_har_data['log'] = {}
        full_har_data['log']['entries'] = entries
        
        print_info(f"Reconstructed HAR data with {len(entries)} entries for critical path analysis")
        
    except Exception as e:
        print_warn(f"Failed to reconstruct HAR data: {e}")
        full_har_data = header  # Fallback to header only
    
    critical_path_analysis = analyze_critical_path(full_har_data, reqs)
    
    if critical_path_analysis.get("analysis_available", False):
        blocking_count = critical_path_analysis["blocking_resources_count"]
        css_count = critical_path_analysis.get("css_blocking_count", 0)
        js_count = critical_path_analysis.get("js_blocking_count", 0)
        critical_time = critical_path_analysis["critical_path_time_ms"]
        
        # Show source document info
        source_doc = critical_path_analysis.get("source_document", {})
        if source_doc:
            print(f"Analyzing document: {source_doc.get('url', 'Unknown')[:80]}...")
            print(f"Document content: {source_doc.get('content_length', 0):,} characters")
        
        # Show blocking resources summary
        print(f"Render-blocking resources found: {blocking_count}")
        if css_count > 0:
            print_warn(f"  • {css_count} blocking CSS file(s)")
        if js_count > 0:
            print_warn(f"  • {js_count} blocking JavaScript file(s)")
        
        # Show critical path time
        if critical_time > 0:
            critical_time_formatted = critical_path_analysis.get("critical_path_time_formatted", f"{critical_time}ms")
            if critical_time > 1500:
                print_error(f"Critical path time: {critical_time_formatted} (CRITICAL - optimize immediately)")
            elif critical_time > 800:
                print_warn(f"Critical path time: {critical_time_formatted} (HIGH - optimization recommended)")
            elif critical_time > 400:
                print_warn(f"Critical path time: {critical_time_formatted} (MEDIUM - consider optimization)")
            else:
                print_ok(f"Critical path time: {critical_time_formatted} (LOW impact)")
        
        # Show top blocking resources
        blocking_resources = critical_path_analysis.get("blocking_resources", [])
        if blocking_resources:
            # Sort by load time and show top 3
            top_blocking = sorted(blocking_resources, key=lambda x: x.get('time', 0), reverse=True)[:3]
            print("\nTop blocking resources:")
            for i, resource in enumerate(top_blocking, 1):
                url_short = resource['url'].split('/')[-1] or resource['url'].split('/')[-2]
                size_info = f"{resource.get('size', 0)/1024:.1f}KB" if resource.get('size', 0) > 0 else "Unknown size"
                time_info = f"{resource.get('time', 0):.0f}ms" if resource.get('time', 0) > 0 else "Unknown time"
                found_status = "OK" if resource.get('found_in_har', True) else "MISS"
                print(f"  {i}. [{resource.get('type', 'unknown')}] {url_short} ({size_info}, {time_info}) [{found_status}]")
        
        # Show recommendations
        recommendations = critical_path_analysis.get("recommendations", [])
        if recommendations:
            print("\nCritical path optimization recommendations:")
            for i, rec in enumerate(recommendations[:4], 1):  # Show top 4
                print(f"  {i}. {rec}")
        
        # Overall assessment
        if blocking_count == 0:
            print_ok("Excellent! No render-blocking resources detected in document head")
        elif blocking_count <= 2 and critical_time <= 500:
            print_ok("Good! Minimal render-blocking impact detected")
        elif blocking_count <= 5 and critical_time <= 1000:
            print_warn("WARNING: Moderate render-blocking impact - optimization recommended")
        else:
            print_error("CRITICAL: High render-blocking impact - immediate optimization needed")
            
    else:
        error_msg = critical_path_analysis.get("error", "Unknown error")
        print_warn(f"Critical Path Analysis Unavailable")
        print_error(f"Reason: {error_msg}")
        
        # Show debug information if available
        debug_info = critical_path_analysis.get("debug_info", {})
        if debug_info:
            total_entries = debug_info.get("total_entries", 0)
            print(f"Debug: Found {total_entries} total entries in HAR file")
            
            if "suggestion" in debug_info:
                print_warn(f"TIP: {debug_info['suggestion']}")
            
            if "first_few_urls" in debug_info:
                print("First few URLs in HAR file:")
                for i, url in enumerate(debug_info["first_few_urls"], 1):
                    print(f"  {i}. {url}...")
            
            if "selected_url" in debug_info:
                print(f"Selected document: {debug_info['selected_url']}")

    print_ok("Analysis Complete!")
    print("Check Performance_Analysis_Report.md for detailed recommendations.")

    # Generate agent-friendly summary with enhanced analysis
    print("\n[AGENT SUMMARY] JSON Summary for Agent Consumption")
    print("=" * 50)
    agent_summary = generate_agent_summary(
        summary,
        header,
        {
            "compression": compression_analysis,
            "caching": cache_analysis,
            "dns_connection": dns_analysis,
            "enhanced_third_party": enhanced_tp_analysis,
            "critical_path": critical_path_analysis,
        },
    )
    print(json.dumps(agent_summary, indent=2))

    # Save agent summary to file
    with open(
        os.path.join(input_dir, "agent_summary.json"), "w", encoding="utf-8"
    ) as f:
        json.dump(agent_summary, f, indent=2)
    print_ok("Agent summary saved to agent_summary.json")


def analyze_critical_path(har_data: dict, reqs: list) -> dict:
    """Analyze critical rendering path from HAR data and requests.
    
    Enhanced version with robust HTML document detection and better error handling.
    
    Args:
        har_data: The full HAR file data structure
        reqs: List of processed request objects
        
    Returns:
        Dict containing critical path analysis results
    """
    try:
        entries = har_data.get('log', {}).get('entries', [])
        if not entries:
            return {
                "error": "No entries found in HAR file",
                "blocking_resources": [],
                "analysis_available": False,
                "debug_info": {"total_entries": 0}
            }
        
        # Strategy 1: Find HTML documents with content
        html_candidates = []
        for i, entry in enumerate(entries):
            response = entry.get('response', {})
            content = response.get('content', {})
            request = entry.get('request', {})
            
            url = request.get('url', '')
            method = request.get('method', 'GET')
            status = response.get('status', 0)
            mime_type = content.get('mimeType', '').lower()
            encoding = content.get('encoding', '')
            text = content.get('text', '')
            
            # Multiple criteria for HTML detection
            is_html_mime = 'text/html' in mime_type or 'application/xhtml' in mime_type
            is_html_url = url.endswith('.html') or url.endswith('.htm') or url.endswith('/')
            has_html_content = text and ('<html' in text.lower() or '<head' in text.lower() or '<!doctype html' in text.lower())
            
            # Decode base64 content if needed
            actual_content = text
            if encoding == 'base64' and text:
                try:
                    import base64
                    actual_content = base64.b64decode(text).decode('utf-8', errors='ignore')
                    has_html_content = '<html' in actual_content.lower() or '<head' in actual_content.lower() or '<!doctype html' in actual_content.lower()
                except Exception:
                    actual_content = text
            
            # Consider as HTML candidate if it meets criteria
            if (is_html_mime or is_html_url or has_html_content) and method == 'GET' and status == 200:
                html_candidates.append({
                    'entry': entry,
                    'index': i,
                    'url': url,
                    'mime_type': mime_type,
                    'has_content': bool(actual_content.strip()),
                    'content_length': len(actual_content.strip()) if actual_content else 0,
                    'actual_content': actual_content,
                    'is_main_document': i == 0 or ('/' == url.split('/')[-1] and len(url.split('/')) <= 4)  # Heuristic for main document
                })
        
        if not html_candidates:
            return {
                "error": "No HTML document found in HAR file",
                "blocking_resources": [],
                "analysis_available": False,
                "debug_info": {
                    "total_entries": len(entries),
                    "suggestion": "Ensure HAR capture includes main HTML document with response body",
                    "first_few_urls": [entries[i].get('request', {}).get('url', '')[:100] for i in range(min(3, len(entries)))]
                }
            }
        
        # Strategy 2: Select the best HTML candidate
        # Prioritize main document, then by content length
        best_candidate = None
        
        # First, try to find the main document (usually first entry or root path)
        main_docs = [c for c in html_candidates if c['is_main_document'] and c['has_content']]
        if main_docs:
            best_candidate = max(main_docs, key=lambda x: x['content_length'])
        
        # Fallback: find any HTML document with content
        if not best_candidate:
            content_docs = [c for c in html_candidates if c['has_content']]
            if content_docs:
                best_candidate = max(content_docs, key=lambda x: x['content_length'])
        
        # Last resort: take any HTML document (even without content)
        if not best_candidate:
            best_candidate = html_candidates[0]
        
        html_content = best_candidate['actual_content']
        if not html_content or not html_content.strip():
            return {
                "error": f"HTML document found but content is empty (URL: {best_candidate['url']})",
                "blocking_resources": [],
                "analysis_available": False,
                "debug_info": {
                    "selected_url": best_candidate['url'],
                    "html_candidates_count": len(html_candidates),
                    "suggestion": "Ensure HAR capture includes response bodies (check DevTools settings)"
                }
            }
        
        # Parse critical resources from HTML
        blocking_resources = parse_critical_resources(html_content, reqs)
        
        # Calculate critical path metrics
        critical_path_time = calculate_critical_path_time(blocking_resources)
        recommendations = generate_critical_path_recommendations(blocking_resources)
        
        return {
            "blocking_resources": blocking_resources,
            "blocking_resources_count": len(blocking_resources),
            "css_blocking_count": len([r for r in blocking_resources if r.get('type') == 'stylesheet']),
            "js_blocking_count": len([r for r in blocking_resources if r.get('type') == 'script']),
            "critical_path_time_ms": critical_path_time,
            "critical_path_time_formatted": f"{critical_path_time:.0f}ms",
            "has_render_blocking_css": any(r.get("type") == "stylesheet" for r in blocking_resources),
            "has_render_blocking_js": any(r.get("type") == "script" for r in blocking_resources),
            "recommendations": recommendations,
            "analysis_available": True,
            "source_document": {
                "url": best_candidate['url'],
                "content_length": best_candidate['content_length'],
                "index": best_candidate['index']
            }
        }
        
    except Exception as e:
        return {
            "error": f"Critical path analysis failed: {str(e)}",
            "blocking_resources": [],
            "analysis_available": False,
            "debug_info": {"exception": str(e)}
        }


def parse_critical_resources(html_content: str, reqs: list) -> list:
    """Parse HTML to identify critical rendering path resources.
    
    Args:
        html_content: The HTML content of the main document
        reqs: List of all requests for correlation
        
    Returns:
        List of critical path resources
    """
    blocking_resources = []
    
    # Create a lookup for fast request correlation
    url_to_request = {req['url']: req for req in reqs}
    
    if HAS_BEAUTIFULSOUP:
        # Use BeautifulSoup for robust HTML parsing
        blocking_resources = parse_with_beautifulsoup(html_content, url_to_request)
    else:
        # Fallback to regex-based parsing
        blocking_resources = parse_with_regex(html_content, url_to_request)
    
    return blocking_resources


def parse_with_beautifulsoup(html_content: str, url_to_request: dict) -> list:
    """Parse HTML using BeautifulSoup to find critical resources."""
    try:
        # Limit HTML content to first 1MB to prevent memory issues
        html_content = html_content[:1024*1024]
        soup = BeautifulSoup(html_content, 'html.parser')
        blocking_resources = []
        
        # Find head section
        head = soup.find('head')
        if not head:
            return []
        
        # Find all stylesheets in head (always render-blocking)
        for link in head.find_all('link', rel='stylesheet'):
            href = link.get('href')
            if href:
                # Convert relative URLs to absolute if needed
                resource = correlate_with_request(href, url_to_request, 'stylesheet')
                if resource:
                    blocking_resources.append(resource)
        
        # Find all scripts in head without async/defer (render-blocking)
        for script in head.find_all('script'):
            src = script.get('src')
            if src and not script.get('async') and not script.get('defer'):
                resource = correlate_with_request(src, url_to_request, 'script')
                if resource:
                    blocking_resources.append(resource)
        
        return blocking_resources
        
    except Exception as e:
        print_warn(f"BeautifulSoup parsing failed: {e}, falling back to regex")
        return parse_with_regex(html_content, url_to_request)


def parse_with_regex(html_content: str, url_to_request: dict) -> list:
    """Parse HTML using regex patterns as fallback method."""
    blocking_resources = []
    
    # Limit content size for performance
    html_content = html_content[:1024*1024]
    
    # Find head section
    head_match = re.search(r'<head[^>]*>(.*?)</head>', html_content, re.DOTALL | re.IGNORECASE)
    if not head_match:
        return []
    
    head_content = head_match.group(1)
    
    # Find stylesheets (always render-blocking)
    css_pattern = r'<link[^>]*rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)["\'][^>]*>'
    for match in re.finditer(css_pattern, head_content, re.IGNORECASE):
        href = match.group(1)
        resource = correlate_with_request(href, url_to_request, 'stylesheet')
        if resource:
            blocking_resources.append(resource)
    
    # Find render-blocking scripts (no async/defer in head)
    script_pattern = r'<script[^>]*src=["\']([^"\']+)["\'][^>]*>'
    for match in re.finditer(script_pattern, head_content, re.IGNORECASE):
        script_tag = match.group(0)
        src = match.group(1)
        
        # Check if script has async or defer attributes
        if not re.search(r'\basync\b', script_tag, re.IGNORECASE) and \
           not re.search(r'\bdefer\b', script_tag, re.IGNORECASE):
            resource = correlate_with_request(src, url_to_request, 'script')
            if resource:
                blocking_resources.append(resource)
    
    return blocking_resources


def correlate_with_request(resource_url: str, url_to_request: dict, resource_type: str) -> dict:
    """Correlate a parsed resource URL with an actual request.
    
    Args:
        resource_url: The URL from HTML parsing
        url_to_request: Dictionary mapping URLs to request objects
        resource_type: Type of resource ('stylesheet' or 'script')
        
    Returns:
        Resource object with timing data, or None if not found
    """
    # Try exact match first
    if resource_url in url_to_request:
        req = url_to_request[resource_url]
        return create_resource_object(req, resource_type)
    
    # Try partial matches for relative URLs
    for url, req in url_to_request.items():
        if url.endswith(resource_url) or resource_url in url:
            return create_resource_object(req, resource_type)
    
    # If no match found, create a minimal object
    return {
        "url": resource_url,
        "type": resource_type,
        "size": 0,
        "time": 0,
        "found_in_har": False
    }


def create_resource_object(req: dict, resource_type: str) -> dict:
    """Create a standardized resource object from a request."""
    return {
        "url": req['url'],
        "type": resource_type,
        "size": req.get('size', 0),
        "time": req.get('time', 0),
        "status": req.get('status', 200),
        "found_in_har": True
    }


def calculate_critical_path_time(blocking_resources: list) -> float:
    """Calculate the total time for critical path resources.
    
    Note: This is a simplified calculation. In reality, resources may load
    in parallel, but this gives an estimate of critical path impact.
    """
    # Get maximum time of blocking resources (assuming parallel loading)
    if not blocking_resources:
        return 0
    
    valid_times = [r['time'] for r in blocking_resources if r.get('found_in_har', True)]
    return max(valid_times) if valid_times else 0


def generate_critical_path_recommendations(blocking_resources: list) -> list:
    """Generate actionable recommendations for critical path optimization."""
    recommendations = []
    
    css_count = sum(1 for r in blocking_resources if r['type'] == 'stylesheet')
    js_count = sum(1 for r in blocking_resources if r['type'] == 'script')
    
    if css_count > 3:
        recommendations.append(f"Consider bundling {css_count} CSS files into fewer files to reduce critical path")
    
    if js_count > 0:
        recommendations.append(f"Add 'async' or 'defer' attributes to {js_count} JavaScript files to prevent render blocking")
    
    large_resources = [r for r in blocking_resources if r.get('size', 0) > 50000]  # >50KB
    if large_resources:
        recommendations.append(f"Optimize {len(large_resources)} large critical resources (>50KB) to improve loading speed")
    
    slow_resources = [r for r in blocking_resources if r.get('time', 0) > 1000]  # >1s
    if slow_resources:
        recommendations.append(f"Investigate {len(slow_resources)} slow-loading critical resources (>1s)")
    
    if css_count > 0:
        recommendations.append("Consider inlining critical CSS for above-the-fold content")
    
    if not recommendations:
        recommendations.append("Critical path appears well-optimized")
    
    return recommendations


def generate_agent_summary(summary, header, enhanced_analysis=None):
    """Generate a comprehensive summary for AI agent consumption"""
    try:
        reqs = summary["requests"]
        total_entries = summary.get("totalEntries", 0)
        page = header["log"]["pages"][0]
        
        # Safely extract timing data with null checks
        page_timings = page.get("pageTimings", {})
        on_content_load = page_timings.get("onContentLoad")
        on_load = page_timings.get("onLoad")
        
        # Convert to seconds with null safety
        dom_ready = round(on_content_load / 1000, 2) if on_content_load is not None else None
        page_load = round(on_load / 1000, 2) if on_load is not None else None

        # Performance categorization
        very_slow = [r for r in reqs if r["time"] >= 1000]
        slow = [r for r in reqs if 500 <= r["time"] < 1000]
        failed = [r for r in reqs if r["status"] >= 400]

        # Resource breakdown
        from collections import defaultdict

        breakdown = defaultdict(list)
        for r in reqs:
            breakdown[r["resourceType"]].append(r)

        # Top largest assets
        largest = sorted([r for r in reqs if r["size"] > 0], key=lambda x: -x["size"])[
            :5
        ]

        # Top slowest requests
        slowest = sorted(reqs, key=lambda x: -x["time"])[:5]

        base_summary = {
            "performance_summary": {
                "total_requests": total_entries,
                "dom_ready_time": f"{dom_ready}s" if dom_ready is not None else "Not available",
                "page_load_time": f"{page_load}s" if page_load is not None else "Not available",
                "performance_grade": (
                    "CRITICAL"
                    if page_load is not None and page_load > 10
                    else (
                        "POOR" if page_load is not None and page_load > 5 
                        else "FAIR" if page_load is not None and page_load > 3 
                        else "GOOD" if page_load is not None
                        else "UNKNOWN"
                    )
                ),
            },
            "critical_issues": {
                "very_slow_requests": len(very_slow),
                "slow_requests": len(slow),
                "failed_requests": len(failed),
                "excessive_requests": total_entries > 100,
            },
            "resource_breakdown": {
                rtype: len(resources) for rtype, resources in breakdown.items()
            },
            "largest_assets": [
                {"url": r["url"][:80], "size_kb": round(r["size"] / 1024, 1)}
                for r in largest
            ],
            "slowest_requests": [
                {"url": r["url"][:80], "time_ms": round(r["time"])} for r in slowest
            ],
            "failed_requests": [
                {"url": r["url"], "status": r["status"]} for r in failed
            ],
        }

        # Add enhanced analysis if provided
        if enhanced_analysis:
            base_summary.update(
                {
                    "compression_analysis": enhanced_analysis.get("compression", {}),
                    "caching_analysis": enhanced_analysis.get("caching", {}),
                    "dns_connection_analysis": enhanced_analysis.get(
                        "dns_connection", {}
                    ),
                    "enhanced_third_party_analysis": enhanced_analysis.get(
                        "enhanced_third_party", {}
                    ),
                    "critical_path_analysis": enhanced_analysis.get("critical_path", {}),
                }
            )

        return base_summary

    except Exception as e:
        return {"error": f"Failed to generate summary: {str(e)}"}


def analyze_compression(requests):
    """Analyze compression usage and opportunities"""

    def get_header_value(headers, name):
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return None

    uncompressed_text = []
    compression_savings = 0
    total_compressible = 0

    for req in requests:
        content_type = (
            get_header_value(req.get("responseHeaders", []), "content-type") or ""
        )
        content_encoding = get_header_value(
            req.get("responseHeaders", []), "content-encoding"
        )
        size = req.get("size", 0)

        # Check if resource is text-based and compressible
        is_text = any(
            t in content_type.lower()
            for t in [
                "text/",
                "application/javascript",
                "application/json",
                "application/xml",
                "application/css",
                "image/svg",
            ]
        )

        if is_text and size > 1024:  # Only check files > 1KB
            total_compressible += size
            if not content_encoding:
                uncompressed_text.append(
                    {
                        "url": req["url"],
                        "size": size,
                        "contentType": content_type,
                        "potential_savings": int(
                            size * 0.7
                        ),  # Estimate 70% compression
                    }
                )
                compression_savings += int(size * 0.7)

    return {
        "uncompressed_resources": uncompressed_text,
        "total_potential_savings_kb": round(compression_savings / 1024, 1),
        "total_compressible_kb": round(total_compressible / 1024, 1),
        "compression_opportunity_count": len(uncompressed_text),
    }


def analyze_caching(requests):
    """Analyze caching headers and opportunities"""

    def get_header_value(headers, name):
        for header in headers:
            if header["name"].lower() == name.lower():
                return header["value"]
        return None

    no_cache = []
    short_cache = []
    good_cache = []
    cache_analysis = {}

    for req in requests:
        headers = req.get("responseHeaders", [])
        cache_control = get_header_value(headers, "cache-control")
        expires = get_header_value(headers, "expires")
        etag = get_header_value(headers, "etag")
        last_modified = get_header_value(headers, "last-modified")

        cache_score = 0
        cache_issues = []

        if not cache_control and not expires:
            no_cache.append(
                {
                    "url": req["url"],
                    "size": req.get("size", 0),
                    "resourceType": req.get("resourceType", "unknown"),
                }
            )
            cache_issues.append("No cache headers")
        else:
            if cache_control:
                if "no-cache" in cache_control or "no-store" in cache_control:
                    cache_issues.append("Caching disabled")
                elif "max-age" in cache_control:
                    # Extract max-age value
                    import re

                    match = re.search(r"max-age=(\d+)", cache_control)
                    if match:
                        max_age = int(match.group(1))
                        if max_age < 3600:  # Less than 1 hour
                            short_cache.append(
                                {
                                    "url": req["url"],
                                    "max_age_hours": round(max_age / 3600, 2),
                                    "resourceType": req.get("resourceType", "unknown"),
                                }
                            )
                            cache_issues.append(f"Short cache duration ({max_age}s)")
                        else:
                            good_cache.append(req["url"])
                            cache_score += 2

            if etag:
                cache_score += 1
            if last_modified:
                cache_score += 1

        if (
            req["url"]
            not in [item["url"] for item in no_cache + short_cache] + good_cache
        ):
            cache_analysis[req["url"]] = {"score": cache_score, "issues": cache_issues}

    # Calculate potential savings from caching
    total_no_cache_size = sum(res.get("size", 0) for res in no_cache)
    total_short_cache_size = sum(res.get("size", 0) for res in short_cache)

    # Convert to KB and round
    total_potential_savings_kb = round(
        (total_no_cache_size + total_short_cache_size) / 1024, 1
    )

    return {
        "no_cache_resources": no_cache[:10],  # Limit to top 10
        "short_cache_resources": short_cache[:10],
        "well_cached_count": len(good_cache),
        "cache_optimization_count": len(no_cache) + len(short_cache),
        "total_potential_savings_kb": total_potential_savings_kb,
    }


def analyze_dns_connection_timing(requests):
    """Analyze DNS resolution and connection timing"""
    dns_times = []
    ssl_times = []
    connection_times = []
    domains = {}

    # Track connection reuse
    total_requests = len(requests)
    reused_connections = 0
    new_connections = 0

    for req in requests:
        timings = req.get("timings", {})
        dns_time = timings.get("dns", -1)
        ssl_time = timings.get("ssl", -1)
        connect_time = timings.get("connect", -1)

        # Extract domain
        from urllib.parse import urlparse

        try:
            domain = urlparse(req["url"]).netloc
        except:
            domain = "unknown"

        if domain not in domains:
            domains[domain] = {
                "requests": 0,
                "dns_times": [],
                "ssl_times": [],
                "connect_times": [],
                "total_time": 0,
            }

        domains[domain]["requests"] += 1
        domains[domain]["total_time"] += req.get("time", 0)

        # Connection reuse analysis
        # If connect_time is 0 or very small (< 10ms), likely reused connection
        if connect_time >= 0:
            if connect_time < 10:  # Connection was reused
                reused_connections += 1
            else:  # New connection established
                new_connections += 1

        if dns_time >= 0:
            dns_times.append(
                {"url": req["url"], "dns_time": dns_time, "domain": domain}
            )
            domains[domain]["dns_times"].append(dns_time)

        if ssl_time >= 0:
            ssl_times.append(
                {"url": req["url"], "ssl_time": ssl_time, "domain": domain}
            )
            domains[domain]["ssl_times"].append(ssl_time)

        if connect_time >= 0:
            connection_times.append(
                {"url": req["url"], "connect_time": connect_time, "domain": domain}
            )
            domains[domain]["connect_times"].append(connect_time)

    # Calculate connection reuse efficiency
    total_connection_data = reused_connections + new_connections
    if total_connection_data > 0:
        connection_reuse_percentage = round(
            (reused_connections / total_connection_data) * 100, 1
        )
    else:
        connection_reuse_percentage = 0

    # Calculate domain-level statistics
    domain_stats = []
    for domain, stats in domains.items():
        avg_dns = (
            sum(stats["dns_times"]) / len(stats["dns_times"])
            if stats["dns_times"]
            else 0
        )
        avg_ssl = (
            sum(stats["ssl_times"]) / len(stats["ssl_times"])
            if stats["ssl_times"]
            else 0
        )
        avg_connect = (
            sum(stats["connect_times"]) / len(stats["connect_times"])
            if stats["connect_times"]
            else 0
        )

        domain_stats.append(
            {
                "domain": domain,
                "requests": stats["requests"],
                "avg_dns_ms": round(avg_dns, 1),
                "avg_ssl_ms": round(avg_ssl, 1),
                "avg_connect_ms": round(avg_connect, 1),
                "total_time_ms": round(stats["total_time"], 1),
            }
        )

    # Sort by total impact
    domain_stats.sort(key=lambda x: x["total_time_ms"], reverse=True)

    # Find slow DNS resolutions (>100ms)
    slow_dns = [item for item in dns_times if item["dns_time"] > 100]
    slow_ssl = [item for item in ssl_times if item["ssl_time"] > 500]

    return {
        "domain_performance": domain_stats[:10],  # Top 10 domains by impact
        "slow_dns_resolutions": sorted(
            slow_dns, key=lambda x: x["dns_time"], reverse=True
        )[:5],
        "slow_ssl_handshakes": sorted(
            slow_ssl, key=lambda x: x["ssl_time"], reverse=True
        )[:5],
        "avg_dns_time": (
            round(sum(item["dns_time"] for item in dns_times) / len(dns_times), 1)
            if dns_times
            else "N/A"
        ),
        "avg_ssl_time": (
            round(sum(item["ssl_time"] for item in ssl_times) / len(ssl_times), 1)
            if ssl_times
            else "N/A"
        ),
        "connection_reuse_percentage": connection_reuse_percentage,
        "reused_connections": reused_connections,
        "new_connections": new_connections,
        "total_connection_requests": total_connection_data,
    }


def analyze_enhanced_third_party(requests):
    """Enhanced third-party analysis with categorization"""
    from urllib.parse import urlparse

    # Known third-party categories
    third_party_categories = {
        "analytics": [
            "google-analytics",
            "googletagmanager",
            "analytics",
            "gtm",
            "ga",
            "mixpanel",
            "segment",
        ],
        "advertising": [
            "doubleclick",
            "adsystem",
            "googlesyndication",
            "facebook.com",
            "adsrvr",
            "amazon-adsystem",
        ],
        "social": [
            "facebook",
            "twitter",
            "linkedin",
            "instagram",
            "pinterest",
            "youtube",
        ],
        "cdn": ["cloudflare", "amazonaws", "cloudfront", "fastly", "jsdelivr", "cdnjs"],
        "performance": ["signalfx", "newrelic", "datadog", "pingdom"],
        "security": ["cookielaw", "onetrust", "cloudflare"],
        "fonts": ["fonts.googleapis", "fonts.gstatic", "typekit"],
        "maps": ["maps.googleapis", "mapbox"],
    }

    def categorize_domain(domain):
        domain_lower = domain.lower()
        for category, keywords in third_party_categories.items():
            if any(keyword in domain_lower for keyword in keywords):
                return category
        return "other"

    third_party_analysis = {}
    domain_impact = {}

    for req in requests:
        try:
            domain = urlparse(req["url"]).netloc
        except:
            domain = "unknown"

        category = categorize_domain(domain)
        time_ms = req.get("time", 0)
        size = req.get("size", 0)

        if domain not in domain_impact:
            domain_impact[domain] = {
                "category": category,
                "requests": 0,
                "total_time": 0,
                "total_size": 0,
                "avg_time": 0,
                "blocking_time": 0,
                "failed_requests": 0,
            }

        domain_impact[domain]["requests"] += 1
        domain_impact[domain]["total_time"] += time_ms
        domain_impact[domain]["total_size"] += size

        # Check for blocking behavior (requests >1s are potentially blocking)
        if time_ms > 1000:
            domain_impact[domain]["blocking_time"] += time_ms

        # Track failures
        if req.get("status", 200) >= 400:
            domain_impact[domain]["failed_requests"] += 1

    # Calculate averages and sort by impact
    for domain, stats in domain_impact.items():
        stats["avg_time"] = round(stats["total_time"] / stats["requests"], 1)
        stats["total_size_kb"] = round(stats["total_size"] / 1024, 1)

    # Sort by total time impact
    sorted_domains = sorted(
        domain_impact.items(), key=lambda x: x[1]["total_time"], reverse=True
    )

    # Category breakdown
    category_impact = {}
    for domain, stats in domain_impact.items():
        category = stats["category"]
        if category not in category_impact:
            category_impact[category] = {
                "domains": 0,
                "requests": 0,
                "total_time": 0,
                "blocking_requests": 0,
            }

        category_impact[category]["domains"] += 1
        category_impact[category]["requests"] += stats["requests"]
        category_impact[category]["total_time"] += stats["total_time"]
        if stats["blocking_time"] > 0:
            category_impact[category]["blocking_requests"] += 1

    return {
        "domain_impact": dict(sorted_domains[:15]),  # Top 15 domains
        "category_breakdown": category_impact,
        "total_third_party_domains": len(domain_impact),
        "high_impact_domains": [domain for domain, stats in sorted_domains[:5]],
        "blocking_third_parties": [
            domain
            for domain, stats in domain_impact.items()
            if stats["blocking_time"] > 2000
        ],
    }


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Single HAR Performance Analysis")
    parser.add_argument("--har", dest="har_file", default=None, help="Path to HAR file")
    parser.add_argument(
        "--input",
        dest="input_dir",
        default=None,
        help="Input directory (har_chunks/<basename>)",
    )
    args = parser.parse_args()
    main(har_file=args.har_file, input_dir=args.input_dir)
