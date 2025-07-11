#!/usr/bin/env python3
"""
Demo: Multi-HAR Analysis
========================
Interactive multi-run HAR analysis demo.
Allows users to select multiple HAR files from the HAR-Files directory and generate comparative reports.

Scripts used:
- scripts/analyze_multi_har_runs.py
- scripts/compare_multi_har_performance.py  
- scripts/generate_multi_har_report.py
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
import json

def print_banner():
    """Print the demo banner."""
    print("🎯 HAR-ANALYZE Multi-Run Interactive Demo")
    print("=" * 50)
    print("✨ Select HAR files and generate multi-run analysis reports")
    print("📊 Executive format - High-level summary for stakeholders")
    print("🚀 Professional performance analysis in seconds")
    print("=" * 50)
    print()

def get_har_files():
    """Get list of HAR files from HAR-Files directory."""
    har_dir = Path("HAR-Files")
    if not har_dir.exists():
        print("❌ HAR-Files directory not found!")
        return []
    
    har_files = list(har_dir.glob("*.har"))
    if not har_files:
        print("❌ No HAR files found in HAR-Files directory!")
        return []
    
    # Sort files by name for consistent ordering
    har_files.sort(key=lambda x: x.name)
    return har_files

def display_har_files(har_files):
    """Display available HAR files with numbers."""
    print("📁 Available HAR Files:")
    print("-" * 60)
    for i, har_file in enumerate(har_files, 1):
        # Get file size
        size_mb = har_file.stat().st_size / (1024 * 1024)
        print(f"{i:2d}. {har_file.name:<40} ({size_mb:.2f} MB)")
    print("-" * 60)
    print()

def get_file_selection(har_files):
    """Get user's file selection."""
    while True:
        print("🎯 Select HAR files to analyze:")
        print("   • Enter numbers separated by commas (e.g., 1,3,5)")
        print("   • Minimum 2 files, maximum 10 files")
        print("   • Type 'q' to quit")
        print()
        
        selection = input("Your selection: ").strip()
        
        if selection.lower() == 'q':
            return None
        
        try:
            # Parse selection
            indices = [int(x.strip()) for x in selection.split(',')]
            
            # Validate indices
            if any(i < 1 or i > len(har_files) for i in indices):
                print(f"❌ Invalid selection! Please choose numbers between 1 and {len(har_files)}")
                print()
                continue
            
            # Check count
            if len(indices) < 2:
                print("❌ Please select at least 2 files for comparison")
                print()
                continue
            
            if len(indices) > 10:
                print("❌ Maximum 10 files supported for comparison")
                print()
                continue
            
            # Remove duplicates and sort
            indices = sorted(list(set(indices)))
            selected_files = [har_files[i-1] for i in indices]
            
            return selected_files
            
        except ValueError:
            print("❌ Invalid format! Please enter numbers separated by commas (e.g., 1,3,5)")
            print()
            continue

def get_report_type():
    """Get user's preferred report type."""
    report_types = {
        '1': ('executive', 'High-level summary for stakeholders and decision makers')
    }
    
    while True:
        print("📊 Select Report Type:")
        print("-" * 50)
        for key, (report_type, description) in report_types.items():
            print(f"{key}. {report_type.title():<15} - {description}")
        print("-" * 50)
        print()
        
        choice = input("Your choice (1): ").strip()
        
        if choice in report_types:
            return report_types[choice][0]
        else:
            print("❌ Invalid choice! Please select 1")
            print()

def generate_output_filename(selected_files, report_type):
    """Generate output filename based on selection."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Create a meaningful name based on selected files
    if len(selected_files) <= 3:
        # Use actual filenames for small selections
        base_names = [f.stem for f in selected_files]
        name_part = "_".join(base_names)[:50]  # Limit length
    else:
        # Use count for larger selections
        name_part = f"{len(selected_files)}_files"
    
    return f"reports/multi_run_{report_type}_{name_part}_{timestamp}.html"

def run_analysis(selected_files, report_type, output_file):
    """Run the multi-run analysis."""
    print("🚀 Generating Multi-Run Analysis Report...")
    print("-" * 50)
    print(f"📁 Files: {len(selected_files)} HAR files")
    print(f"📊 Type: {report_type.title()}")
    print(f"💾 Output: {output_file}")
    print("-" * 50)
    
    # Prepare command
    cmd = [
        sys.executable,
        "scripts/generate_multi_har_report.py"
    ]
    
    # Add file paths
    for file_path in selected_files:
        cmd.append(str(file_path))
    
    # Add options
    cmd.extend(["-o", output_file, "-t", report_type])
    
    try:
        # Run the analysis
        print("⏳ Processing...")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        print("✅ Analysis completed successfully!")
        print(f"📄 Report saved: {output_file}")
        
        # Check if file exists and get size
        output_path = Path(output_file)
        if output_path.exists():
            size_kb = output_path.stat().st_size / 1024
            print(f"📊 Report size: {size_kb:.1f} KB")
        
        return True
        
    except subprocess.CalledProcessError as e:
        print("❌ Analysis failed!")
        print(f"Error: {e.stderr}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def open_report_prompt(output_file):
    """Ask user if they want to open the report."""
    while True:
        choice = input("\n🌐 Open report in browser? (y/n): ").strip().lower()
        if choice in ['y', 'yes']:
            try:
                import webbrowser
                webbrowser.open(f"file:///{Path(output_file).absolute()}")
                print("🎉 Report opened in your default browser!")
            except Exception as e:
                print(f"❌ Could not open browser: {e}")
                print(f"📂 Please manually open: {Path(output_file).absolute()}")
            break
        elif choice in ['n', 'no']:
            print(f"📂 Report saved at: {Path(output_file).absolute()}")
            break
        else:
            print("❌ Please enter 'y' for yes or 'n' for no")

def show_quick_examples():
    """Show quick example selections."""
    print("🎯 Quick Examples:")
    print("   • Enter '1,2,3' to compare first 3 files")
    print("   • Enter '1,3,5' to compare files 1, 3, and 5")
    print("   • Enter '2,4' to compare files 2 and 4")
    print()

def main():
    """Main demo function."""
    print_banner()
    
    # Get available HAR files
    har_files = get_har_files()
    if not har_files:
        return
    
    # Display files
    display_har_files(har_files)
    
    # Show examples
    show_quick_examples()
    
    while True:
        # Get file selection
        selected_files = get_file_selection(har_files)
        if selected_files is None:
            print("👋 Thanks for using HAR-ANALYZE Multi-Run Demo!")
            break
        
        print(f"\n✅ Selected {len(selected_files)} files:")
        for i, file_path in enumerate(selected_files, 1):
            print(f"   {i}. {file_path.name}")
        print()
        
        # Get report type
        report_type = get_report_type()
        
        # Generate output filename
        output_file = generate_output_filename(selected_files, report_type)
        
        # Ensure reports directory exists
        Path("reports").mkdir(exist_ok=True)
        
        # Run analysis
        success = run_analysis(selected_files, report_type, output_file)
        
        if success:
            open_report_prompt(output_file)
        
        # Ask if user wants to continue
        print("\n" + "="*50)
        while True:
            continue_choice = input("🔄 Analyze another set of files? (y/n): ").strip().lower()
            if continue_choice in ['y', 'yes']:
                print("\n" + "="*50)
                break
            elif continue_choice in ['n', 'no']:
                print("👋 Thanks for using HAR-ANALYZE Multi-Run Demo!")
                return
            else:
                print("❌ Please enter 'y' for yes or 'n' for no")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Demo interrupted. Thanks for using HAR-ANALYZE!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        print("Please check your setup and try again.")
