#!/usr/bin/env python3
"""
HAR Performance Analysis HTML Report Generator
- Generates comprehensive HTML reports from HAR analysis data
- Includes interactive charts, detailed metrics, and actionable insights
- Follows HAR Q&A assistant instructions for performance analysis
"""

import os
import sys
import json
import datetime
from pathlib import Path
from urllib.parse import urlparse

class HARHtmlReportGenerator:
    def __init__(self, har_chunks_dir=None):
        """Initialize the HTML report generator"""
        self.har_chunks_dir = har_chunks_dir or "har_chunks"
        self.report_data = {}
        
    def load_analysis_data(self, har_name):
        """Load all analysis data from HAR chunks directory"""
        chunks_path = Path(self.har_chunks_dir) / har_name
        
        if not chunks_path.exists():
            raise FileNotFoundError(f"HAR chunks directory not found: {chunks_path}")
        
        # Load all relevant JSON files
        files_to_load = {
            'header': '01_header_and_metadata.json',
            'summary': '02_requests_summary.json',
            'agent_summary': 'agent_summary.json',
            'document': '04_resource_type_document.json',
            'script': '04_resource_type_script.json',
            'image': '04_resource_type_image.json',
            'font': '04_resource_type_font.json',
            'xhr': '04_resource_type_xhr.json',
            'fetch': '04_resource_type_fetch.json'
        }
        
        for key, filename in files_to_load.items():
            filepath = chunks_path / filename
            if filepath.exists():
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.report_data[key] = json.load(f)
                except Exception as e:
                    print(f"Warning: Could not load {filename}: {e}")
                    self.report_data[key] = {}
            else:
                print(f"Warning: {filename} not found")
                self.report_data[key] = {}
        
        return self.report_data
    
    def analyze_performance_issues(self):
        """Analyze performance issues and generate insights"""
        agent_data = self.report_data.get('agent_summary', {})
        summary_data = self.report_data.get('summary', {})
        
        issues = []
        recommendations = []
        
        # Extract key metrics
        perf_summary = agent_data.get('performance_summary', {})
        load_time = perf_summary.get('page_load_time', '0s')
        dom_time = perf_summary.get('dom_ready_time', '0s')
        total_requests = perf_summary.get('total_requests', 0)
        
        # Convert times to seconds for analysis
        load_time_sec = float(load_time.replace('s', '')) if 's' in load_time else 0
        dom_time_sec = float(dom_time.replace('s', '')) if 's' in dom_time else 0
        
        # Analyze load times
        if load_time_sec > 10:
            issues.append(f"Critical: Page load time is {load_time} (should be <3s)")
            recommendations.append("Implement code splitting and lazy loading")
            recommendations.append("Optimize and compress large JavaScript bundles")
        elif load_time_sec > 5:
            issues.append(f"Poor: Page load time is {load_time} (should be <3s)")
            recommendations.append("Reduce bundle sizes and optimize critical path")
        
        # Analyze DOM ready time
        if dom_time_sec > 5:
            issues.append(f"Critical: DOM ready time is {dom_time} (should be <2s)")
            recommendations.append("Minimize blocking JavaScript and CSS")
        
        # Analyze request count
        if total_requests > 100:
            issues.append(f"Excessive requests: {total_requests} requests (should be <50)")
            recommendations.append("Bundle smaller assets and use resource consolidation")
            recommendations.append("Implement HTTP/2 server push or preload strategies")
        
        # Analyze large assets
        largest_assets = agent_data.get('largest_assets', [])
        for asset in largest_assets[:3]:  # Top 3 largest
            size_kb = asset.get('size_kb', 0)
            if size_kb > 5000:  # > 5MB
                issues.append(f"Massive asset: {size_kb/1024:.1f}MB file detected")
                recommendations.append("Break large bundles into smaller chunks")
                recommendations.append("Implement tree shaking to remove unused code")
        
        # Analyze failed requests
        failed_requests = agent_data.get('failed_requests', [])
        if failed_requests:
            issues.append(f"Failed requests: {len(failed_requests)} requests failed")
            recommendations.append("Fix or remove broken third-party dependencies")
        
        # Analyze slow requests
        critical_issues = agent_data.get('critical_issues', {})
        slow_requests = critical_issues.get('very_slow_requests', 0)
        if slow_requests > 10:
            issues.append(f"Many slow requests: {slow_requests} requests >3s")
            recommendations.append("Optimize server response times and CDN configuration")
            recommendations.append("Consider deferring non-critical third-party scripts")
        
        return {
            'issues': issues,
            'recommendations': list(set(recommendations)),  # Remove duplicates
            'severity': 'critical' if load_time_sec > 10 else 'warning' if load_time_sec > 5 else 'info'
        }
    
    def generate_resource_breakdown_chart(self):
        """Generate data for resource breakdown chart"""
        agent_data = self.report_data.get('agent_summary', {})
        resource_breakdown = agent_data.get('resource_breakdown', {})
        
        chart_data = []
        colors = {
            'script': '#FF6B6B',
            'image': '#4ECDC4', 
            'document': '#45B7D1',
            'xhr': '#96CEB4',
            'fetch': '#FFEAA7',
            'font': '#DDA0DD',
            'ping': '#FFA07A',
            'other': '#D3D3D3'
        }
        
        for resource_type, count in resource_breakdown.items():
            chart_data.append({
                'label': resource_type.title(),
                'value': count,
                'color': colors.get(resource_type, '#D3D3D3')
            })
        
        return sorted(chart_data, key=lambda x: x['value'], reverse=True)
    
    def generate_timeline_data(self):
        """Generate timeline data for waterfall chart"""
        summary_data = self.report_data.get('summary', {})
        requests = summary_data.get('requests', [])
        
        timeline_data = []
        for i, req in enumerate(requests[:20]):  # Top 20 requests
            start_time = req.get('startedDateTime', '')
            duration = req.get('time', 0)
            url = req.get('url', '')
            
            # Parse domain for grouping
            try:
                domain = urlparse(url).netloc
            except:
                domain = 'unknown'
            
            timeline_data.append({
                'name': url.split('/')[-1][:30] + '...' if len(url.split('/')[-1]) > 30 else url.split('/')[-1],
                'domain': domain,
                'start': i * 100,  # Simplified timeline
                'duration': duration,
                'url': url,
                'size': req.get('size', 0),
                'status': req.get('status', 0)
            })
        
        return timeline_data
    
    def generate_html_report(self, har_name, output_file=None):
        """Generate the complete HTML report"""
        if not output_file:
            output_file = f"{har_name}_performance_report.html"
        
        # Load analysis data
        self.load_analysis_data(har_name)
        
        # Generate analysis
        performance_analysis = self.analyze_performance_issues()
        resource_chart_data = self.generate_resource_breakdown_chart()
        timeline_data = self.generate_timeline_data()
        
        # Extract key data
        agent_data = self.report_data.get('agent_summary', {})
        header_data = self.report_data.get('header', {})
        
        perf_summary = agent_data.get('performance_summary', {})
        critical_issues = agent_data.get('critical_issues', {})
        largest_assets = agent_data.get('largest_assets', [])
        slowest_requests = agent_data.get('slowest_requests', [])
        failed_requests = agent_data.get('failed_requests', [])
        
        # Helper function to get performance class
        def get_perf_class(value, thresholds):
            if isinstance(value, str) and 's' in value:
                value = float(value.replace('s', ''))
            if value > thresholds[0]:
                return 'critical'
            elif value > thresholds[1]:
                return 'warning'
            else:
                return 'success'
        
        # Generate HTML sections
        failed_requests_html = ""
        if failed_requests:
            failed_rows = []
            for req in failed_requests:
                url = req.get('url', 'N/A')
                status = req.get('status', 'N/A')
                status_class = f"status-{str(status)[0]}xx" if str(status).isdigit() else "status-error"
                failed_rows.append(f"""
                <tr>
                    <td class="url-cell" title="{url}">{url[:60]}...</td>
                    <td><span class="status-badge {status_class}">{status}</span></td>
                </tr>
                """)
            
            failed_requests_html = f"""
            <div class="section">
                <div class="section-header">
                    <h2>❌ Failed Requests</h2>
                    <p>Requests that failed to load properly</p>
                </div>
                <div class="section-content">
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Request</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(failed_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            """
        
        # Generate largest assets HTML
        largest_assets_rows = []
        max_size = max([a.get('size_kb', 1) for a in largest_assets]) if largest_assets else 1
        for asset in largest_assets[:10]:
            url = asset.get('url', 'N/A')
            size_kb = asset.get('size_kb', 0)
            bar_width = min(size_kb / max_size * 200, 200)
            largest_assets_rows.append(f"""
            <tr>
                <td class="url-cell" title="{url}">{url[:50]}...</td>
                <td>{size_kb:.1f} KB</td>
                <td><div class="size-bar" style="width: {bar_width}px;"></div></td>
            </tr>
            """)
        
        # Generate slowest requests HTML
        slowest_requests_rows = []
        max_time = max([r.get('time_ms', 1) for r in slowest_requests]) if slowest_requests else 1
        for req in slowest_requests[:10]:
            url = req.get('url', 'N/A')
            time_ms = req.get('time_ms', 0)
            bar_width = min(time_ms / max_time * 200, 200)
            slowest_requests_rows.append(f"""
            <tr>
                <td class="url-cell" title="{url}">{url[:50]}...</td>
                <td>{time_ms:.0f} ms</td>
                <td><div class="size-bar" style="width: {bar_width}px; background: linear-gradient(90deg, #e74c3c, #c0392b);"></div></td>
            </tr>
            """)
        
        # Generate issues and recommendations HTML
        issues_html = ''.join(f'<li class="issue-item">{issue}</li>' for issue in performance_analysis['issues'])
        recommendations_html = ''.join(f'<li class="recommendation-item">{rec}</li>' for rec in performance_analysis['recommendations'])
        
        # Get performance classes
        load_time_str = perf_summary.get('page_load_time', '0s')
        dom_time_str = perf_summary.get('dom_ready_time', '0s')
        load_time_class = get_perf_class(load_time_str, [10, 5])
        dom_time_class = get_perf_class(dom_time_str, [5, 2])
        
        total_requests = perf_summary.get('total_requests', 0)
        requests_class = 'critical' if total_requests > 100 else 'warning' if total_requests > 50 else 'success'
        
        # Generate enhanced analysis sections
        enhanced_analysis_html = self._generate_enhanced_analysis_html(agent_data)
        
        # Generate complete HTML
        html_content = self._generate_html_template(
            har_name=har_name,
            perf_summary=perf_summary,
            critical_issues=critical_issues,
            load_time_class=load_time_class,
            dom_time_class=dom_time_class,
            requests_class=requests_class,
            performance_analysis=performance_analysis,
            issues_html=issues_html,
            recommendations_html=recommendations_html,
            resource_chart_data=resource_chart_data,
            largest_assets_rows=largest_assets_rows,
            slowest_requests_rows=slowest_requests_rows,
            failed_requests_html=failed_requests_html,
            largest_assets=largest_assets,
            enhanced_analysis_html=enhanced_analysis_html
        )
        
        # Write HTML file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"HTML report generated: {output_file}")
        print(f"Performance Grade: {perf_summary.get('performance_grade', 'N/A')}")
        print(f"Load Time: {perf_summary.get('page_load_time', 'N/A')}")
        print(f"Total Requests: {perf_summary.get('total_requests', 'N/A')}")
        print(f"Critical Issues: {len(performance_analysis['issues'])}")
        print(f"Recommendations: {len(performance_analysis['recommendations'])}")
        
        return output_file
    
    def _generate_enhanced_analysis_html(self, agent_data):
        """Generate HTML for enhanced analysis sections"""
        compression_data = agent_data.get('compression_analysis', {})
        caching_data = agent_data.get('caching_analysis', {})
        dns_data = agent_data.get('dns_connection_analysis', {})
        third_party_data = agent_data.get('enhanced_third_party_analysis', {})
        
        # Compression Analysis Section
        compression_html = ""
        if compression_data:
            uncompressed_count = compression_data.get('compression_opportunity_count', 0)
            potential_savings = compression_data.get('total_potential_savings_kb', 0)
            
            if uncompressed_count > 0:
                compression_rows = []
                for resource in compression_data.get('uncompressed_resources', [])[:5]:
                    url = resource.get('url', 'N/A')
                    size_kb = round(resource.get('size', 0) / 1024, 1)
                    potential_kb = round(resource.get('potential_savings', 0) / 1024, 1)
                    compression_rows.append(f"""
                    <tr>
                        <td class="url-cell" title="{url}">{url[:50]}...</td>
                        <td>{size_kb:.1f} KB</td>
                        <td>{potential_kb:.1f} KB</td>
                    </tr>
                    """)
                
                compression_html = f"""
                <div class="section">
                    <div class="section-header">
                        <h2>🗜️ Compression Analysis</h2>
                        <p>Resources that could benefit from compression</p>
                    </div>
                    <div class="section-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value warning">{uncompressed_count}</div>
                                <div class="metric-label">Uncompressed Resources</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value info">{potential_savings:.1f} KB</div>
                                <div class="metric-label">Potential Savings</div>
                            </div>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Resource</th>
                                    <th>Current Size</th>
                                    <th>Potential Savings</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(compression_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
                """
        
        # Caching Analysis Section
        caching_html = ""
        if caching_data:
            no_cache_count = len(caching_data.get('no_cache_resources', []))
            short_cache_count = len(caching_data.get('short_cache_resources', []))
            
            if no_cache_count > 0 or short_cache_count > 0:
                cache_rows = []
                for resource in caching_data.get('no_cache_resources', [])[:5]:
                    url = resource.get('url', 'N/A')
                    resource_type = resource.get('resourceType', 'unknown')
                    cache_rows.append(f"""
                    <tr>
                        <td class="url-cell" title="{url}">{url[:50]}...</td>
                        <td>{resource_type}</td>
                        <td><span class="status-badge status-error">No Cache</span></td>
                    </tr>
                    """)
                
                for resource in caching_data.get('short_cache_resources', [])[:5]:
                    url = resource.get('url', 'N/A')
                    resource_type = resource.get('resourceType', 'unknown')
                    max_age = resource.get('max_age_hours', 0)
                    cache_rows.append(f"""
                    <tr>
                        <td class="url-cell" title="{url}">{url[:50]}...</td>
                        <td>{resource_type}</td>
                        <td><span class="status-badge status-warning">{max_age:.1f}h</span></td>
                    </tr>
                    """)
                
                caching_html = f"""
                <div class="section">
                    <div class="section-header">
                        <h2>🔄 Caching Analysis</h2>
                        <p>Resources with caching optimization opportunities</p>
                    </div>
                    <div class="section-content">
                        <div class="metric-grid">
                            <div class="metric-card">
                                <div class="metric-value critical">{no_cache_count}</div>
                                <div class="metric-label">No Cache Headers</div>
                            </div>
                            <div class="metric-card">
                                <div class="metric-value warning">{short_cache_count}</div>
                                <div class="metric-label">Short Cache Duration</div>
                            </div>
                        </div>
                        <table class="data-table">
                            <thead>
                                <tr>
                                    <th>Resource</th>
                                    <th>Type</th>
                                    <th>Cache Status</th>
                                </tr>
                            </thead>
                            <tbody>
                                {''.join(cache_rows)}
                            </tbody>
                        </table>
                    </div>
                </div>
                """
        
        # DNS/Connection Analysis Section
        dns_html = ""
        if dns_data:
            avg_dns = dns_data.get('avg_dns_time', 0)
            avg_ssl = dns_data.get('avg_ssl_time', 0)

            # Prepare display values and classes for N/A
            if avg_dns == "N/A":
                avg_dns_display = "N/A"
                avg_dns_class = "warning"
            else:
                avg_dns_display = f"{avg_dns:.1f} ms"
                avg_dns_class = "warning" if avg_dns > 50 else "success"

            if avg_ssl == "N/A":
                avg_ssl_display = "N/A"
                avg_ssl_class = "warning"
            else:
                avg_ssl_display = f"{avg_ssl:.1f} ms"
                avg_ssl_class = "warning" if avg_ssl > 200 else "success"

            domain_rows = []
            for domain in dns_data.get('domain_performance', [])[:5]:
                domain_name = domain.get('domain', 'N/A')
                requests = domain.get('requests', 0)
                avg_dns_ms = domain.get('avg_dns_ms', 0)
                avg_ssl_ms = domain.get('avg_ssl_ms', 0)
                total_time = domain.get('total_time_ms', 0)
                domain_rows.append(f"""
                <tr>
                    <td class="url-cell" title="{domain_name}">{domain_name[:40]}...</td>
                    <td>{requests}</td>
                    <td>{avg_dns_ms if avg_dns_ms != 0 else 'N/A'} ms</td>
                    <td>{avg_ssl_ms if avg_ssl_ms != 0 else 'N/A'} ms</td>
                    <td>{total_time:.1f} ms</td>
                </tr>
                """)

            dns_html = f"""
            <div class="section">
                <div class="section-header">
                    <h2>🌐 DNS & Connection Analysis</h2>
                    <p>Network timing and connection performance</p>
                </div>
                <div class="section-content">
                    <div class="metric-grid">
                        <div class="metric-card">
                            <div class="metric-value {avg_dns_class}">{avg_dns_display}</div>
                            <div class="metric-label">Average DNS Time</div>
                        </div>
                        <div class="metric-card">
                            <div class="metric-value {avg_ssl_class}">{avg_ssl_display}</div>
                            <div class="metric-label">Average SSL Time</div>
                        </div>
                    </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Domain</th>
                                <th>Requests</th>
                                <th>Avg DNS</th>
                                <th>Avg SSL</th>
                                <th>Total Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(domain_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            """
        
        # Enhanced Third-Party Analysis Section
        third_party_html = ""
        if third_party_data:
            total_domains = third_party_data.get('total_third_party_domains', 0)
            blocking_domains = third_party_data.get('blocking_third_parties', [])

            category_rows = []
            for category, stats in third_party_data.get('category_breakdown', {}).items():
                domains = stats.get('domains', 0)
                requests = stats.get('requests', 0)
                total_time = stats.get('total_time', 0)
                category_rows.append(f"""
                <tr>
                    <td>{category.title()}</td>
                    <td>{domains}</td>
                    <td>{requests}</td>
                    <td>{total_time:.0f} ms</td>
                </tr>
                """)

            # Add blocking domains table if any
            blocking_table_html = ""
            if blocking_domains:
                domain_impact = third_party_data.get('domain_impact', {})
                table_rows = []
                for domain in blocking_domains:
                    stats = domain_impact.get(domain, {})
                    blocking_time = stats.get('blocking_time', 0)
                    requests = stats.get('requests', 0)
                    table_rows.append(f"<tr><td>{domain}</td><td>{blocking_time:.0f} ms</td><td>{requests}</td></tr>")
                blocking_table_html = f"""
                    <table class='data-table' style='margin-top:8px;'>
                        <thead>
                            <tr><th>Domain</th><th>Blocking Time</th><th>Requests</th></tr>
                        </thead>
                        <tbody>
                            {''.join(table_rows)}
                        </tbody>
                    </table>
                """

            # Third-party domains table (all domains)
            # Show category breakdown table (Category, Domains, Requests, Total Time)
            category_table_html = ""
            category_breakdown = third_party_data.get('category_breakdown', {})
            if category_breakdown:
                cat_rows = []
                for category, stats in category_breakdown.items():
                    domains = stats.get('domains', 0)
                    requests = stats.get('requests', 0)
                    total_time = stats.get('total_time', 0)
                    cat_rows.append(f"<tr><td>{category.title()}</td><td>{domains}</td><td>{requests}</td><td>{total_time:.0f} ms</td></tr>")
                category_table_html = f"""
                    <table class='data-table' style='margin-top:8px;'>
                        <thead>
                            <tr><th>Category</th><th>Domains</th><th>Requests</th><th>Total Time</th></tr>
                        </thead>
                        <tbody>
                            {''.join(cat_rows)}
                        </tbody>
                    </table>
                """
            all_domains_table_html = category_table_html

            third_party_html = f"""
            <div class="section">
                <div class="section-header">
                    <h2>🔗 Enhanced Third-Party Analysis</h2>
                    <p>Categorized third-party service impact</p>
                </div>
                <div class="section-content">
                    <div class="metric-grid">
            <div class="metric-card" id="thirdparty-metric-card" style="cursor:pointer;">
                <div class="metric-value info">{total_domains}</div>
                <div class="metric-label">Third-Party Domains</div>
            </div>
            <div class="metric-card" id="blocking-metric-card" style="cursor:pointer;">
                <div class="metric-value {'critical' if len(blocking_domains) > 0 else 'success'}">{len(blocking_domains)}</div>
                <div class="metric-label">Blocking Services</div>
            </div>
                    </div>
            <div id="thirdparty-table-container" style="margin-top:10px; display:none;">
                {all_domains_table_html}
            </div>
            <div id="blocking-table-container" style="margin-top:10px; display:none;">
                {blocking_table_html}
            </div>
                    <table class="data-table">
                        <thead>
                            <tr>
                                <th>Category</th>
                                <th>Domains</th>
                                <th>Requests</th>
                                <th>Total Time</th>
                            </tr>
                        </thead>
                        <tbody>
                            {''.join(category_rows)}
                        </tbody>
                    </table>
                </div>
            </div>
            <script>
            document.addEventListener('DOMContentLoaded', function() {{
                var blockingCard = document.getElementById('blocking-metric-card');
                var blockingTable = document.getElementById('blocking-table-container');
                var thirdPartyCard = document.getElementById('thirdparty-metric-card');
                var thirdPartyTable = document.getElementById('thirdparty-table-container');
                function hideAllTables() {{
                    if (blockingTable) blockingTable.style.display = 'none';
                    if (thirdPartyTable) thirdPartyTable.style.display = 'none';
                }}
                if (blockingCard && blockingTable) {{
                    blockingCard.addEventListener('click', function() {{
                        hideAllTables();
                        blockingTable.style.display = 'block';
                    }});
                }}
                if (thirdPartyCard && thirdPartyTable) {{
                    thirdPartyCard.addEventListener('click', function() {{
                        hideAllTables();
                        thirdPartyTable.style.display = 'block';
                    }});
                }}
            }});
            </script>
            """
        
        return compression_html + caching_html + dns_html + third_party_html
    
    def _generate_html_template(self, **kwargs):
        """Generate the HTML template with all data"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>HAR Performance Analysis Report - {kwargs['har_name']}</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            color: #333;
            background-color: #f8f9fa;
        }}
        
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px 0;
            text-align: center;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 4px 20px rgba(0,0,0,0.1);
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .metric-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        
        .metric-card {{
            background: white;
            padding: 25px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            text-align: center;
            transition: transform 0.3s ease;
        }}
        
        .metric-card:hover {{
            transform: translateY(-5px);
        }}
        
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin-bottom: 10px;
        }}
        
        .metric-label {{
            color: #666;
            font-size: 0.9em;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .critical {{ color: #e74c3c; }}
        .warning {{ color: #f39c12; }}
        .success {{ color: #27ae60; }}
        .info {{ color: #3498db; }}
        
        .section {{
            background: white;
            margin-bottom: 30px;
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .section-header {{
            background: #f8f9fa;
            padding: 20px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .section-header h2 {{
            font-size: 1.5em;
            color: #2c3e50;
            margin-bottom: 5px;
        }}
        
        .section-content {{
            padding: 20px;
        }}
        
        .issue-list {{
            list-style: none;
        }}
        
        .issue-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #e74c3c;
            background: #fdf2f2;
            border-radius: 5px;
        }}
        
        .recommendation-list {{
            list-style: none;
        }}
        
        .recommendation-item {{
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #27ae60;
            background: #f0f9f0;
            border-radius: 5px;
        }}
        
        .recommendation-item:before {{
            content: "💡 ";
            margin-right: 10px;
        }}
        
        .chart-container {{
            position: relative;
            height: 400px;
            margin-bottom: 20px;
        }}
        
        .data-table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }}
        
        .data-table th,
        .data-table td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .data-table th {{
            background: #f8f9fa;
            font-weight: 600;
            color: #2c3e50;
        }}
        
        .data-table tr:hover {{
            background: #f8f9fa;
        }}
        
        .url-cell {{
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            cursor: pointer;
        }}
        
        .size-bar {{
            display: inline-block;
            height: 20px;
            background: linear-gradient(90deg, #3498db, #2ecc71);
            border-radius: 10px;
            margin-right: 10px;
            min-width: 10px;
        }}
        
        .status-badge {{
            padding: 4px 8px;
            border-radius: 20px;
            font-size: 0.8em;
            font-weight: bold;
            color: white;
        }}
        
        .status-2xx {{ background: #27ae60; }}
        .status-3xx {{ background: #f39c12; }}
        .status-4xx {{ background: #e74c3c; }}
        .status-5xx {{ background: #8e44ad; }}
        .status-error {{ background: #95a5a6; }}
        
        .footer {{
            text-align: center;
            margin-top: 50px;
            padding: 20px;
            color: #666;
            font-size: 0.9em;
        }}
        
        @media (max-width: 768px) {{
            .metric-grid {{
                grid-template-columns: 1fr;
            }}
            
            .container {{
                padding: 10px;
            }}
            
            .header h1 {{
                font-size: 2em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 HAR Performance Analysis Report</h1>
            <p>Analysis of {kwargs['har_name']} • Generated on {datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p')}</p>
        </div>
        
        <!-- Performance Metrics -->
        <div class="metric-grid">
            <div class="metric-card">
                <div class="metric-value {kwargs['load_time_class']}">{kwargs['perf_summary'].get('page_load_time', 'N/A')}</div>
                <div class="metric-label">Page Load Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {kwargs['dom_time_class']}">{kwargs['perf_summary'].get('dom_ready_time', 'N/A')}</div>
                <div class="metric-label">DOM Ready Time</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {kwargs['requests_class']}">{kwargs['perf_summary'].get('total_requests', 'N/A')}</div>
                <div class="metric-label">Total Requests</div>
            </div>
            <div class="metric-card">
                <div class="metric-value {kwargs['performance_analysis']['severity']}">{kwargs['perf_summary'].get('performance_grade', 'N/A')}</div>
                <div class="metric-label">Performance Grade</div>
            </div>
        </div>
        
        <!-- Critical Issues -->
        <div class="section">
            <div class="section-header">
                <h2>🚨 Critical Performance Issues</h2>
                <p>Issues that significantly impact user experience and need immediate attention</p>
            </div>
            <div class="section-content">
                <ul class="issue-list">
                    {kwargs['issues_html']}
                </ul>
            </div>
        </div>
        
        <!-- Recommendations -->
        <div class="section">
            <div class="section-header">
                <h2>💡 Performance Recommendations</h2>
                <p>Actionable steps to improve page performance</p>
            </div>
            <div class="section-content">
                <ul class="recommendation-list">
                    {kwargs['recommendations_html']}
                </ul>
            </div>
        </div>
        
        <!-- Resource Breakdown Chart -->
        <div class="section">
            <div class="section-header">
                <h2>📊 Resource Breakdown</h2>
                <p>Distribution of resources by type</p>
            </div>
            <div class="section-content">
                <div class="chart-container">
                    <canvas id="resourceChart"></canvas>
                </div>
            </div>
        </div>
        
        <!-- Largest Assets -->
        <div class="section">
            <div class="section-header">
                <h2>📦 Largest Assets</h2>
                <p>Top assets by size that may be impacting performance</p>
            </div>
            <div class="section-content">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Asset</th>
                            <th>Size</th>
                            <th>Visual</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(kwargs['largest_assets_rows'])}
                    </tbody>
                </table>
            </div>
        </div>
        
        <!-- Slowest Requests -->
        <div class="section">
            <div class="section-header">
                <h2>🐌 Slowest Requests</h2>
                <p>Requests taking the longest time to complete</p>
            </div>
            <div class="section-content">
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>Request</th>
                            <th>Time</th>
                            <th>Visual</th>
                        </tr>
                    </thead>
                    <tbody>
                        {''.join(kwargs['slowest_requests_rows'])}
                    </tbody>
                </table>
            </div>
        </div>
        
        {kwargs['failed_requests_html']}
        
        <!-- Summary Stats -->
        <div class="section">
            <div class="section-header">
                <h2>📈 Summary Statistics</h2>
                <p>Key performance indicators and metrics</p>
            </div>
            <div class="section-content">
                <div class="metric-grid">
                    <div class="metric-card">
                        <div class="metric-value info">{kwargs['critical_issues'].get('very_slow_requests', 0)}</div>
                        <div class="metric-label">Very Slow Requests (>3s)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value warning">{kwargs['critical_issues'].get('slow_requests', 0)}</div>
                        <div class="metric-label">Slow Requests (>1s)</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value critical">{kwargs['critical_issues'].get('failed_requests', 0)}</div>
                        <div class="metric-label">Failed Requests</div>
                    </div>
                    <div class="metric-card">
                        <div class="metric-value info">{len(kwargs['largest_assets'])}</div>
                        <div class="metric-label">Assets Analyzed</div>
                    </div>
                </div>
            </div>
        </div>
        
        <!-- Enhanced Analysis Sections -->
        {kwargs['enhanced_analysis_html']}
        
        <div class="footer">
            <p>Generated by HAR Performance Analysis Tool • {datetime.datetime.now().strftime('%Y')}</p>
            <p>Report based on HAR file analysis using industry-standard performance metrics</p>
        </div>
    </div>
    
    <script>
        // Resource Breakdown Chart
        const ctx = document.getElementById('resourceChart').getContext('2d');
        const resourceData = {json.dumps(kwargs['resource_chart_data'])};
        
        new Chart(ctx, {{
            type: 'doughnut',
            data: {{
                labels: resourceData.map(item => item.label),
                datasets: [{{
                    data: resourceData.map(item => item.value),
                    backgroundColor: resourceData.map(item => item.color),
                    borderWidth: 2,
                    borderColor: '#fff'
                }}]
            }},
            options: {{
                responsive: true,
                maintainAspectRatio: false,
                plugins: {{
                    legend: {{
                        position: 'bottom',
                        labels: {{
                            padding: 20,
                            usePointStyle: true
                        }}
                    }},
                    tooltip: {{
                        callbacks: {{
                            label: function(context) {{
                                const label = context.label || '';
                                const value = context.raw || 0;
                                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                                const percentage = ((value / total) * 100).toFixed(1);
                                return `${{label}}: ${{value}} (${{percentage}}%)`;
                            }}
                        }}
                    }}
                }}
            }}
        }});
        
        // Add interactive features
        document.addEventListener('DOMContentLoaded', function() {{
            // Add click-to-copy functionality for URLs
            const urlCells = document.querySelectorAll('.url-cell');
            urlCells.forEach(cell => {{
                cell.addEventListener('click', function() {{
                    const url = this.getAttribute('title');
                    if (navigator.clipboard) {{
                        navigator.clipboard.writeText(url).then(() => {{
                            const originalText = this.textContent;
                            this.textContent = 'Copied!';
                            setTimeout(() => {{
                                this.textContent = originalText;
                            }}, 1000);
                        }});
                    }}
                }});
            }});
            
            // Add hover effects
            const metricCards = document.querySelectorAll('.metric-card');
            metricCards.forEach(card => {{
                card.addEventListener('mouseenter', function() {{
                    this.style.boxShadow = '0 8px 25px rgba(0,0,0,0.15)';
                }});
                card.addEventListener('mouseleave', function() {{
                    this.style.boxShadow = '0 2px 10px rgba(0,0,0,0.1)';
                }});
            }});
        }});
    </script>
</body>
</html>"""

def main():
    """Main function to generate HTML report"""
    if len(sys.argv) < 2:
        print("Usage: python generate_html_report.py <har_name>")
        print("Example: python generate_html_report.py v3_Pie_LP_reload_private_tab")
        sys.exit(1)
    
    har_name = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    generator = HARHtmlReportGenerator()
    
    try:
        report_file = generator.generate_html_report(har_name, output_file)
        print(f"\n🎉 Report generation complete!")
        print(f"📁 Open the file: {report_file}")
        
        # Try to open the report automatically
        try:
            import webbrowser
            webbrowser.open(f"file://{os.path.abspath(report_file)}")
            print("🌐 Report opened in your default browser")
        except:
            print("💡 Manually open the HTML file in your browser to view the report")
            
    except Exception as e:
        print(f"Error generating report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
