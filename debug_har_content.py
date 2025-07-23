#!/usr/bin/env python3
"""
Debug script to examine HAR file structure and identify HTML content issues.
"""

import json
import os
from pathlib import Path
import base64


def debug_har_structure(har_file_path: str) -> None:
    """Debug utility to understand HAR file structure and HTML content."""
    try:
        print(f"🔍 Analyzing HAR file: {Path(har_file_path).name}")
        print("=" * 80)
        
        with open(har_file_path, 'r', encoding='utf-8') as f:
            har_data = json.load(f)
        
        entries = har_data.get('log', {}).get('entries', [])
        print(f"📊 Total entries: {len(entries)}")
        print()
        
        # Analyze first 10 entries for HTML content
        html_candidates = []
        all_entries_info = []
        
        for i, entry in enumerate(entries):
            request = entry.get('request', {})
            response = entry.get('response', {})
            content = response.get('content', {})
            
            url = request.get('url', '')
            method = request.get('method', '')
            status = response.get('status', 0)
            mime_type = content.get('mimeType', '')
            encoding = content.get('encoding', '')
            text = content.get('text', '')
            size = content.get('size', 0)
            
            entry_info = {
                'index': i,
                'url': url,
                'method': method,
                'status': status,
                'mime_type': mime_type,
                'encoding': encoding,
                'has_text': bool(text),
                'text_length': len(text) if text else 0,
                'content_size': size
            }
            all_entries_info.append(entry_info)
            
            # Check for HTML content
            is_html = (
                'text/html' in mime_type.lower() or
                'application/xhtml' in mime_type.lower() or
                url.endswith('.html') or
                url.endswith('.htm') or
                (url.endswith('/') and text and ('<html' in text.lower() or '<head' in text.lower()))
            )
            
            if is_html or (text and ('<html' in text.lower() or '<head' in text.lower())):
                html_candidates.append(entry_info)
        
        # Show HTML candidates
        print(f"🌐 HTML Document Candidates: {len(html_candidates)}")
        if html_candidates:
            for candidate in html_candidates:
                print(f"  [{candidate['index']}] {candidate['method']} {candidate['status']} - {candidate['url'][:100]}")
                print(f"      MIME: {candidate['mime_type']}")
                print(f"      Encoding: {candidate['encoding']}")
                print(f"      Has Content: {candidate['has_text']} ({candidate['text_length']} chars)")
                
                # Show snippet of content if available
                if candidate['has_text'] and candidate['index'] < len(entries):
                    entry = entries[candidate['index']]
                    text = entry.get('response', {}).get('content', {}).get('text', '')
                    encoding = entry.get('response', {}).get('content', {}).get('encoding', '')
                    
                    # Handle base64 encoded content
                    if encoding == 'base64' and text:
                        try:
                            decoded_text = base64.b64decode(text).decode('utf-8')
                            snippet = decoded_text[:200].replace('\n', ' ').replace('\r', ' ')
                            print(f"      Content: {snippet}...")
                        except Exception as e:
                            print(f"      Content: [Base64 decode error: {e}]")
                    elif text:
                        snippet = text[:200].replace('\n', ' ').replace('\r', ' ')
                        print(f"      Content: {snippet}...")
                    else:
                        print(f"      Content: [Empty]")
                print()
        else:
            print("❌ No HTML documents detected!")
            print("\n🔍 Checking first 10 entries for any patterns:")
            
            for entry_info in all_entries_info[:10]:
                print(f"  [{entry_info['index']}] {entry_info['method']} {entry_info['status']} - {entry_info['url'][:80]}...")
                print(f"      MIME: {entry_info['mime_type']}")
                print(f"      Has Content: {entry_info['has_text']} ({entry_info['text_length']} chars)")
                
                # Check if content might be HTML even without proper MIME type
                if entry_info['has_text'] and entry_info['index'] < len(entries):
                    entry = entries[entry_info['index']]
                    text = entry.get('response', {}).get('content', {}).get('text', '')
                    encoding = entry.get('response', {}).get('content', {}).get('encoding', '')
                    
                    if encoding == 'base64' and text:
                        try:
                            decoded_text = base64.b64decode(text).decode('utf-8')
                            if '<html' in decoded_text.lower() or '<head' in decoded_text.lower():
                                print(f"      ⚠️  Contains HTML tags but wrong MIME type!")
                                snippet = decoded_text[:200].replace('\n', ' ')
                                print(f"      Content: {snippet}...")
                        except:
                            pass
                    elif text and ('<html' in text.lower() or '<head' in text.lower()):
                        print(f"      ⚠️  Contains HTML tags but wrong MIME type!")
                        snippet = text[:200].replace('\n', ' ')
                        print(f"      Content: {snippet}...")
                print()
        
        # Summary recommendations
        print("📋 DIAGNOSIS & RECOMMENDATIONS:")
        print("-" * 50)
        
        if html_candidates:
            best_candidate = max(html_candidates, key=lambda x: x['text_length'])
            print(f"✅ Found {len(html_candidates)} HTML document(s)")
            print(f"📄 Best candidate: Entry [{best_candidate['index']}] with {best_candidate['text_length']} characters")
            print(f"🎯 URL: {best_candidate['url']}")
            
            if best_candidate['text_length'] == 0:
                print("⚠️  WARNING: HTML document has no content - this is why critical path analysis fails")
                print("💡 SOLUTION: Ensure HAR capture includes response bodies")
        else:
            print("❌ No HTML documents found in HAR file")
            print("💡 POSSIBLE SOLUTIONS:")
            print("   1. Ensure the HAR file was captured from the main page load")
            print("   2. Check that 'Preserve log' was enabled during capture")
            print("   3. Verify that response bodies were included in the HAR export")
            print("   4. Try capturing a fresh HAR file with DevTools")
        
        print()
        
    except Exception as e:
        print(f"❌ Error analyzing HAR file: {e}")


def main():
    """Main function to test HAR files in the project."""
    print("🧪 HAR Content Debugger")
    print("=" * 80)
    
    # Check for HAR files in the project
    har_dir = Path("HAR-Files")
    if har_dir.exists():
        har_files = list(har_dir.glob("*.har"))
        if har_files:
            print(f"Found {len(har_files)} HAR file(s) to analyze:")
            for har_file in har_files:
                print(f"  - {har_file.name}")
            print()
            
            # Analyze each HAR file
            for i, har_file in enumerate(har_files):
                if i > 0:
                    print("\n" + "="*80 + "\n")
                debug_har_structure(str(har_file))
        else:
            print("❌ No HAR files found in HAR-Files directory")
    else:
        print("❌ HAR-Files directory not found")
        print("💡 Create a HAR-Files directory and place .har files there for analysis")


if __name__ == "__main__":
    main()
