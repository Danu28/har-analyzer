# HAR-ANALYZE Project: AI Agent Onboarding Guide

## 1. 🎯 Project Overview

**HAR-ANALYZE** is a Python-based toolkit for analyzing HTTP Archive (`.har`) files. Its primary purpose is to process HAR files to extract key performance metrics, identify bottlenecks, and generate insightful, interactive HTML reports. The project supports single-file analysis, side-by-side comparisons, and multi-run trend analysis.

### Key Capabilities:
-   **Web GUI**: A user-friendly Flask-based web interface ([`app.py`](app.py)) for easy analysis.
-   **CLI Demos**: Interactive command-line scripts for single ([`demo_single_file_report.py`](demo_single_file_report.py)), comparison ([`demo_har_comparison.py`](demo_har_comparison.py)), and multi-run ([`demo_multi_run_selector.py`](demo_multi_run_selector.py)) analysis.
-   **Modular Scripts**: A collection of specialized scripts in the [`scripts/`](scripts/) directory for parsing, analysis, and report generation.
-   **Rich HTML Reports**: Generates professional, customizable HTML reports from data using templates found in [`templates/`](templates/).
-   **Agent-Friendly Output**: Produces structured `agent_summary.json` files, designed for programmatic consumption by AI agents.

## 2. 🏗️ Architecture & Components

The project is organized into distinct modules, each with a specific responsibility.

```
/
├── app.py                     # Flask Web GUI application
├── demo_*.py                  # Interactive CLI demo scripts
├── scripts/                   # Core analysis and utility scripts
│   ├── break_har_*.py         # Scripts to parse and chunk HAR files
│   ├── analyze_*.py           # Scripts for performance metric calculation
│   └── generate_*_report.py   # Scripts for creating HTML reports
├── HAR-Files/                 # Default directory for input .har files
├── har_chunks/                # Directory for intermediate processed data
├── reports/                   # Output directory for generated HTML reports
├── templates/                 # HTML templates for reports
└── static/                    # Static assets (CSS, JS) for the GUI and reports
```

### Key Workflows:
1.  **Capture**: Users obtain `.har` files from a browser's DevTools.
2.  **Parse**: A `break_har_*.py` script reads the HAR file and splits it into manageable JSON chunks in the `har_chunks/` directory.
3.  **Analyze**: An `analyze_*.py` script processes these chunks to calculate metrics and generates a summary file (e.g., `agent_summary.json`).
4.  **Report**: A `generate_*_report.py` script uses the analysis summary and an HTML template from [`templates/`](templates/) to create a final report in the `reports/` directory.

## 3. 🔧 Technical Standards

Adherence to these standards is crucial for maintaining code quality, performance, and security.

### Code Quality
-   **Type Hinting**: All function signatures must include type hints.
-   **Error Handling**: Use `try...except` blocks for operations that can fail (e.g., file I/O, JSON parsing) and provide clear error messages.
-   **Logging**: Prefer logging over `print()` for debugging and operational messages.
-   **Modularity**: Keep functions focused on a single task. Refactor large functions (>50 lines) and complex logic.

### Performance
-   **Memory Efficiency**: Process large HAR files in chunks. Avoid loading entire multi-megabyte files into memory at once. The `break_har_*.py` scripts are designed for this.
-   **Efficiency**: Use efficient data structures and algorithms. For example, use dictionaries for lookups and comprehensions for transformations.

### Security
-   **File Paths**: Sanitize all user-provided file paths to prevent directory traversal attacks. Use `pathlib.Path` for robust path manipulation.
-   **Input Validation**: Validate inputs from the command line and web forms. Check file extensions and implement size limits where appropriate.
-   **Dependencies**: Keep `requirements.txt` updated. Audit dependencies for known vulnerabilities.

## 4. 📊 Performance Analysis Domain

The core of the project is its ability to interpret web performance data.

### Key Metrics
-   **Page Load Time**: The primary indicator of user-perceived performance. Graded as GOOD (`<3s`), FAIR (`3-5s`), POOR (`5-10s`), or CRITICAL (`>10s`).
-   **DOM Content Loaded**: Time until the DOM is ready.
-   **Request Counts**: Total number of network requests.
-   **Resource Sizes**: Breakdown of page weight by resource type (JS, CSS, images, etc.).
-   **Third-Party Impact**: Analysis of performance costs from external services.
-   **Caching & Compression**: Checks for proper use of caching headers and text compression.

### Analysis Priorities
1.  **Identify Critical Issues**: Find failed requests, very slow resources, and render-blocking assets.
2.  **Provide Actionable Recommendations**: Suggest concrete steps for improvement (e.g., "Compress large images," "Leverage browser caching").
3.  **Highlight Strengths**: Point out what the page is doing well (e.g., "Excellent connection reuse," "No failed requests").

## 5. 🚀 Agent Responsibilities & Enhancements

As an AI agent, your role is to maintain and improve the project.

### Immediate Priorities
-   **Improve Error Handling**: Enhance exception handling to be more specific and provide clearer, user-friendly error messages across all scripts.
-   **Add Unit Tests**: Increase test coverage for core functions, especially in the `scripts/` directory, to ensure reliability and prevent regressions.
-   **Refactor for Clarity**: Improve code readability and maintainability by refactoring complex functions and improving inline documentation.
-   **Enhance Reports**: Add more data visualizations or metrics to the HTML templates in [`templates/`](templates/).

### Medium-Term Goals
-   **Core Web Vitals**: Integrate LCP, FID, and CLS metrics into the analysis.
-   **Configuration System**: Implement a YAML or JSON-based configuration file for settings like performance thresholds and report options.
-   **Batch Comparison**: Improve the multi-run analysis workflow to better visualize trends over time.

### Long-Term Vision
-   **Plugin Architecture**: Design a system to allow for extensible analysis modules.
-   **Real-Time Monitoring**: Explore capabilities for live performance monitoring.
-   **CI/CD Integration**: Create automated workflows for performance regression testing within a CI/CD pipeline.
# HAR-ANALYZE Project: AI Agent Onboarding Guide

## 1. 🎯 Project Overview

**HAR-ANALYZE** is a Python-based toolkit for analyzing HTTP Archive (`.har`) files. Its primary purpose is to process HAR files to extract key performance metrics, identify bottlenecks, and generate insightful, interactive HTML reports. The project supports single-file analysis, side-by-side comparisons, and multi-run trend analysis.

### Key Capabilities:
-   **Web GUI**: A user-friendly Flask-based web interface ([`app.py`](app.py)) for easy analysis.
-   **CLI Demos**: Interactive command-line scripts for single ([`demo_single_file_report.py`](demo_single_file_report.py)), comparison ([`demo_har_comparison.py`](demo_har_comparison.py)), and multi-run ([`demo_multi_run_selector.py`](demo_multi_run_selector.py)) analysis.
-   **Modular Scripts**: A collection of specialized scripts in the [`scripts/`](scripts/) directory for parsing, analysis, and report generation.
-   **Rich HTML Reports**: Generates professional, customizable HTML reports from data using templates found in [`templates/`](templates/).
-   **Agent-Friendly Output**: Produces structured `agent_summary.json` files, designed for programmatic consumption by AI agents.

## 2. 🏗️ Architecture & Components

The project is organized into distinct modules, each with a specific responsibility.

```
/
├── app.py                     # Flask Web GUI application
├── demo_*.py                  # Interactive CLI demo scripts
├── scripts/                   # Core analysis and utility scripts
│   ├── break_har_*.py         # Scripts to parse and chunk HAR files
│   ├── analyze_*.py           # Scripts for performance metric calculation
│   └── generate_*_report.py   # Scripts for creating HTML reports
├── HAR-Files/                 # Default directory for input .har files
├── har_chunks/                # Directory for intermediate processed data
├── reports/                   # Output directory for generated HTML reports
├── templates/                 # HTML templates for reports
└── static/                    # Static assets (CSS, JS) for the GUI and reports
```

### Key Workflows:
1.  **Capture**: Users obtain `.har` files from a browser's DevTools.
2.  **Parse**: A `break_har_*.py` script reads the HAR file and splits it into manageable JSON chunks in the `har_chunks/` directory.
3.  **Analyze**: An `analyze_*.py` script processes these chunks to calculate metrics and generates a summary file (e.g., `agent_summary.json`).
4.  **Report**: A `generate_*_report.py` script uses the analysis summary and an HTML template from [`templates/`](templates/) to create a final report in the `reports/` directory.

## 3. 🔧 Technical Standards

Adherence to these standards is crucial for maintaining code quality, performance, and security.

### Code Quality
-   **Type Hinting**: All function signatures must include type hints.
-   **Error Handling**: Use `try...except` blocks for operations that can fail (e.g., file I/O, JSON parsing) and provide clear error messages.
-   **Logging**: Prefer logging over `print()` for debugging and operational messages.
-   **Modularity**: Keep functions focused on a single task. Refactor large functions (>50 lines) and complex logic.

### Performance
-   **Memory Efficiency**: Process large HAR files in chunks. Avoid loading entire multi-megabyte files into memory at once. The `break_har_*.py` scripts are designed for this.
-   **Efficiency**: Use efficient data structures and algorithms. For example, use dictionaries for lookups and comprehensions for transformations.

### Security
-   **File Paths**: Sanitize all user-provided file paths to prevent directory traversal attacks. Use `pathlib.Path` for robust path manipulation.
-   **Input Validation**: Validate inputs from the command line and web forms. Check file extensions and implement size limits where appropriate.
-   **Dependencies**: Keep `requirements.txt` updated. Audit dependencies for known vulnerabilities.

## 4. 📊 Performance Analysis Domain

The core of the project is its ability to interpret web performance data.

### Key Metrics
-   **Page Load Time**: The primary indicator of user-perceived performance. Graded as GOOD (`<3s`), FAIR (`3-5s`), POOR (`5-10s`), or CRITICAL (`>10s`).
-   **DOM Content Loaded**: Time until the DOM is ready.
-   **Request Counts**: Total number of network requests.
-   **Resource Sizes**: Breakdown of page weight by resource type (JS, CSS, images, etc.).
-   **Third-Party Impact**: Analysis of performance costs from external services.
-   **Caching & Compression**: Checks for proper use of caching headers and text compression.

### Analysis Priorities
1.  **Identify Critical Issues**: Find failed requests, very slow resources, and render-blocking assets.
2.  **Provide Actionable Recommendations**: Suggest concrete steps for improvement (e.g., "Compress large images," "Leverage browser caching").
3.  **Highlight Strengths**: Point out what the page is doing well (e.g., "Excellent connection reuse," "No failed requests").

## 5. 🚀 Agent Responsibilities & Enhancements

As an AI agent, your role is to maintain and improve the project.

### Immediate Priorities
-   **Improve Error Handling**: Enhance exception handling to be more specific and provide clearer, user-friendly error messages across all scripts.
-   **Add Unit Tests**: Increase test coverage for core functions, especially in the `scripts/` directory, to ensure reliability and prevent regressions.
-   **Refactor for Clarity**: Improve code readability and maintainability by refactoring complex functions and improving inline documentation.
-   **Enhance Reports**: Add more data visualizations or metrics to the HTML templates in [`templates/`](templates/).

### Medium-Term Goals
-   **Core Web Vitals**: Integrate LCP, FID, and CLS metrics into the analysis.
-   **Configuration System**: Implement a YAML or JSON-based configuration file for settings like performance thresholds and report options.
-   **Batch Comparison**: Improve the multi-run analysis workflow to better visualize trends over time.

### Long-Term Vision
-   **Plugin Architecture**: Design a system to allow for extensible analysis modules.
-   **Real-Time Monitoring**: Explore capabilities for live performance monitoring.
-   **CI/CD Integration**: Create automated workflows for performance regression