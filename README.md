# HAR-Analyze

Simple Python tool for analyzing HTTP Archive (.har) files and generating performance reports.

## Quick Start

### Web Interface (Recommended)
```bash
git clone https://github.com/Danu28/har-analyzer.git
cd har-analyzer
pip install -r requirements.txt
python app.py
```
Open http://localhost:5000 in your browser.

### Command Line
```bash
# Single file analysis
python demo_single_file_report.py

# Compare two files  
python demo_har_comparison.py

# Multi-file analysis
python demo_multi_run_selector.py
```

## What It Does

- **Analyzes HAR files** from browser DevTools or performance testing tools
- **Generates HTML reports** with performance metrics and recommendations
- **Compares performance** between different test runs
- **Identifies bottlenecks** like slow requests, large assets, and third-party impacts

## Performance Grades

- **GOOD**: < 3 seconds load time
- **FAIR**: 3-5 seconds  
- **POOR**: 5-10 seconds
- **CRITICAL**: > 10 seconds

## Project Structure

```
HAR-analyze/
├── app.py                     # Web GUI
├── demo_*.py                  # Interactive demos
├── scripts/                   # Core analysis scripts
├── HAR-Files/                 # Input HAR files
├── reports/                   # Generated reports
└── templates/                 # HTML templates
```

## Usage

1. **Get HAR files**: Export from browser DevTools Network tab (Right-click → Save as HAR)
2. **Run analysis**: Use web GUI or command line demos
3. **View reports**: Interactive HTML reports open automatically

## Requirements

- Python 3.8+
- Flask (for web GUI)
- Standard library only for core functionality

## License

MIT License
