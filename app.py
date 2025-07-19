#!/usr/bin/env python3
"""
HAR-ANALYZE Flask Web GUI Application

A web-based graphical user interface for the HAR-ANALYZE project,
providing an intuitive way to analyze HAR files through a browser.
"""

import os
import tempfile
import logging
import uuid
import subprocess
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, flash, jsonify
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Flask app configuration
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'har-analyze-dev-key-' + str(uuid.uuid4()))
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024  # 500MB max file size
app.config['UPLOAD_FOLDER'] = tempfile.mkdtemp(prefix='har_analyze_uploads_')

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'har', 'json'}

def allowed_file(filename: str) -> bool:
    """Check if uploaded file has allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file) -> Optional[Path]:
    """Save uploaded file and return path."""
    if file and file.filename and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_filename = f"{timestamp}_{filename}"
        file_path = Path(app.config['UPLOAD_FOLDER']) / unique_filename
        file.save(str(file_path))
        logger.info(f"File saved: {file_path}")
        return file_path
    return None

def analyze_single_har_workflow(file_path: Path) -> Dict[str, Any]:
    """Run the complete single HAR file analysis workflow."""
    try:
        base_dir = Path(__file__).parent
        har_name = file_path.stem
        
        # Create temporary directory for this analysis
        temp_analysis_dir = Path(tempfile.mkdtemp(prefix=f'analysis_{har_name}_'))
        temp_har_path = temp_analysis_dir / file_path.name
        
        # Copy HAR file to temporary location
        import shutil
        shutil.copy2(file_path, temp_har_path)
        
        logger.info(f"Starting analysis workflow for: {file_path.name}")
        
        # Step 1: Break HAR file into chunks
        logger.info("Step 1: Breaking HAR file into chunks...")
        cmd1 = [
            sys.executable,
            str(base_dir / "scripts" / "break_har_for_single_analysis.py"),
            "--har",
            str(temp_har_path),
        ]
        
        result1 = subprocess.run(cmd1, capture_output=True, text=True, cwd=base_dir)
        if result1.returncode != 0:
            raise Exception(f"HAR breaking failed: {result1.stderr}")
        
        # Step 2: Analyze performance
        logger.info("Step 2: Analyzing performance...")
        chunk_dir = base_dir / "har_chunks" / har_name
        cmd2 = [
            sys.executable,
            str(base_dir / "scripts" / "analyze_single_har_performance.py"),
            "--input",
            str(chunk_dir),
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=base_dir)
        if result2.returncode != 0:
            raise Exception(f"Performance analysis failed: {result2.stderr}")
        
        # Step 3: Generate HTML report
        logger.info("Step 3: Generating HTML report...")
        analysis_file = chunk_dir / "agent_summary.json"
        template_file = base_dir / "templates" / "har_single_premium.html"
        
        # Create reports directory if it doesn't exist
        reports_dir = base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        output_file = reports_dir / f"{har_name}_gui_report.html"
        
        cmd3 = [
            sys.executable,
            str(base_dir / "scripts" / "generate_single_har_report.py"),
            "--analysis-file",
            str(analysis_file),
            "--template-file",
            str(template_file),
            "--output",
            str(output_file),
            "--no-browser",
        ]
        
        result3 = subprocess.run(cmd3, capture_output=True, text=True, cwd=base_dir)
        if result3.returncode != 0:
            raise Exception(f"Report generation failed: {result3.stderr}")
        
        if not output_file.exists():
            raise Exception("Report file was not created")
        
        return {
            'success': True,
            'report_path': str(output_file),
            'analysis_file': str(analysis_file),
            'message': 'Analysis completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Analysis workflow failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Analysis failed: {str(e)}'
        }

def analyze_comparison_workflow(baseline_path: Path, target_path: Path) -> Dict[str, Any]:
    """Run the HAR comparison analysis workflow."""
    try:
        base_dir = Path(__file__).parent
        logger.info(f"Starting comparison workflow: {baseline_path.name} vs {target_path.name}")
        
        # Create temporary directory for comparison
        temp_comparison_dir = Path(tempfile.mkdtemp(prefix='comparison_'))
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Step 1: Break baseline HAR file
        logger.info("Step 1: Breaking baseline HAR file...")
        baseline_output_dir = temp_comparison_dir / "baseline"
        cmd1 = [
            sys.executable,
            str(base_dir / "scripts" / "break_har_for_comparison.py"),
            "--har",
            str(baseline_path),
            "--output",
            str(baseline_output_dir),
        ]
        
        result1 = subprocess.run(cmd1, capture_output=True, text=True, cwd=base_dir)
        if result1.returncode != 0:
            raise Exception(f"Baseline HAR breaking failed: {result1.stderr}")
        
        baseline_json = baseline_output_dir / "har_breakdown.json"
        if not baseline_json.exists():
            raise Exception("Baseline breakdown JSON was not created")
        
        # Step 2: Break target HAR file
        logger.info("Step 2: Breaking target HAR file...")
        target_output_dir = temp_comparison_dir / "target"
        cmd2 = [
            sys.executable,
            str(base_dir / "scripts" / "break_har_for_comparison.py"),
            "--har",
            str(target_path),
            "--output",
            str(target_output_dir),
        ]
        
        result2 = subprocess.run(cmd2, capture_output=True, text=True, cwd=base_dir)
        if result2.returncode != 0:
            raise Exception(f"Target HAR breaking failed: {result2.stderr}")
        
        target_json = target_output_dir / "har_breakdown.json"
        if not target_json.exists():
            raise Exception("Target breakdown JSON was not created")
        
        # Step 3: Run comparison analysis
        logger.info("Step 3: Running comparison analysis...")
        comparison_json = temp_comparison_dir / "comparison_analysis.json"
        cmd3 = [
            sys.executable,
            str(base_dir / "scripts" / "compare_har_analysis.py"),
            "--base",
            str(baseline_json),
            "--target",
            str(target_json),
            "--output",
            str(comparison_json),
        ]
        
        result3 = subprocess.run(cmd3, capture_output=True, text=True, cwd=base_dir)
        if result3.returncode != 0:
            raise Exception(f"Comparison analysis failed: {result3.stderr}")
        
        if not comparison_json.exists():
            raise Exception("Comparison analysis JSON was not created")
        
        # Step 4: Generate comparison report
        logger.info("Step 4: Generating comparison report...")
        reports_dir = base_dir / "reports"
        reports_dir.mkdir(exist_ok=True)
        
        output_file = reports_dir / f"comparison_report_{timestamp}.html"
        
        cmd4 = [
            sys.executable,
            str(base_dir / "scripts" / "generate_har_comparison_report.py"),
            "report",
            "--comparison",
            str(comparison_json),
            "--output",
            str(output_file),
            "--template-style",
            "side-by-side",
            "--no-browser",
        ]
        
        result4 = subprocess.run(cmd4, capture_output=True, text=True, cwd=base_dir)
        if result4.returncode != 0:
            raise Exception(f"Comparison report generation failed: {result4.stderr}")
        
        if not output_file.exists():
            raise Exception("Comparison report file was not created")
        
        return {
            'success': True,
            'report_path': str(output_file),
            'comparison_file': str(comparison_json),
            'message': 'Comparison analysis completed successfully'
        }
        
    except Exception as e:
        logger.error(f"Comparison workflow failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Comparison analysis failed: {str(e)}'
        }

def analyze_multi_file_workflow(file_paths: List[Path]) -> Dict[str, Any]:
    """Run the multi-file trend analysis workflow."""
    try:
        base_dir = Path(__file__).parent
        logger.info(f"Starting multi-file analysis for {len(file_paths)} files")
        
        # Copy files to HAR-Files directory temporarily
        har_files_dir = base_dir / "HAR-Files"
        har_files_dir.mkdir(exist_ok=True)
        
        temp_files = []
        for file_path in file_paths:
            temp_file = har_files_dir / file_path.name
            import shutil
            shutil.copy2(file_path, temp_file)
            temp_files.append(temp_file)
        
        try:
            # Generate multi-file report using the script directly
            logger.info("Generating multi-file report...")
            reports_dir = base_dir / "reports"
            reports_dir.mkdir(exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = reports_dir / f"multi_file_report_{timestamp}.html"
            
            # Use the generate_multi_har_report.py script directly with HAR files as arguments
            cmd = [
                sys.executable,
                str(base_dir / "scripts" / "generate_multi_har_report.py"),
                *[str(tf) for tf in temp_files],  # HAR files as positional arguments
                "-o", str(output_file),
                "-t", "executive",
                "-v",
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=base_dir)
            if result.returncode != 0:
                raise Exception(f"Multi-file report generation failed: {result.stderr}")
            
            if not output_file.exists():
                raise Exception("Multi-file report was not created")
            
            return {
                'success': True,
                'report_path': str(output_file),
                'message': f'Multi-file analysis completed for {len(file_paths)} files'
            }
            
        finally:
            # Clean up temporary files
            for temp_file in temp_files:
                try:
                    temp_file.unlink()
                except:
                    pass
        
    except Exception as e:
        logger.error(f"Multi-file workflow failed: {e}")
        return {
            'success': False,
            'error': str(e),
            'message': f'Multi-file analysis failed: {str(e)}'
        }

@app.route('/')
def index():
    """Main dashboard page."""
    return render_template('gui_index.html')

@app.route('/analyze-single', methods=['POST'])
def analyze_single():
    """Handle single HAR file analysis."""
    try:
        if 'har_file' not in request.files:
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        file = request.files['har_file']
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(url_for('index'))
        
        # Save uploaded file
        file_path = save_uploaded_file(file)
        if not file_path:
            flash('Invalid file type. Please upload a .har file', 'error')
            return redirect(url_for('index'))
        
        # Run analysis workflow
        result = analyze_single_har_workflow(file_path)
        
        if result['success']:
            flash('Analysis completed successfully!', 'success')
            return send_file(result['report_path'], as_attachment=False)
        else:
            flash(f"Analysis failed: {result['message']}", 'error')
            return redirect(url_for('index'))
            
    except RequestEntityTooLarge:
        flash('File too large. Maximum file size is 500MB', 'error')
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Unexpected error in analyze_single: {e}")
        flash('An unexpected error occurred', 'error')
        return redirect(url_for('index'))

@app.route('/compare', methods=['POST'])
def compare_files():
    """Handle two-file comparison."""
    try:
        if 'baseline_file' not in request.files or 'target_file' not in request.files:
            flash('Please select both baseline and target files', 'error')
            return redirect(url_for('index'))
        
        baseline_file = request.files['baseline_file']
        target_file = request.files['target_file']
        
        if baseline_file.filename == '' or target_file.filename == '':
            flash('Please select both baseline and target files', 'error')
            return redirect(url_for('index'))
        
        # Save uploaded files
        baseline_path = save_uploaded_file(baseline_file)
        target_path = save_uploaded_file(target_file)
        
        if not baseline_path or not target_path:
            flash('Invalid file type. Please upload .har files', 'error')
            return redirect(url_for('index'))
        
        # Run comparison workflow
        result = analyze_comparison_workflow(baseline_path, target_path)
        
        if result['success']:
            flash('Comparison analysis completed successfully!', 'success')
            return send_file(result['report_path'], as_attachment=False)
        else:
            flash(f"Comparison failed: {result['message']}", 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Unexpected error in compare_files: {e}")
        flash('An unexpected error occurred during comparison', 'error')
        return redirect(url_for('index'))

@app.route('/analyze-multi', methods=['POST'])
def analyze_multi():
    """Handle multi-file trend analysis."""
    try:
        files = request.files.getlist('multi_files')
        
        if len(files) < 2:
            flash('Please select at least 2 files for trend analysis', 'error')
            return redirect(url_for('index'))
        
        # Save all uploaded files
        file_paths = []
        for file in files:
            if file.filename != '':
                file_path = save_uploaded_file(file)
                if file_path:
                    file_paths.append(file_path)
        
        if len(file_paths) < 2:
            flash('At least 2 valid HAR files are required', 'error')
            return redirect(url_for('index'))
        
        # Run multi-file analysis workflow
        result = analyze_multi_file_workflow(file_paths)
        
        if result['success']:
            flash(f'Multi-file analysis completed for {len(file_paths)} files!', 'success')
            return send_file(result['report_path'], as_attachment=False)
        else:
            flash(f"Multi-file analysis failed: {result['message']}", 'error')
            return redirect(url_for('index'))
            
    except Exception as e:
        logger.error(f"Unexpected error in analyze_multi: {e}")
        flash('An unexpected error occurred during multi-file analysis', 'error')
        return redirect(url_for('index'))

@app.route('/status')
def status():
    """API endpoint for checking application status."""
    return jsonify({
        'status': 'running',
        'upload_folder': app.config['UPLOAD_FOLDER'],
        'max_file_size': app.config['MAX_CONTENT_LENGTH'],
        'allowed_extensions': list(ALLOWED_EXTENSIONS)
    })

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File too large. Maximum file size is 500MB', 'error')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(e):
    """Handle internal server errors."""
    logger.error(f"Internal server error: {e}")
    flash('An internal error occurred', 'error')
    return redirect(url_for('index'))

if __name__ == '__main__':
    # Create necessary directories
    os.makedirs('static/css', exist_ok=True)
    os.makedirs('static/js', exist_ok=True)
    os.makedirs('templates', exist_ok=True)
    
    print("=" * 60)
    print("🚀 HAR-ANALYZE Web GUI Starting...")
    print("=" * 60)
    print(f"📁 Upload folder: {app.config['UPLOAD_FOLDER']}")
    print(f"📊 Max file size: {app.config['MAX_CONTENT_LENGTH'] / (1024*1024):.0f}MB")
    print(f"🔗 Open your browser to: http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)
