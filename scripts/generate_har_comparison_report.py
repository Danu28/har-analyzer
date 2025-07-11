#!/usr/bin/env python3
"""
HAR Comparison Report Generator
==============================
This script generates comprehensive HTML comparison reports from HAR comparison analysis data.
Creates professional, interactive reports with charts and detailed performance insights
for comparing two HAR file analyses.

Features:
- HTML report generation from comparison analysis data
- Interactive charts and visualizations
- Professional styling and responsive design
- Actionable performance insights and recommendations
- Detailed resource analysis tables
- Side-by-side comparison views
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime
import webbrowser

def generate_comparison_report(comparison_data: Dict[str, Any], 
                             output_file: Optional[str] = None,
                             template_file: Optional[str] = None,
                             template_style: str = "side-by-side",
                             open_browser: bool = True) -> str:
    """
    Generate HTML comparison report from comparison analysis data
    
    Args:
        comparison_data: Comparison analysis dictionary from analyze_two_chunks.py
        output_file: Output HTML file path (default: har_comparison_report.html)
        template_file: Custom template file path (default: uses built-in template)
        template_style: Template style - "side-by-side" or "detailed" (default: side-by-side)
        open_browser: Whether to open report in browser
        
    Returns:
        Path to generated HTML report
    """
    print("[INFO] Generating HAR comparison report...")
    
    # Set default output file
    if not output_file:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"har_comparison_report_{timestamp}.html"
    
    # Ensure .html extension
    if not output_file.endswith('.html'):
        output_file += '.html'
    
    # Try to use external template first, then fall back to built-in
    if template_file and os.path.exists(template_file):
        print(f"[TEMPLATE] Using custom template: {template_file}")
        template_content = _load_template_file(template_file)
    else:
        # Check for style-specific template in templates directory
        template_filename = f"har_comparison_{template_style.replace('-', '_')}.html" if template_style != "detailed" else "har_comparison_expected.html"
        default_template = Path(__file__).parent.parent / "templates" / template_filename
        
        if default_template.exists():
            print(f"[TEMPLATE] Using {template_style} template: {default_template}")
            template_content = _load_template_file(str(default_template))
        else:
            # Fall back to original detailed template
            fallback_template = Path(__file__).parent.parent / "templates" / "har_comparison_expected.html"
            if fallback_template.exists():
                print(f"[TEMPLATE] Using fallback template: {fallback_template}")
                template_content = _load_template_file(str(fallback_template))
            else:
                print("[TEMPLATE] Using built-in template")
                template_content = _get_builtin_template()
    
    # Process and validate comparison data
    processed_data = _process_comparison_data(comparison_data)
    
    # Render template with data
    try:
        from jinja2 import Template, DebugUndefined
        template = Template(template_content, undefined=DebugUndefined)
        html_content = template.render(**processed_data)
    except ImportError:
        print("[WARNING] Jinja2 not found, using simple template replacement")
        html_content = _render_simple_template(template_content, processed_data)
    except Exception as e:
        print(f"[WARNING] Jinja2 template error: {e}")
        print("   Falling back to simple template replacement")
        html_content = _render_simple_template(template_content, processed_data)
    
    # Write HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    file_size = os.path.getsize(output_file) / 1024
    print(f"[SUCCESS] Report generated: {output_file} ({file_size:.1f} KB)")
    
    # Open in browser if requested
    if open_browser:
        try:
            webbrowser.open(f"file://{os.path.abspath(output_file)}")
            print("[BROWSER] Report opened in browser")
        except Exception as e:
            print(f"[WARNING] Could not open browser: {e}")
    
    return output_file

def _load_template_file(template_path: str) -> str:
    """Load template content from file"""
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        print(f"[WARNING] Could not load template {template_path}: {e}")
        return _get_builtin_template()

def _process_comparison_data(comparison_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process and validate comparison data for template rendering"""
    
    # Ensure all required sections exist with defaults
    processed = {
        'metadata': comparison_data.get('metadata', {}),
        'summary': comparison_data.get('summary', {}),
        'kpi_changes': comparison_data.get('kpi_changes', {}),
        'resource_deltas': comparison_data.get('resource_deltas', {}),
        'endpoint_timing_diffs': comparison_data.get('endpoint_timing_diffs', {}),
        'resource_type_aggregates': comparison_data.get('resource_type_aggregates', {}),
        'performance_regression': comparison_data.get('performance_regression', {}),
        'third_party_changes': comparison_data.get('third_party_changes', {}),
        'size_changes': comparison_data.get('size_changes', {}),
        'failed_requests_comparison': comparison_data.get('failed_requests_comparison', {})
    }
    
    # Add current timestamp to metadata
    if 'comparison_timestamp' not in processed['metadata']:
        processed['metadata']['comparison_timestamp'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Ensure summary has key_findings as a list
    if 'key_findings' not in processed['summary']:
        processed['summary']['key_findings'] = []
    
    # Ensure resource_deltas has counts
    if 'counts' not in processed['resource_deltas']:
        processed['resource_deltas']['counts'] = {
            'added': len(processed['resource_deltas'].get('added', [])),
            'removed': len(processed['resource_deltas'].get('removed', [])),
            'modified': len(processed['resource_deltas'].get('modified', [])),
            'unchanged': 0
        }
    
    # Ensure performance_regression has lists
    if 'regressions' not in processed['performance_regression']:
        processed['performance_regression']['regressions'] = []
    if 'improvements' not in processed['performance_regression']:
        processed['performance_regression']['improvements'] = []
    
    # Ensure failed_requests_comparison has counts
    if 'counts' not in processed['failed_requests_comparison']:
        processed['failed_requests_comparison']['counts'] = {
            'newly_failed': 0,
            'fixed': 0,
            'still_failing': 0
        }
    
    # Add helper functions for template
    processed['format_bytes'] = lambda x: f"{x / 1024:.1f}KB" if x else "0KB"
    processed['format_time'] = lambda x: f"{x:.0f}ms" if x else "0ms"
    
    return processed

def _render_simple_template(template_content: str, data: Dict[str, Any]) -> str:
    """Simple template rendering without Jinja2 (fallback)"""
    
    # Simple placeholder replacement for basic functionality
    html = template_content
    
    # Replace basic metadata
    metadata = data.get('metadata', {})
    html = html.replace('{{ metadata.base_file }}', metadata.get('base_file', 'base.har'))
    html = html.replace('{{ metadata.target_file }}', metadata.get('target_file', 'target.har'))
    html = html.replace('{{ metadata.comparison_timestamp }}', metadata.get('comparison_timestamp', ''))
    
    # Replace summary data
    summary = data.get('summary', {})
    html = html.replace('{{ summary.overall_status }}', summary.get('overall_status', 'unknown'))
    html = html.replace('{{ summary.risk_level }}', summary.get('risk_level', 'unknown'))
    
    # Replace KPI data (simplified)
    kpi = data.get('kpi_changes', {})
    if 'page_load_time' in kpi:
        plt = kpi['page_load_time']
        html = html.replace('{{ kpi_changes.page_load_time.target }}', str(plt.get('target', 0)))
        html = html.replace('{{ kpi_changes.page_load_time.absolute }}', str(plt.get('absolute', 0)))
        html = html.replace('{{ kpi_changes.page_load_time.percentage }}', str(plt.get('percentage', 0)))
    
    # Add warning about limited functionality
    warning = '''
    <div style="background: #fff3cd; border: 1px solid #ffeaa7; padding: 15px; margin: 20px 0; border-radius: 8px;">
        <strong>WARNING - Limited Report:</strong> This report was generated without Jinja2 template engine. 
        Install Jinja2 for full functionality: <code>pip install jinja2</code>
    </div>
    '''
    html = html.replace('<div class="container">', f'<div class="container">{warning}')
    
    return html

def _get_builtin_template() -> str:
    """Return built-in HTML template as fallback"""
    return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAR Performance Comparison Report</title>
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f5f5f5;
            margin: 0;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            overflow: hidden;
        }
        .header {
            background: linear-gradient(135deg, #2563eb, #0891b2);
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5rem;
            margin: 0 0 10px 0;
        }
        .content {
            padding: 30px;
        }
        .summary-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        .summary-card {
            background: #f8fafc;
            border-radius: 8px;
            padding: 20px;
            border-left: 4px solid #2563eb;
        }
        .kpi-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin: 20px 0;
        }
        .kpi-item {
            text-align: center;
            padding: 15px;
            background: #f8fafc;
            border-radius: 8px;
        }
        .kpi-value {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 5px;
        }
        .section {
            margin: 30px 0;
            padding: 20px;
            background: #f8fafc;
            border-radius: 8px;
        }
        .section h2 {
            border-bottom: 2px solid #e5e7eb;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e5e7eb;
        }
        th {
            background: #f3f4f6;
            font-weight: 600;
        }
        .alert {
            padding: 15px;
            border-radius: 8px;
            margin: 15px 0;
        }
        .alert-info {
            background: #dbeafe;
            border: 1px solid #bfdbfe;
            color: #1e40af;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>HAR Performance Comparison</h1>
            <p>{{ metadata.base_file }} vs {{ metadata.target_file }}</p>
        </div>
        
        <div class="content">
            <div class="alert alert-info">
                <strong>📊 Basic Comparison Report</strong><br>
                Overall Status: <strong>{{ summary.overall_status }}</strong><br>
                Risk Level: <strong>{{ summary.risk_level }}</strong><br>
                Generated: {{ metadata.comparison_timestamp }}
            </div>
            
            <div class="section">
                <h2>📈 Key Performance Indicators</h2>
                <div class="kpi-grid">
                    <div class="kpi-item">
                        <div class="kpi-value">{{ kpi_changes.page_load_time.target }}s</div>
                        <div>Page Load Time</div>
                        <div>Change: {{ kpi_changes.page_load_time.absolute }}s ({{ kpi_changes.page_load_time.percentage }}%)</div>
                    </div>
                    <div class="kpi-item">
                        <div class="kpi-value">{{ kpi_changes.total_requests.target }}</div>
                        <div>Total Requests</div>
                        <div>Change: {{ kpi_changes.total_requests.absolute }} ({{ kpi_changes.total_requests.percentage }}%)</div>
                    </div>
                    <div class="kpi-item">
                        <div class="kpi-value">{{ kpi_changes.total_size_mb.target }}MB</div>
                        <div>Total Size</div>
                        <div>Change: {{ kpi_changes.total_size_mb.absolute }}MB ({{ kpi_changes.total_size_mb.percentage }}%)</div>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>📦 Resource Changes Summary</h2>
                <div class="kpi-grid">
                    <div class="kpi-item">
                        <div class="kpi-value">{{ resource_deltas.counts.added }}</div>
                        <div>Added Resources</div>
                    </div>
                    <div class="kpi-item">
                        <div class="kpi-value">{{ resource_deltas.counts.removed }}</div>
                        <div>Removed Resources</div>
                    </div>
                    <div class="kpi-item">
                        <div class="kpi-value">{{ resource_deltas.counts.modified }}</div>
                        <div>Modified Resources</div>
                    </div>
                </div>
            </div>
            
            <div class="alert alert-info">
                <strong>🎯 Note:</strong> This is a simplified report. Install Jinja2 for full interactive features:
                <code>pip install jinja2</code>
            </div>
        </div>
    </div>
</body>
</html>
    '''

def create_comparison_workflow(base_har: str, target_har: str, output_dir: str = None) -> str:
    """
    Complete workflow: break down HARs, analyze, and generate report
    
    Args:
        base_har: Path to baseline HAR file
        target_har: Path to target HAR file
        output_dir: Output directory for all generated files
        
    Returns:
        Path to generated HTML report
    """
    from . import break_har, analyze_two_chunks
    
    print("🚀 Starting complete HAR comparison workflow...")
    
    if not output_dir:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"har_comparison_{timestamp}"
    
    os.makedirs(output_dir, exist_ok=True)
    
    # Step 1: Break down base HAR
    print("\n📊 Step 1: Breaking down base HAR...")
    base_data = break_har.extract_har_data(base_har)
    base_breakdown_dir = os.path.join(output_dir, "base_breakdown")
    break_har.save_broken_har_data(base_data, base_breakdown_dir)
    
    # Step 2: Break down target HAR
    print("\n📊 Step 2: Breaking down target HAR...")
    target_data = break_har.extract_har_data(target_har)
    target_breakdown_dir = os.path.join(output_dir, "target_breakdown")
    break_har.save_broken_har_data(target_data, target_breakdown_dir)
    
    # Step 3: Compare the two
    print("\n[STEP 3] Analyzing comparison...")
    comparison = analyze_two_chunks.compare_har_chunks(base_data, target_data)
    
    # Save comparison analysis
    comparison_file = os.path.join(output_dir, "comparison_analysis.json")
    analyze_two_chunks.save_comparison_analysis(comparison, comparison_file)
    
    # Step 4: Generate HTML report
    print("\n[STEP 4] Generating HTML report...")
    report_file = os.path.join(output_dir, "comparison_report.html")
    generate_comparison_report(comparison, report_file)
    
    print(f"\n[SUCCESS] Workflow complete! Output directory: {output_dir}")
    return report_file

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate HAR comparison HTML report")
    
    # Mode selection
    subparsers = parser.add_subparsers(dest='mode', help='Operation mode')
    
    # Report generation mode
    report_parser = subparsers.add_parser('report', help='Generate report from comparison JSON')
    report_parser.add_argument('--comparison', required=True, help='Comparison analysis JSON file')
    report_parser.add_argument('--output', help='Output HTML file')
    report_parser.add_argument('--template', help='Custom template file')
    report_parser.add_argument('--template-style', choices=['side-by-side', 'detailed'], 
                              default='side-by-side', help='Report template style')
    report_parser.add_argument('--no-browser', action='store_true', help='Don\'t open in browser')
    
    # Complete workflow mode
    workflow_parser = subparsers.add_parser('workflow', help='Complete comparison workflow')
    workflow_parser.add_argument('--base', required=True, help='Base HAR file')
    workflow_parser.add_argument('--target', required=True, help='Target HAR file')
    workflow_parser.add_argument('--output-dir', help='Output directory')
    
    args = parser.parse_args()
    
    if not args.mode:
        parser.print_help()
        exit(1)
    
    try:
        if args.mode == 'report':
            # Load comparison data
            with open(args.comparison, 'r', encoding='utf-8') as f:
                comparison_data = json.load(f)
            
            # Generate report
            report_file = generate_comparison_report(
                comparison_data,
                args.output,
                args.template,
                args.template_style,
                not args.no_browser
            )
            
            print(f"[REPORT] Report: {report_file}")
            
        elif args.mode == 'workflow':
            # Run complete workflow
            report_file = create_comparison_workflow(
                args.base,
                args.target,
                args.output_dir
            )
            
            print(f"[FINAL] Final report: {report_file}")
            
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        exit(1)
