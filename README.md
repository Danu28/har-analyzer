# HAR-ANALYZE: Professional Web Performance Analysis Toolkit

A comprehensive Python toolkit for analyzing HTTP Archive (.har) files with professional reporting capabilities. Designed for performance engineers, developers, and automated analysis workflows.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![CI Pipeline](https://github.com/Danu28/har-analyzer/workflows/CI%20Pipeline/badge.svg)](https://github.com/Danu28/har-analyzer/actions)

## 🚀 Quick Start

```bash
# Clone the repository
git clone https://github.com/Danu28/har-analyzer.git
cd har-analyzer

# Install dependencies (optional - uses standard library by default)
pip install -r requirements.txt

# Run interactive demos
python demo_single_file_report.py     # Single HAR analysis
python demo_har_comparison.py         # Compare two HAR files  
python demo_multi_run_selector.py     # Multi-HAR analysis
```

## 🎯 Analysis Workflows

### 1. Single HAR File Analysis
**Purpose**: Deep performance analysis of individual HAR files

```bash
python demo_single_file_report.py
```

**Workflow**:
1. **Break**: `scripts/break_har_for_single_analysis.py` - Parse HAR into manageable chunks
2. **Analyze**: `scripts/analyze_single_har_performance.py` - Extract performance metrics
3. **Report**: `scripts/generate_single_har_report.py` - Generate premium HTML report

**Output**: Interactive HTML report with performance grades, recommendations, and detailed metrics

### 2. HAR File Comparison
**Purpose**: Performance regression detection and A/B testing

```bash
python demo_har_comparison.py
```

**Workflow**:
1. **Break**: `scripts/break_har_for_comparison.py` - Prepare both files for comparison
2. **Compare**: `scripts/compare_har_analysis.py` - Identify performance differences
3. **Report**: `scripts/generate_har_comparison_report.py` - Generate side-by-side comparison

**Output**: Professional comparison report highlighting performance changes and regressions

### 3. Multi-HAR Analysis
**Purpose**: Trend analysis across multiple test runs

```bash
python demo_multi_run_selector.py
```

**Workflow**:
1. **Analyze**: `scripts/analyze_multi_har_runs.py` - Process multiple HAR files
2. **Compare**: `scripts/compare_multi_har_performance.py` - Identify trends and outliers
3. **Report**: `scripts/generate_multi_har_report.py` - Generate executive summary

**Output**: Executive dashboard with performance trends and statistical analysis

## 📊 Performance Metrics & Grading

### Performance Grades
- **GOOD**: Load time < 3 seconds, optimal resource usage
- **FAIR**: Load time 3-5 seconds, moderate optimization needed  
- **POOR**: Load time 5-10 seconds, significant issues identified
- **CRITICAL**: Load time > 10 seconds, major performance problems

### Key Metrics Analyzed
- **Page Load Time**: Time until `onLoad` event completion
- **DOM Ready Time**: Time until `DOMContentLoaded` event
- **Request Analysis**: Total count, failed requests, slow requests (>1s)
- **Resource Breakdown**: Size analysis by type (JS, CSS, Images, etc.)
- **Third-Party Impact**: External service performance assessment
- **Critical Path**: Render-blocking resource identification

## 🏗️ Project Structure

```
HAR-analyze/
├── demo_single_file_report.py      # Interactive single file demo
├── demo_har_comparison.py          # Interactive comparison demo
├── demo_multi_run_selector.py      # Interactive multi-run demo
├── scripts/                        # Core analysis scripts
│   ├── break_har_for_single_analysis.py
│   ├── analyze_single_har_performance.py
│   ├── generate_single_har_report.py
│   ├── break_har_for_comparison.py
│   ├── compare_har_analysis.py
│   ├── generate_har_comparison_report.py
│   ├── analyze_multi_har_runs.py
│   ├── compare_multi_har_performance.py
│   └── generate_multi_har_report.py
├── templates/                      # Professional HTML templates
│   ├── har_single_premium.html
│   ├── har_comparison_side_by_side.html
│   └── har_multi_run_executive.html
├── HAR-Files/                      # Input HAR files directory
├── har_chunks/                     # Processed analysis data
└── reports/                        # Generated HTML reports
```

## 🤖 Programmatic Usage

### For AI Agents & Automation

```python
import subprocess
import json
from pathlib import Path

# Single file analysis
def analyze_single_har(har_file_path):
    """Analyze a single HAR file and return structured data"""
    # Copy HAR file to HAR-Files directory
    har_files_dir = Path("HAR-Files")
    har_files_dir.mkdir(exist_ok=True)
    
    # Run analysis workflow
    subprocess.run([
        "python", "demo_single_file_report.py", 
        "--har", str(har_file_path), 
        "--auto"
    ], check=True)
    
    # Read generated analysis
    analysis_file = har_files_dir / f"{Path(har_file_path).stem}_analysis.json"
    with open(analysis_file) as f:
        return json.load(f)

# Compare two HAR files
def compare_har_files(baseline_path, target_path):
    """Compare two HAR files for performance regression detection"""
    result = subprocess.run([
        "python", "demo_har_comparison.py",
        "--baseline", str(baseline_path),
        "--target", str(target_path),
        "--auto"
    ], capture_output=True, text=True)
    
    # Read comparison results
    with open("comparison_analysis.json") as f:
        return json.load(f)

# Multi-run analysis
def analyze_multiple_runs(har_file_list):
    """Analyze multiple HAR files for trend analysis"""
    # Run multi-run analysis
    subprocess.run([
        "python", "demo_multi_run_selector.py",
        "--files"] + har_file_list + ["--auto"]
    , check=True)
    
    # Read executive summary
    with open("executive_summary.json") as f:
        return json.load(f)
```

## � Sample Analysis Output

### Agent Summary JSON Structure
```json
{
  "analysis_metadata": {
    "har_file": "example.har",
    "analysis_timestamp": "2025-07-17T10:30:00Z",
    "performance_grade": "FAIR"
  },
  "performance_summary": {
    "page_load_time": 4.23,
    "dom_ready_time": 2.15,
    "total_requests": 156,
    "total_size_kb": 2847.3,
    "failed_requests": 2
  },
  "critical_issues": {
    "slow_requests": 12,
    "very_slow_requests": 3,
    "large_assets": 5,
    "third_party_slowdowns": 8
  },
  "performance_breakdown": {
    "html": {"requests": 3, "size_kb": 45.2, "avg_time_ms": 245},
    "javascript": {"requests": 28, "size_kb": 1234.5, "avg_time_ms": 892},
    "css": {"requests": 8, "size_kb": 234.1, "avg_time_ms": 156},
    "images": {"requests": 67, "size_kb": 987.4, "avg_time_ms": 345}
  },
  "recommendations": [
    "Optimize JavaScript bundle size (>1MB detected)",
    "Enable compression for CSS files",
    "Consider image optimization for faster loading"
  ]
}
```

## 🎨 Report Templates

### Premium Single File Report
- **Interactive charts** with performance metrics
- **Resource waterfall** visualization  
- **Performance grade** with color-coded indicators
- **Optimization recommendations** with priority levels
- **Third-party analysis** with domain breakdown

### Side-by-Side Comparison Report
- **Before/after performance comparison**
- **Resource delta analysis** (added, removed, modified)
- **Performance regression highlighting**
- **Statistical change analysis**
- **Executive summary** with key findings

### Multi-Run Executive Dashboard
- **Trend analysis** across multiple test runs
- **Statistical variance** and outlier detection
- **Performance consistency** metrics
- **Executive KPI dashboard**
- **Actionable insights** for stakeholders

## 🛠️ Advanced Features

### Cross-Platform Compatibility
- **Windows**: PowerShell and Command Prompt support
- **macOS/Linux**: Bash shell compatibility
- **Python 3.8+**: Modern Python version support
- **Optional Dependencies**: Jinja2 for enhanced templates

### Performance Optimization
- **Streaming Processing**: Handles large HAR files (>100MB)
- **Memory Efficient**: Chunked analysis to minimize RAM usage
- **Fast Analysis**: Optimized algorithms for quick insights
- **Parallel Processing**: Multi-threaded where applicable

### Integration Ready
- **CI/CD Pipelines**: JSON output for automated workflows
- **GitHub Actions**: Pre-built workflows included
- **Docker Support**: Containerization ready
- **API Friendly**: Structured data output

## 🚀 Getting Started

### Prerequisites
- **Python 3.8+** installed on your system
- **HAR files** from browser DevTools, WebPageTest, or other sources

### Installation
1. **Clone the repository**:
   ```bash
   git clone https://github.com/Danu28/har-analyzer.git
   cd har-analyzer
   ```

2. **Install dependencies** (optional):
   ```bash
   pip install -r requirements.txt
   ```
   *Note: The toolkit works with Python standard library only. Jinja2 is optional for enhanced HTML templates.*

3. **Add HAR files**:
   - Place your `.har` files in the `HAR-Files/` directory
   - Or use the interactive demos to select files

### Quick Start Examples

#### Single File Analysis
```bash
# Interactive demo with file selection
python demo_single_file_report.py

# The demo will:
# 1. List available HAR files
# 2. Let you select one for analysis  
# 3. Generate a premium HTML report
# 4. Open the report in your browser
```

#### Performance Comparison
```bash
# Interactive comparison demo
python demo_har_comparison.py

# The demo will:
# 1. Let you select baseline HAR file
# 2. Let you select target HAR file for comparison
# 3. Generate side-by-side comparison report
# 4. Highlight performance differences
```

#### Multi-Run Analysis
```bash
# Interactive multi-run demo
python demo_multi_run_selector.py

# The demo will:
# 1. Show available HAR files
# 2. Let you select multiple files
# 3. Generate executive summary report
# 4. Show performance trends and statistics
```

## 🔧 Configuration & Customization

### Environment Variables
```bash
# Optional: Set custom output directories
export HAR_CHUNKS_DIR="./custom_chunks"
export HAR_REPORTS_DIR="./custom_reports"

# Optional: Enable enhanced features
export USE_JINJA2_TEMPLATES="true"
```

### Template Customization
Modify HTML templates in the `templates/` directory:
- `har_single_premium.html` - Single file reports
- `har_comparison_side_by_side.html` - Comparison reports  
- `har_multi_run_executive.html` - Multi-run reports

## 🔍 Troubleshooting

### Common Issues

**Q: "No HAR files found" error**
```bash
# Ensure HAR files are in the correct location:
ls HAR-Files/*.har

# Or place HAR files in the current directory:
ls *.har
```

**Q: Large HAR files causing memory issues**
```bash
# The toolkit automatically handles large files through chunking
# For files >100MB, processing may take longer but should complete
# Monitor system memory during processing
```

**Q: Reports not generating properly**
```bash
# Check if all required directories exist:
mkdir -p HAR-Files har_chunks reports

# Verify Python version:
python --version  # Should be 3.8+

# Check for any error messages in the console output
```

**Q: Browser not opening reports automatically**
```bash
# Manual report opening:
# Windows:
start reports/your_report.html

# macOS:
open reports/your_report.html

# Linux:
xdg-open reports/your_report.html
```

## 📚 Documentation

- **[CHANGELOG.md](CHANGELOG.md)** - Version history and feature updates
- **[LICENSE](LICENSE)** - MIT License details
- **[scripts/README.md](scripts/README.md)** - Detailed script documentation
- **[GitHub Actions](.github/workflows/)** - CI/CD pipeline documentation

## 🤝 Contributing

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/new-analysis`
3. **Make your changes** and add tests
4. **Run quality checks**: The CI pipeline will validate your changes
5. **Submit a pull request** with a clear description

### Development Setup
```bash
# Install development dependencies
pip install -r requirements.txt
pip install pytest black flake8 isort

# Run code formatting
black .
isort .

# Run linting
flake8 .

# Run tests (when available)
pytest
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🏆 Acknowledgments

- **HAR Format**: Based on the [HTTP Archive format specification](http://www.softwareishard.com/blog/har-12-spec/)
- **Performance Metrics**: Inspired by [Core Web Vitals](https://web.dev/vitals/) and industry best practices
- **Community**: Built for the web performance analysis community

---

**Made with ❤️ for performance engineers, developers, and anyone who cares about web performance.**

For questions, issues, or feature requests, please visit our [GitHub repository](https://github.com/Danu28/har-analyzer).
