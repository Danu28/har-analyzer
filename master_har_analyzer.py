#!/usr/bin/env python3
"""
Master HAR Analyzer Script
==========================
This script orchestrates the complete HAR analysis workflow:
1. Lists all HAR files in the HAR-Files folder
2. Allows user to select a file by number
3. Processes the HAR file through all analysis stages
4. Generates comprehensive reports in the reports folder
5. Opens the final report in the browser

Usage: python master_har_analyzer.py
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

# Color codes for better terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print colored header"""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*len(text)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*len(text)}{Colors.ENDC}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.OKBLUE}[INFO]{Colors.ENDC} {text}")

def print_success(text):
    """Print success message"""
    print(f"{Colors.OKGREEN}[SUCCESS]{Colors.ENDC} {text}")

def print_warning(text):
    """Print warning message"""
    print(f"{Colors.WARNING}[WARNING]{Colors.ENDC} {text}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.FAIL}[ERROR]{Colors.ENDC} {text}")

def print_step(step_num, total_steps, description):
    """Print current step"""
    print(f"\n{Colors.OKCYAN}[STEP {step_num}/{total_steps}]{Colors.ENDC} {description}")

def find_har_files():
    """Find all HAR files in the HAR-Files directory"""
    har_files_dir = Path("HAR-Files")
    
    if not har_files_dir.exists():
        print_error("HAR-Files directory not found!")
        print_info("Please ensure you have a 'HAR-Files' folder with .har files")
        return []
    
    har_files = list(har_files_dir.glob("*.har"))
    return sorted(har_files)

def display_har_files(har_files):
    """Display available HAR files for user selection"""
    print_header("Available HAR Files")
    
    if not har_files:
        print_error("No HAR files found in HAR-Files directory!")
        return None
    
    print(f"Found {len(har_files)} HAR file(s):\n")
    
    for idx, har_file in enumerate(har_files, 1):
        # Get file size for display
        try:
            file_size = har_file.stat().st_size
            size_mb = file_size / (1024 * 1024)
            print(f"{Colors.OKBLUE}[{idx}]{Colors.ENDC} {har_file.name} ({size_mb:.1f}MB)")
        except:
            print(f"{Colors.OKBLUE}[{idx}]{Colors.ENDC} {har_file.name}")
    
    print(f"\n{Colors.OKBLUE}[0]{Colors.ENDC} Exit")
    
    while True:
        try:
            choice = input(f"\n{Colors.BOLD}Select HAR file number: {Colors.ENDC}")
            choice = int(choice)
            
            if choice == 0:
                print_info("Exiting...")
                return None
            elif 1 <= choice <= len(har_files):
                selected_file = har_files[choice - 1]
                print_success(f"Selected: {selected_file.name}")
                return selected_file
            else:
                print_error(f"Invalid choice. Please enter a number between 0 and {len(har_files)}")
        except ValueError:
            print_error("Invalid input. Please enter a number.")
        except KeyboardInterrupt:
            print_info("\nOperation cancelled by user.")
            return None

def create_reports_directory():
    """Create reports directory if it doesn't exist"""
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    return reports_dir

def run_script(script_path, args=None, description=""):
    """Run a Python script and capture output"""
    cmd = [sys.executable, script_path]
    if args:
        cmd.extend(args)
    
    print_info(f"Running: {' '.join(map(str, cmd))}")
    
    try:
        # Set environment to handle Unicode properly
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        
        # Run script with explicit UTF-8 encoding for output
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            cwd=os.getcwd(), 
            env=env,
            encoding='utf-8',
            errors='replace'  # Replace characters that can't be decoded
        )
        
        if result.returncode == 0:
            print_success(f"{description} completed successfully")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print_error(f"{description} failed with return code {result.returncode}")
            if result.stderr:
                print(f"Error output:\n{result.stderr}")
            if result.stdout:
                print(f"Standard output:\n{result.stdout}")
            return False
    except Exception as e:
        print_error(f"Failed to run {script_path}: {str(e)}")
        return False

def get_har_base_name(har_file):
    """Get base name without extension for file operations"""
    return har_file.stem

def move_report_to_reports_folder(har_base_name, reports_dir):
    """Move generated report to reports folder with proper naming"""
    # Look for generated HTML report
    current_report = Path(f"{har_base_name}_performance_report.html")
    
    if current_report.exists():
        # Create new report filename
        new_report_name = f"{har_base_name}.html"
        new_report_path = reports_dir / new_report_name
        
        # Remove existing report if it exists
        if new_report_path.exists():
            new_report_path.unlink()
            print_info(f"Removed existing report: {new_report_path}")
        
        # Move and rename the report
        current_report.rename(new_report_path)
        print_success(f"Report saved as: {new_report_path}")
        return new_report_path
    else:
        print_error(f"Generated report not found: {current_report}")
        return None

def archive_analysis_files(har_base_name, reports_dir):
    """Move analysis files to a dedicated folder in the reports directory."""
    # Create a dedicated folder for the analysis files
    analysis_data_dir = reports_dir / f"{har_base_name}_analysis_data"
    analysis_data_dir.mkdir(exist_ok=True)
    print_info(f"Archiving analysis files to: {analysis_data_dir}")

    analysis_files = [
        "agent_summary.json",
        "Performance_Analysis_Report.md"
    ]

    for file_name in analysis_files:
        current_path = Path(file_name)
        if current_path.exists():
            new_path = analysis_data_dir / file_name
            # If file exists in destination, remove it before moving
            if new_path.exists():
                new_path.unlink()
            current_path.rename(new_path)
            print_info(f"Archived: {file_name}")

def display_final_summary(har_file, report_path, start_time):
    """Display final summary of the analysis"""
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("Analysis Complete!")
    print_success(f"HAR File: {har_file.name}")
    print_success(f"Report Location: {report_path}")
    print_success(f"Processing Time: {duration.total_seconds():.1f} seconds")
    
    # Try to read agent summary for summary stats
    try:
        agent_summary_file = Path("agent_summary.json")
        if agent_summary_file.exists():
            with open(agent_summary_file, 'r') as f:
                data = json.load(f)
                perf_summary = data.get('performance_summary', {})
                print_info(f"Performance Grade: {perf_summary.get('performance_grade', 'N/A')}")
                print_info(f"Page Load Time: {perf_summary.get('page_load_time', 'N/A')}")
                print_info(f"DOM Ready Time: {perf_summary.get('dom_ready_time', 'N/A')}")
                print_info(f"Total Requests: {perf_summary.get('total_requests', 'N/A')}")
    except:
        pass

def main():
    """Main execution function"""
    start_time = datetime.now()
    
    print_header("🚀 Master HAR Analyzer")
    print_info("This tool will analyze your HAR files and generate comprehensive performance reports")
    print_info(f"Started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Step 1: Find and display HAR files
    print_step(1, 5, "Finding HAR files")
    har_files = find_har_files()
    selected_har = display_har_files(har_files)
    
    if not selected_har:
        return
    
    # Step 2: Create reports directory
    print_step(2, 5, "Setting up reports directory")
    reports_dir = create_reports_directory()
    har_base_name = get_har_base_name(selected_har)
    
    # Step 3: Break down HAR file
    print_step(3, 5, "Breaking down HAR file into analyzable chunks")
    if not run_script("scripts/break_har_file.py", ["--har", str(selected_har)], description="HAR file breakdown"):
        print_error("Failed to break down HAR file. Exiting.")
        return
    
    # Step 4: Analyze performance
    print_step(4, 5, "Analyzing performance metrics")
    if not run_script("scripts/analyze_performance.py", ["--har", str(selected_har)], description="Performance analysis"):
        print_error("Failed to analyze performance. Exiting.")
        return
    
    # Step 5: Generate HTML report
    print_step(5, 5, "Generating comprehensive HTML report")
    if not run_script("scripts/generate_html_report.py", [har_base_name], description="HTML report generation"):
        print_error("Failed to generate HTML report. Exiting.")
        return
    
    # Move report to reports folder
    print_info("Moving report to reports folder...")
    final_report_path = move_report_to_reports_folder(har_base_name, reports_dir)
    
    if final_report_path:
        # Display final summary before cleanup
        display_final_summary(selected_har, final_report_path, start_time)
        
        # Archive analysis files instead of deleting them
        print_info("Archiving analysis files...")
        archive_analysis_files(har_base_name, reports_dir)
        
        # Open report in browser
        try:
            webbrowser.open(f"file:///{final_report_path.absolute()}")
            print_success("Report opened in your default browser!")
        except Exception as e:
            print_warning(f"Could not open browser automatically: {e}")
            print_info(f"Please manually open: {final_report_path}")
    else:
        print_error("Failed to move report to reports folder.")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\nOperation cancelled by user.")
    except Exception as e:
        print_error(f"Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
