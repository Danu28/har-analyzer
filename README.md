# HAR Analysis Tools for AI Agents

This directory contains Python tools specifically designed for AI agents to analyze HAR (HTTP Archive) files efficiently.

## 🛠️ Available Tools

### 1. `quick_analyze.py` - Fast Analysis
**Best for**: Quick performance overview and agent consumption

```bash
python quick_analyze.py
```

**Features**:
- ✅ Auto-detects HAR files in current directory or `HAR-Files/` subdirectory
- ✅ Provides immediate performance grade (GOOD/FAIR/POOR/CRITICAL)
- ✅ Shows key metrics: load time, requests, size, failures
- ✅ Outputs structured JSON for easy parsing
- ✅ No file breakdown required (works directly with large HAR files)

**Output**: `quick_analysis_<filename>.json`

### 2. `break_har_file.py` - Detailed Breakdown
**Best for**: Comprehensive analysis and large file handling

```bash
python break_har_file.py
```

**Features**:
- ✅ Breaks large HAR files into manageable chunks
- ✅ Auto-detects HAR files in current directory
- ✅ Creates organized output in `har_chunks/` directory
- ✅ Generates resource type files, summaries, and guides
- ✅ Enables detailed analysis of massive HAR files

**Output**: `har_chunks/<filename>/` directory with 30+ analysis files

### 3. `analyze_performance.py` - Advanced Analysis
**Best for**: Deep performance analysis and recommendations

```bash
python analyze_performance.py
```

**Features**:
- ✅ Comprehensive performance metrics
- ✅ Critical path analysis
- ✅ Third-party service impact assessment
- ✅ Resource type performance breakdown
- ✅ Automated recommendations
- ✅ Agent-friendly JSON summary

**Output**: Console output + `agent_summary.json`

## 🤖 Agent Usage Patterns

### For Quick Assessment
```python
# Run quick analysis
result = subprocess.run(['python', 'quick_analyze.py'], capture_output=True, text=True)
# Parse the generated JSON file
with open('quick_analysis_<filename>.json') as f:
    data = json.load(f)
```

### For Detailed Analysis
```python
# 1. Break down the HAR file
subprocess.run(['python', 'break_har_file.py'])
# 2. Run detailed analysis
subprocess.run(['python', 'analyze_performance.py'])
# 3. Read agent summary
with open('har_chunks/<filename>/agent_summary.json') as f:
    detailed_data = json.load(f)
```

## 📊 Understanding the Output

### Performance Grades
- **GOOD**: Load time < 3 seconds
- **FAIR**: Load time 3-5 seconds  
- **POOR**: Load time 5-10 seconds
- **CRITICAL**: Load time > 10 seconds

### Key Metrics
- **Total Requests**: Number of network requests (target: < 100)
- **Page Load Time**: Time until `onLoad` event
- **DOM Ready Time**: Time until `DOMContentLoaded` event
- **Failed Requests**: HTTP status codes 400+
- **Slow Requests**: Individual requests taking > 1 second

## 🔧 Troubleshooting

### Common Issues
1. **No HAR files found**: Place `.har` files in current directory or `HAR-Files/` subdirectory
2. **Large file errors**: Use `break_har_file.py` first to handle files > 50MB
3. **Missing analysis data**: Run `break_har_file.py` before `analyze_performance.py`

### Directory Structure
```
HAR-analyze/
├── quick_analyze.py          # Quick analysis tool
├── break_har_file.py         # HAR file breakdown tool
├── analyze_performance.py    # Advanced analysis tool
├── HAR-Files/                # Place HAR files here
│   └── your_file.har
└── har_chunks/               # Generated analysis files
    └── your_file/
        ├── agent_summary.json
        ├── 01_header_and_metadata.json
        └── ...
```

## 📈 Sample Agent Summary JSON

```json
{
  "performance_summary": {
    "total_requests": 173,
    "dom_ready_time": "43.26s",
    "page_load_time": "56.36s",
    "performance_grade": "CRITICAL"
  },
  "critical_issues": {
    "very_slow_requests": 69,
    "slow_requests": 29,
    "failed_requests": 1,
    "excessive_requests": true
  },
  "largest_assets": [
    {
      "url": "https://example.com/large-bundle.js",
      "size_kb": 31609.4
    }
  ],
  "failed_requests": [
    {
      "url": "https://broken-resource.com/script.js",
      "status": 403
    }
  ]
}
```

## 🚀 Quick Start for Agents

1. **Place HAR file** in `HAR-Files/` directory
2. **Run quick analysis**: `python quick_analyze.py`
3. **Check performance grade** in the output
4. **For detailed analysis**: Run `python break_har_file.py` then `python analyze_performance.py`
5. **Parse JSON output** for structured data

The tools are designed to be robust, automatic, and provide consistent JSON output suitable for programmatic consumption by AI agents.
