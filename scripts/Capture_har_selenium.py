from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import json
import os
import time
import logging
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import threading

# Configure logging with thread safety
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s - %(threadName)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('har_capture.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Thread-safe lock for logging
log_lock = threading.Lock()

def safe_log(level, message):
    """Thread-safe logging function"""
    with log_lock:
        # Replace emoji characters for console compatibility
        console_message = message.replace('✅', '[SUCCESS]').replace('❌', '[FAILED]')
        if level == 'info':
            logger.info(console_message)
        elif level == 'error':
            logger.error(console_message)
        elif level == 'warning':
            logger.warning(console_message)

def capture_har_with_devtools(url, use_private_tab=False, output_filename=None, wait_time=5, browser_id=None):
    """
    Capture HAR data using Chrome DevTools Protocol instead of BrowserMob Proxy.
    This is more reliable and doesn't require external proxy setup.
    
    Args:
        url (str): Target URL to capture
        use_private_tab (bool): Whether to use incognito mode
        output_filename (str): Custom filename for HAR output
        wait_time (int): Time to wait for network requests to complete
        browser_id (int): Browser instance ID for parallel processing
    """
    thread_id = threading.current_thread().name
    try:
        # Configure Chrome options for HAR capture
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--enable-logging')
        chrome_options.add_argument('--log-level=0')
        chrome_options.add_argument('--disable-web-security')
        chrome_options.add_argument('--disable-features=VizDisplayCompositor')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        
        # Add incognito mode if requested
        if use_private_tab:
            chrome_options.add_argument('--incognito')
            safe_log('info', f"[{thread_id}] Using private/incognito mode")
        
        # Enable DevTools logging for network events
        chrome_options.set_capability('goog:loggingPrefs', {'performance': 'ALL'})
        
        # Initialize Chrome driver
        safe_log('info', f"[{thread_id}] Starting Chrome driver...")
        driver = webdriver.Chrome(options=chrome_options)
        
        # Enable performance logging
        driver.execute_cdp_cmd('Performance.enable', {})
        driver.execute_cdp_cmd('Network.enable', {})
        
        # Navigate to the target URL
        safe_log('info', f"[{thread_id}] Navigating to {url}")
        driver.get(url)
        
        # Wait for page to load
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # Give some time for all network requests to complete
        safe_log('info', f"[{thread_id}] Waiting {wait_time} seconds for network requests to complete...")
        time.sleep(wait_time)
        
        # Get network logs
        logs = driver.get_log('performance')
        
        # Process logs to create HAR-like structure
        har_data = process_logs_to_har(logs, url)
        
        # Generate output filename if not provided
        if not output_filename:
            # Create safe filename from URL
            safe_url = url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
            if len(safe_url) > 50:
                safe_url = safe_url[:50]
            
            private_suffix = '_private' if use_private_tab else ''
            
            if browser_id is not None:
                # For parallel processing, use browser_X format
                output_filename = f"{safe_url}_browser_{browser_id}{private_suffix}.har"
            else:
                # For single captures, use clean filename without timestamp
                output_filename = f"{safe_url}{private_suffix}.har"
        
        # Ensure HAR-Files directory exists
        har_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'HAR-Files')
        os.makedirs(har_dir, exist_ok=True)
        
        # Full path for output file
        output_path = os.path.join(har_dir, output_filename)
        
        # Save HAR data
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(har_data, f, indent=2)
        
        safe_log('info', f"[{thread_id}] HAR data saved to {output_path}")
        safe_log('info', f"[{thread_id}] Captured {len(har_data.get('log', {}).get('entries', []))} network requests")
        
        return output_path, len(har_data.get('log', {}).get('entries', []))
        
    except Exception as e:
        safe_log('error', f"[{thread_id}] Error during HAR capture: {str(e)}")
        raise
    finally:
        if 'driver' in locals():
            driver.quit()
            safe_log('info', f"[{thread_id}] Chrome driver closed")

def process_logs_to_har(logs, page_url):
    """
    Convert Chrome performance logs to HAR format.
    """
    entries = []
    requests = {}
    
    for log in logs:
        message = log.get('message', {})
        if isinstance(message, str):
            try:
                message = json.loads(message)
            except:
                continue
                
        method = message.get('message', {}).get('method', '')
        params = message.get('message', {}).get('params', {})
        
        if method == 'Network.requestWillBeSent':
            request_id = params.get('requestId')
            request = params.get('request', {})
            
            requests[request_id] = {
                'url': request.get('url', ''),
                'method': request.get('method', 'GET'),
                'headers': request.get('headers', {}),
                'startTime': params.get('timestamp', 0),
                'postData': request.get('postData', ''),
                'response': None
            }
            
        elif method == 'Network.responseReceived':
            request_id = params.get('requestId')
            response = params.get('response', {})
            
            if request_id in requests:
                requests[request_id]['response'] = {
                    'status': response.get('status', 0),
                    'statusText': response.get('statusText', ''),
                    'headers': response.get('headers', {}),
                    'mimeType': response.get('mimeType', ''),
                    'url': response.get('url', '')
                }
    
    # Convert to HAR entries format
    for request_id, request_data in requests.items():
        if request_data.get('response'):
            # Format timestamp properly
            timestamp = request_data['startTime']
            dt = time.gmtime(timestamp)
            formatted_time = time.strftime('%Y-%m-%dT%H:%M:%S', dt) + '.000Z'
            
            entry = {
                'startedDateTime': formatted_time,
                'time': 0,  # We don't have precise timing data
                'request': {
                    'method': request_data['method'],
                    'url': request_data['url'],
                    'httpVersion': 'HTTP/1.1',
                    'headers': [{'name': k, 'value': v} for k, v in request_data['headers'].items()],
                    'queryString': [],
                    'postData': {'text': request_data.get('postData', '')},
                    'headersSize': -1,
                    'bodySize': len(request_data.get('postData', ''))
                },
                'response': {
                    'status': request_data['response']['status'],
                    'statusText': request_data['response']['statusText'],
                    'httpVersion': 'HTTP/1.1',
                    'headers': [{'name': k, 'value': v} for k, v in request_data['response']['headers'].items()],
                    'content': {'size': 0, 'mimeType': request_data['response']['mimeType']},
                    'redirectURL': '',
                    'headersSize': -1,
                    'bodySize': 0
                },
                'cache': {},
                'timings': {
                    'send': 0,
                    'wait': 0,
                    'receive': 0
                }
            }
            entries.append(entry)
    
    # Create HAR structure
    har_data = {
        'log': {
            'version': '1.2',
            'creator': {
                'name': 'HAR Capture Script',
                'version': '1.0'
            },
            'pages': [{
                'startedDateTime': time.strftime('%Y-%m-%dT%H:%M:%S') + '.000Z',
                'id': 'page_1',
                'title': page_url,
                'pageTimings': {
                    'onContentLoad': -1,
                    'onLoad': -1
                }
            }],
            'entries': entries
        }
    }
    
    return har_data

def capture_multiple_urls_parallel(urls, use_private_tab=False, max_workers=3, wait_time=5):
    """
    Capture HAR data from multiple URLs in parallel.
    
    Args:
        urls (list): List of URLs to capture
        use_private_tab (bool): Whether to use incognito mode
        max_workers (int): Maximum number of parallel workers
        wait_time (int): Time to wait for network requests to complete
        
    Returns:
        dict: Results of all captures
    """
    results = {}
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all capture tasks with browser IDs
        future_to_url = {}
        browser_id = 1
        
        for url in urls:
            future = executor.submit(capture_har_with_devtools, url, use_private_tab, None, wait_time, browser_id)
            future_to_url[future] = (url, browser_id)
            browser_id += 1
        
        # Collect results as they complete
        for future in as_completed(future_to_url):
            url, browser_id = future_to_url[future]
            try:
                output_path, request_count = future.result()
                results[url] = {
                    'status': 'success',
                    'output_file': output_path,
                    'request_count': request_count,
                    'browser_id': browser_id
                }
                safe_log('info', f"✅ Completed capture for {url} (Browser {browser_id})")
            except Exception as e:
                results[url] = {
                    'status': 'failed',
                    'error': str(e),
                    'browser_id': browser_id
                }
                safe_log('error', f"❌ Failed to capture {url} (Browser {browser_id}): {str(e)}")
    
    return results

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='HAR Capture Tool with Advanced Features')
    
    parser.add_argument('--url', '-u', type=str, 
                       help='Single URL to capture (default: instantink-pie1.hpconnectedpie.com)',
                       default='https://instantink-pie1.hpconnectedpie.com/')
    
    parser.add_argument('--urls', '-U', type=str, nargs='+',
                       help='Multiple URLs to capture in parallel')
    
    parser.add_argument('--private', '-p', action='store_true',
                       help='Use private/incognito mode')
    
    parser.add_argument('--parallel', '-P', action='store_true',
                       help='Enable parallel processing for multiple URLs')
    
    parser.add_argument('--workers', '-w', type=int, default=3,
                       help='Number of parallel workers (default: 3)')
    
    parser.add_argument('--wait', '-W', type=int, default=5,
                       help='Wait time for network requests to complete (default: 5 seconds)')
    
    parser.add_argument('--output', '-o', type=str,
                       help='Custom output filename (only for single URL)')
    
    parser.add_argument('--repeat', '-r', type=int, default=1,
                       help='Number of times to repeat the capture (useful for load testing)')
    
    return parser.parse_args()

def display_results_summary(results):
    """Display a summary of capture results"""
    print("\n" + "="*80)
    print("🎯 HAR CAPTURE RESULTS SUMMARY")
    print("="*80)
    
    successful = [url for url, result in results.items() if result['status'] == 'success']
    failed = [url for url, result in results.items() if result['status'] == 'failed']
    
    print(f"✅ Successful captures: {len(successful)}")
    print(f"❌ Failed captures: {len(failed)}")
    print(f"📊 Total captures processed: {len(results)}")
    
    if successful:
        print("\n📁 Generated HAR Files:")
        for url in successful:
            result = results[url]
            filename = os.path.basename(result['output_file'])
            print(f"   • {filename} - {result['request_count']} requests")
    
    if failed:
        print("\n❌ Failed Captures:")
        for url in failed:
            print(f"   • {url}: {results[url]['error']}")
    
    # Show total requests captured
    total_requests = sum(result.get('request_count', 0) for result in results.values() if result['status'] == 'success')
    print(f"\n🌐 Total network requests captured: {total_requests}")
    
    # Show unique vs repeated URLs
    unique_urls = set()
    for url_key in results.keys():
        if '_run' in url_key:
            base_url = url_key.split('_run')[0]
            unique_urls.add(base_url)
        else:
            unique_urls.add(url_key)
    
    if len(unique_urls) < len(results):
        print(f"🔄 Unique URLs tested: {len(unique_urls)}")
        print(f"📈 Total test runs: {len(results)}")
    
    print("="*80)

if __name__ == "__main__":
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        print("🚀 HAR Capture Tool - Enhanced Version")
        print("="*50)
        
        results = {}
        
        # Determine URLs to process
        if args.urls:
            # Multiple URLs provided
            urls_to_process = args.urls
            if args.parallel:
                print(f"🔄 Starting parallel capture of {len(urls_to_process)} URLs...")
                print(f"👥 Using {args.workers} parallel workers")
                print(f"🕐 Wait time per URL: {args.wait} seconds")
                if args.private:
                    print("🕵️ Using private/incognito mode")
                print("-"*50)
                
                results = capture_multiple_urls_parallel(
                    urls_to_process, 
                    args.private, 
                    args.workers, 
                    args.wait
                )
            else:
                print(f"📝 Processing {len(urls_to_process)} URLs sequentially...")
                if args.private:
                    print("🕵️ Using private/incognito mode")
                print("-"*50)
                
                for url in urls_to_process:
                    try:
                        output_path, request_count = capture_har_with_devtools(
                            url, args.private, None, args.wait
                        )
                        results[url] = {
                            'status': 'success',
                            'output_file': output_path,
                            'request_count': request_count
                        }
                    except Exception as e:
                        results[url] = {
                            'status': 'failed',
                            'error': str(e)
                        }
        else:
            # Single URL
            single_url = args.url
            repeat_count = args.repeat
            
            if repeat_count > 1 and args.parallel:
                # Multiple captures of same URL in parallel
                print(f"🎯 Capturing URL {repeat_count} times in parallel: {single_url}")
                print(f"👥 Using {args.workers} parallel workers")
                if args.private:
                    print("🕵️ Using private/incognito mode")
                print(f"🕐 Wait time: {args.wait} seconds")
                print("-"*50)
                
                # Create list of same URL repeated
                urls_to_process = [single_url] * repeat_count
                results = capture_multiple_urls_parallel(
                    urls_to_process, 
                    args.private, 
                    args.workers, 
                    args.wait
                )
                
                # Rename keys to show run numbers
                renamed_results = {}
                run_counter = 1
                for url, result in results.items():
                    renamed_results[f"{single_url}_run{run_counter:02d}"] = result
                    run_counter += 1
                results = renamed_results
                
            else:
                # Single URL capture (possibly repeated sequentially)
                if repeat_count > 1:
                    print(f"🎯 Capturing URL {repeat_count} times sequentially: {single_url}")
                else:
                    print(f"🎯 Capturing single URL: {single_url}")
                if args.private:
                    print("🕵️ Using private/incognito mode")
                print(f"🕐 Wait time: {args.wait} seconds")
                print("-"*50)
                
                for i in range(repeat_count):
                    try:
                        # Add iteration number to filename if repeating
                        custom_filename = None
                        if repeat_count > 1:
                            safe_url = single_url.replace('https://', '').replace('http://', '').replace('/', '_').replace(':', '_')
                            if len(safe_url) > 50:
                                safe_url = safe_url[:50]
                            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                            private_suffix = '_private' if args.private else ''
                            custom_filename = f"{safe_url}_{timestamp}_run{i+1:02d}{private_suffix}.har"
                        elif args.output:
                            custom_filename = args.output
                        
                        output_path, request_count = capture_har_with_devtools(
                            single_url, args.private, custom_filename, args.wait
                        )
                        
                        # Use URL with run number as key for repeated captures
                        result_key = f"{single_url}_run{i+1:02d}" if repeat_count > 1 else single_url
                        results[result_key] = {
                            'status': 'success',
                            'output_file': output_path,
                            'request_count': request_count
                        }
                        
                        if repeat_count > 1:
                            print(f"✅ Completed run {i+1}/{repeat_count}")
                            
                    except Exception as e:
                        result_key = f"{single_url}_run{i+1:02d}" if repeat_count > 1 else single_url
                        results[result_key] = {
                            'status': 'failed',
                            'error': str(e)
                        }
        
        # Display results summary
        display_results_summary(results)
        
        # Check if any captures failed
        failed_count = len([r for r in results.values() if r['status'] == 'failed'])
        if failed_count > 0:
            exit(1)
        else:
            print("\n🎉 All captures completed successfully!")
        
    except KeyboardInterrupt:
        print("\n⚠️ Capture interrupted by user")
        exit(1)
    except Exception as e:
        safe_log('error', f"❌ HAR capture failed: {str(e)}")
        print(f"❌ Error: {str(e)}")
        exit(1)
