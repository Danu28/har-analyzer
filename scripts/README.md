# HAR Capture Scripts

This directory contains scripts for capturing and analyzing HAR (HTTP Archive) files.

## Quick HAR Capture Script

### Basic Usage

```bash
# Quick capture with default settings (headless mode)
python quick_har_capture.py

# Capture a specific URL
python quick_har_capture.py --url "https://example.com"

# Capture with custom filename
python quick_har_capture.py --url "https://example.com" --output "my_test"

# Capture with proxy support
python quick_har_capture.py --url "https://example.com" --proxy "127.0.0.1:8080"

# Capture in visible mode (see the browser)
python quick_har_capture.py --url "https://example.com" --visible

# Full example with all options
python quick_har_capture.py --url "https://example.com" --proxy "http://proxy:8080" --output "test_with_proxy" --visible
```

### Features

- **Automatic Proxy Support**: Supports HTTP, HTTPS, SOCKS4, and SOCKS5 proxies
- **Smart Filename Generation**: Auto-generates timestamped filenames based on domain
- **HAR-Files Directory**: Automatically saves all captures to the `HAR-Files` directory
- **Headless/Visible Mode**: Choose between fast headless capture or visible browser
- **Chrome DevTools**: Uses Chrome's native performance logging for accurate HAR data
- **Error Handling**: Robust error handling with clear success/failure messages

### Output

- HAR files are saved to: `../HAR-Files/`
- Filenames follow the pattern: `domain_YYYYMMDD_HHMMSS.har`
- Compatible with the main analysis pipeline (`master_har_analyzer.py`)

### Proxy Formats Supported

```
127.0.0.1:8080
http://proxy.example.com:8080
https://secure-proxy.example.com:8080
socks4://socks-proxy:1080
socks5://socks-proxy:1080
```

## Other Scripts

- `selenium_script.py` - Full Selenium-based capture with BrowserMob Proxy fallback
- `analyze_performance.py` - Advanced performance analysis
- `generate_html_report.py` - HTML report generation
- `break_har_file.py` - HAR file chunking for analysis

## Usage Workflow

1. **Capture**: `python quick_har_capture.py --url "https://yoursite.com"`
2. **Analyze**: `python ../master_har_analyzer.py`
3. **Review**: Open the generated HTML report in your browser

The tools work together to provide a complete HAR capture and analysis workflow!

## HAR Comparison Scripts 🆕

The HAR comparison workflow consists of three modular scripts that work together to provide comprehensive performance comparison between two HAR files.

### 1. `break_har.py` - HAR Breakdown Engine

```bash
# Break down a HAR file into structured components
python break_har.py --har my_file.har --output breakdown_data/

# Get JSON output directly (for programmatic use)
python break_har.py --har my_file.har --json-output
```

**Purpose**: Converts raw HAR files into structured, analyzable data
**Output**: JSON files with requests, timings, resource types, and performance metrics

### 2. `analyze_two_chunks.py` - Comparison Analysis

```bash
# Compare two HAR breakdowns
python analyze_two_chunks.py --base base_breakdown.json --target target_breakdown.json --output comparison.json
```

**Purpose**: Analyzes differences between two HAR breakdowns
**Features**:
- Resource deltas (added/removed/modified URLs)
- KPI changes (load time, request count, sizes)
- Performance regression detection
- Third-party domain analysis

### 3. `generate_comparison_report.py` - HTML Report Generator

```bash
# Generate HTML comparison report
python generate_comparison_report.py comparison.json report.html

# Use custom template
python generate_comparison_report.py comparison.json report.html --template custom_template.html
```

**Purpose**: Creates professional HTML reports from comparison data
**Features**:
- Interactive charts and visualizations
- Professional responsive design
- Actionable performance insights
- Template-based customization

### Complete Workflow Example

```bash
# 1. Break down both HAR files
python break_har.py --har baseline.har --output baseline_data/
python break_har.py --har current.har --output current_data/

# 2. Compare the breakdowns
python analyze_two_chunks.py --base baseline_data/har_breakdown.json --target current_data/har_breakdown.json --output comparison_analysis.json

# 3. Generate HTML report
python generate_comparison_report.py comparison_analysis.json performance_comparison.html
```

**Tip**: Use `../demo_har_comparison.py` for automated end-to-end comparison workflow!
