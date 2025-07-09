#!/usr/bin/env python3
"""
Quick HAR Capture Script - Simplified version for testing
Uses Chrome DevTools to capture network traffic and save as HAR
Supports proxy configuration and saves to HAR-Files directory
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import json, os, time
from urllib.parse import urlparse

def quick_har_capture(url="https://instantink-pie1.hpconnectedpie.com/us/en/l/v2", 
                      proxy=None, 
                      output_file=None, 
                      headless=True):
    """
    Quick HAR capture using Chrome DevTools
    
    Args:
        url (str): URL to capture
        proxy (str): Proxy server (e.g., "127.0.0.1:8080" or "http://proxy:8080")
        output_file (str): Output filename (auto-generated if None)
        headless (bool): Run Chrome in headless mode
    """
    print(f"🚀 Quick HAR capture from: {url}")
    
    # Generate output filename if not provided
    if not output_file:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.replace(':', '_').replace('.', '_')
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        output_file = f"{domain}_{timestamp}.har"
    
    # Ensure .har extension
    if not output_file.endswith('.har'):
        output_file += '.har'
    
    # Create HAR-Files directory if it doesn't exist
    har_files_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "HAR-Files")
    os.makedirs(har_files_dir, exist_ok=True)
    
    # Full path for output file
    output_path = os.path.join(har_files_dir, output_file)
    
    try:
        chrome_options = Options()
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--ignore-certificate-errors")
        
        # Add proxy configuration if provided
        if proxy:
            # Handle different proxy formats
            if not proxy.startswith(('http://', 'https://', 'socks4://', 'socks5://')):
                proxy = f"http://{proxy}"
            chrome_options.add_argument(f"--proxy-server={proxy}")
            print(f"🔗 Using proxy: {proxy}")
        
        if headless:
            chrome_options.add_argument("--headless")  # Run headless for speed
        
        # Enable performance logging
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        print("🌐 Starting Chrome...")
        driver = webdriver.Chrome(options=chrome_options)
        
        print(f"📱 Navigating to {url}...")
        driver.get(url)
        time.sleep(3)  # Wait for page load and dynamic content
        
        print("📊 Collecting logs...")
        logs = driver.get_log('performance')
        
        # Create proper HAR format
        current_time = time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime())
        parsed_url = urlparse(url)
        page_title = parsed_url.netloc
        
        har_data = {
            "log": {
                "version": "1.2",
                "creator": {
                    "name": "Quick HAR Capture",
                    "version": "2.0"
                },
                "pages": [
                    {
                        "startedDateTime": current_time,
                        "id": "page_1",
                        "title": page_title,
                        "pageTimings": {
                            "onContentLoad": 1000,
                            "onLoad": 2000
                        }
                    }
                ],
                "entries": []
            }
        }
        
        # Process logs into HAR entries
        entry_count = 0
        for log in logs:
            try:
                message = json.loads(log['message'])
                if message['message']['method'] == 'Network.responseReceived':
                    response = message['message']['params']['response']
                    url_entry = response.get('url', '')
                    
                    if url_entry and not url_entry.startswith('data:'):
                        har_entry = {
                            "pageref": "page_1",
                            "startedDateTime": current_time,
                            "time": 100,
                            "request": {
                                "method": "GET",
                                "url": url_entry,
                                "httpVersion": "HTTP/1.1",
                                "headers": [{"name": k, "value": str(v)} for k, v in response.get('requestHeaders', {}).items()],
                                "queryString": [],
                                "cookies": [],
                                "headersSize": -1,
                                "bodySize": 0
                            },
                            "response": {
                                "status": response.get('status', 200),
                                "statusText": response.get('statusText', 'OK'),
                                "httpVersion": "HTTP/1.1",
                                "headers": [{"name": k, "value": str(v)} for k, v in response.get('headers', {}).items()],
                                "cookies": [],
                                "content": {
                                    "size": response.get('encodedDataLength', 0),
                                    "mimeType": response.get('mimeType', 'text/html')
                                },
                                "redirectURL": "",
                                "headersSize": -1,
                                "bodySize": response.get('encodedDataLength', 0)
                            },
                            "cache": {},
                            "timings": {
                                "blocked": 1,
                                "dns": 10,
                                "connect": 20,
                                "send": 5,
                                "wait": 50,
                                "receive": 14,
                                "ssl": 15
                            }
                        }
                        har_data['log']['entries'].append(har_entry)
                        entry_count += 1
            except:
                continue
        
        driver.quit()
        
        # Save HAR file to HAR-Files directory
        print(f"💾 Saving {entry_count} entries to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(har_data, f, indent=2)
        
        file_size = os.path.getsize(output_path) / 1024
        print(f"✅ HAR saved: {output_file} ({file_size:.1f} KB)")
        print(f"📁 Full path: {output_path}")
        return output_path
        
    except Exception as e:
        print(f"❌ Error: {e}")
        if 'driver' in locals():
            try:
                driver.quit()
            except:
                pass
        return None

def main():
    """Main function with command line interface"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Quick HAR capture using Chrome DevTools")
    parser.add_argument("--url", "-u", 
                       default="https://instantink-pie1.hpconnectedpie.com/us/en/l/v2",
                       help="URL to capture (default: HP Instant Ink)")
    parser.add_argument("--proxy", "-p", 
                       help="Proxy server (e.g., 127.0.0.1:8080 or http://proxy:8080)")
    parser.add_argument("--output", "-o", 
                       help="Output filename (auto-generated if not specified)")
    parser.add_argument("--visible", "-v", action="store_true",
                       help="Run Chrome in visible mode (not headless)")
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("🚀 Quick HAR Capture Tool")
    print("=" * 60)
    print(f"🌐 URL: {args.url}")
    if args.proxy:
        print(f"🔗 Proxy: {args.proxy}")
    print(f"👁️ Mode: {'Visible' if args.visible else 'Headless'}")
    print("=" * 60)
    
    result = quick_har_capture(
        url=args.url,
        proxy=args.proxy,
        output_file=args.output,
        headless=not args.visible
    )
    
    if result:
        print("\n🎉 Quick HAR capture completed!")
        print("💡 Analyze with:")
        print(f"   python master_har_analyzer.py")
        return True
    else:
        print("❌ HAR capture failed!")
        return False

if __name__ == "__main__":
    main()
