
"""
HAR File Breakdown for Single Analysis
======================================
Breaks a HAR file into manageable chunks for single file performance analysis.
Creates header, summary, chunks, resource type files, and index/guide.

Purpose: Single HAR file analysis workflow (not comparison)
Uses only standard libraries for maximum compatibility.
"""
import os
import sys
import json
from pathlib import Path
from datetime import datetime

def print_info(msg):
    print(f"[INFO] {msg}")
def print_ok(msg):
    print(f"[OK] {msg}")
def print_warn(msg):
    print(f"[WARNING] {msg}")
def print_error(msg):
    print(f"[ERROR] {msg}")

def auto_detect_har_file(root_dir):
    # First check current directory
    har_files = list(Path(root_dir).glob('*.har'))
    
    # If no HAR files in current dir, check HAR-Files subdirectory
    if not har_files:
        har_files_dir = Path(root_dir) / "HAR-Files"
        if har_files_dir.exists():
            har_files = list(har_files_dir.glob('*.har'))
            print_info(f"Checking HAR-Files subdirectory: {har_files_dir}")
    
    if not har_files:
        print_error(f"No HAR files found in {root_dir} or HAR-Files subdirectory")
        print_info(f"Current directory contents:")
        for f in Path(root_dir).iterdir():
            print(f"  - {f.name}")
        if Path(root_dir, "HAR-Files").exists():
            print_info(f"HAR-Files directory contents:")
            for f in Path(root_dir, "HAR-Files").iterdir():
                print(f"  - {f.name}")
        print_info("Please ensure a .har file exists in the current directory or HAR-Files subdirectory")
        print_info("Or specify the path manually: python break_har_file.py --har path/to/file.har")
        sys.exit(1)
    elif len(har_files) == 1:
        print_ok(f"Auto-detected HAR file: {har_files[0].name}")
        print_info(f"Full path: {har_files[0]}")
        return str(har_files[0])
    else:
        print_info("Multiple HAR files found:")
        for idx, f in enumerate(har_files, 1):
            print(f"  [{idx}] {f.name}")
        # For agent usage, automatically select the first one
        print_info("Auto-selecting first HAR file for agent usage...")
        selected_file = har_files[0]
        print_ok(f"Selected HAR file: {selected_file.name}")
        print_info(f"Full path: {selected_file}")
        return str(selected_file)

def main(har_file=None, output_dir=None):
    print_info("Breaking down HAR file for analysis...")
    root_dir = "."  # Work in current directory
    print_info(f"Current working directory: {os.path.abspath(root_dir)}")
    
    # Auto-detect HAR file if not specified
    if not har_file:
        har_file = auto_detect_har_file(root_dir)
    else:
        if not os.path.isfile(har_file):
            print_error(f"Specified HAR file not found: {har_file}")
            sys.exit(1)
        print_ok(f"Using specified HAR file: {os.path.basename(har_file)}")
        print_info(f"Full path: {os.path.abspath(har_file)}")
    
    har_base = Path(har_file).stem
    if not output_dir:
        output_dir = os.path.join("har_chunks", har_base)  # Create in current directory
    print_info(f"Output directory: {output_dir}")
    os.makedirs(output_dir, exist_ok=True)
    print_ok(f"Created output directory: {output_dir}")
    # Read HAR file
    with open(har_file, encoding="utf-8") as f:
        json_data = json.load(f)
    # 1. Header and Metadata
    header_data = {
        "log": {
            "version": json_data["log"]["version"],
            "creator": json_data["log"]["creator"],
            "pages": json_data["log"]["pages"]
        }
    }
    with open(os.path.join(output_dir, "01_header_and_metadata.json"), "w", encoding="utf-8") as f:
        json.dump(header_data, f, indent=2)
    print_ok("Created header and metadata file")
    # 2. Summary of all requests
    summary = []
    for i, entry in enumerate(json_data["log"]["entries"], 1):
        summary.append({
            "entryNumber": i,
            "method": entry["request"]["method"],
            "url": entry["request"]["url"],
            "status": entry["response"]["status"],
            "statusText": entry["response"].get("statusText", ""),
            "mimeType": entry["response"]["content"].get("mimeType", ""),
            "size": entry["response"]["content"].get("size", 0),
            "time": entry["time"],
            "startedDateTime": entry["startedDateTime"],
            "resourceType": entry.get("_resourceType", "unknown"),
            "timings": entry.get("timings", {})  # Include timings for DNS/SSL analysis
        })
    summary_data = {
        "totalEntries": len(summary),
        "requests": summary
    }
    with open(os.path.join(output_dir, "02_requests_summary.json"), "w", encoding="utf-8") as f:
        json.dump(summary_data, f, indent=2)
    print_ok(f"Created requests summary file ({len(summary)} entries)")
    # 3. Break entries into chunks of 10
    chunk_size = 10
    entries = json_data["log"]["entries"]
    chunk_number = 1
    for i in range(0, len(entries), chunk_size):
        chunk = entries[i:i+chunk_size]
        chunk_data = {
            "chunkNumber": chunk_number,
            "entryCount": len(chunk),
            "entries": chunk
        }
        fname = f"03_requests_chunk_{chunk_number:02d}.json"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            json.dump(chunk_data, f, indent=2)
        print_ok(f"Created chunk {chunk_number} ({len(chunk)} requests)")
        chunk_number += 1
    # 4. Resource type breakdown
    resource_types = {}
    for entry in entries:
        rtype = entry.get("_resourceType", "unknown")
        if rtype not in resource_types:
            resource_types[rtype] = []
        resource_types[rtype].append({
            "url": entry["request"]["url"],
            "method": entry["request"]["method"],
            "status": entry["response"]["status"],
            "size": entry["response"]["content"].get("size", 0),
            "time": entry["time"],
            "startedDateTime": entry["startedDateTime"]
        })
    for rtype, reqs in resource_types.items():
        resource_data = {
            "resourceType": rtype,
            "count": len(reqs),
            "requests": reqs
        }
        fname = f"04_resource_type_{rtype.lower()}.json"
        with open(os.path.join(output_dir, fname), "w", encoding="utf-8") as f:
            json.dump(resource_data, f, indent=2)
        print_ok(f"Created {rtype} requests file ({len(reqs)} requests)")
    # 5. Index file
    index_data = {
        "originalFile": os.path.basename(har_file),
        "originalSize": os.path.getsize(har_file),
        "totalEntries": len(entries),
        "chunksCreated": chunk_number-1,
        "resourceTypesFound": len(resource_types),
        "createdFiles": [
            "01_header_and_metadata.json - Contains HAR version, creator info, and page timing data",
            f"02_requests_summary.json - Overview of all {len(entries)} network requests",
            "03_requests_chunk_XX.json - Detailed request/response data in manageable chunks",
            "04_resource_type_*.json - Requests grouped by resource type (document, script, stylesheet, etc.)",
            "README.md - This explanation file"
        ],
        "instructions": [
            "Start with 01_header_and_metadata.json to understand the page load context",
            "Use 02_requests_summary.json to get an overview of all network activity",
            "Browse 03_requests_chunk_XX.json files for detailed request/response analysis",
            "Use 04_resource_type_*.json files to analyze specific types of resources"
        ]
    }
    with open(os.path.join(output_dir, "00_index_and_guide.json"), "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)
    # 6. README file
    readme_lines = [
        "# HAR File Breakdown\n",
        "This directory contains a breakdown of the large HAR (HTTP Archive) file into meaningful, manageable chunks.\n",
        f"## Original File\n- **File**: {os.path.basename(har_file)}\n- **Size**: {round(os.path.getsize(har_file)/1_048_576, 2)} MB\n- **Total Requests**: {len(entries)}\n",
        "## Generated Files\n",
        "### \U0001F4CB Overview Files\n- **00_index_and_guide.json** - This breakdown guide and file index\n- **01_header_and_metadata.json** - HAR version, creator info, and page timing data\n- **02_requests_summary.json** - Quick overview of all network requests\n",
        f"### \U0001F4E6 Request Chunks (Detailed Data)\n- **03_requests_chunk_01.json** through **03_requests_chunk_{chunk_number-1:02d}.json**\n  - Each chunk contains 10 requests (last chunk may have fewer)\n  - Includes complete request/response headers, timing, and content data\n",
        "### \U0001F3F7️ Resource Type Files\n" + "\n".join([f"- **04_resource_type_{rtype.lower()}.json** - {len(reqs)} {rtype} requests" for rtype, reqs in resource_types.items()]) + "\n",
        "## How to Use\n",
        "1. **Start Here**: Open `01_header_and_metadata.json` to understand the page context\n2. **Get Overview**: Check `02_requests_summary.json` for a quick summary of all network activity\n3. **Analyze Details**: Browse through `03_requests_chunk_XX.json` files for detailed analysis\n4. **By Resource Type**: Use `04_resource_type_*.json` files to focus on specific resource types\n",
        "## Analysis Tips\n",
        "- Look at the page timing data in the header to understand overall page load performance\n- Use the summary file to identify slow requests or failed requests\n- Resource type files help identify what types of assets are taking the most time\n- Chunk files contain complete request/response data for detailed debugging\n",
        f"Created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    ]
    with open(os.path.join(output_dir, "README.md"), "w", encoding="utf-8") as f:
        f.writelines(readme_lines)
    print()
    print_ok("SUCCESS: HAR file successfully broken down!")
    print_info(f"Output directory: {output_dir}")
    print_info(f"Files created: {chunk_number-1 + 4 + len(resource_types) + 2}")
    print()
    print_info("TIP: Start by reading the README.md file in the output directory")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Break HAR file into chunks for single analysis")
    parser.add_argument('--har', dest='har_file', default=None, help='Path to HAR file')
    parser.add_argument('--output', dest='output_dir', default=None, help='Output directory for chunks')
    args = parser.parse_args()
    main(har_file=args.har_file, output_dir=args.output_dir)
