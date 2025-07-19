/**
 * HAR-ANALYZE Web GUI JavaScript
 * Handles form interactions, file validation, and user experience enhancements
 */

// Global configuration
const CONFIG = {
    maxFileSize: 500 * 1024 * 1024, // 500MB in bytes
    allowedExtensions: ['har', 'json'],
    animationDuration: 300
};

/**
 * Initialize all form handlers when DOM is loaded
 */
function initializeFormHandlers() {
    const forms = document.querySelectorAll('.analysis-form');
    
    forms.forEach(form => {
        const submitButton = form.querySelector('button[type="submit"]');
        const fileInputs = form.querySelectorAll('input[type="file"]');
        
        // Handle form submission
        form.addEventListener('submit', function(e) {
            if (!validateForm(form)) {
                e.preventDefault();
                return false;
            }
            
            showLoadingState(submitButton);
            showAnalysisProgress(form);
        });
        
        // Handle file input changes
        fileInputs.forEach(input => {
            input.addEventListener('change', function() {
                validateFormInputs(form);
                updateFileInfo(input);
            });
        });
    });
}

/**
 * Initialize file validation for all file inputs
 */
function initializeFileValidation() {
    const fileInputs = document.querySelectorAll('input[type="file"]');
    
    fileInputs.forEach(input => {
        input.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            const isValid = validateFiles(files, input);
            
            if (!isValid) {
                input.value = ''; // Clear invalid files
            }
            
            updateFileDisplay(input, files);
        });
        
        // Add drag and drop functionality
        addDragDropToInput(input);
    });
}

/**
 * Initialize multi-file selection handler
 */
function initializeMultiFileHandler() {
    const multiFileInput = document.getElementById('multi-files');
    const fileListDiv = document.getElementById('file-list');
    const selectedFilesList = document.getElementById('selected-files');
    
    if (multiFileInput) {
        multiFileInput.addEventListener('change', function(e) {
            const files = Array.from(e.target.files);
            
            if (files.length >= 2) {
                showMultiFileList(files, fileListDiv, selectedFilesList);
            } else {
                hideMultiFileList(fileListDiv);
            }
        });
    }
}

/**
 * Validate files against size and extension requirements
 */
function validateFiles(files, input) {
    const errors = [];
    
    files.forEach((file, index) => {
        // Check file size
        if (file.size > CONFIG.maxFileSize) {
            errors.push(`File "${file.name}" is too large (${formatFileSize(file.size)}). Maximum size is ${formatFileSize(CONFIG.maxFileSize)}.`);
        }
        
        // Check file extension
        const extension = file.name.split('.').pop().toLowerCase();
        if (!CONFIG.allowedExtensions.includes(extension)) {
            errors.push(`File "${file.name}" has invalid extension. Allowed: ${CONFIG.allowedExtensions.join(', ')}`);
        }
    });
    
    if (errors.length > 0) {
        showValidationErrors(errors, input);
        return false;
    }
    
    clearValidationErrors(input);
    return true;
}

/**
 * Validate entire form before submission
 */
function validateForm(form) {
    const fileInputs = form.querySelectorAll('input[type="file"]');
    let isValid = true;
    
    fileInputs.forEach(input => {
        if (input.required && input.files.length === 0) {
            showInputError(input, 'Please select a file');
            isValid = false;
        } else if (input.files.length > 0) {
            const files = Array.from(input.files);
            if (!validateFiles(files, input)) {
                isValid = false;
            }
        }
    });
    
    // Special validation for multi-file input
    const multiFileInput = form.querySelector('#multi-files');
    if (multiFileInput && multiFileInput.files.length < 2 && multiFileInput.required) {
        showInputError(multiFileInput, 'Please select at least 2 files for trend analysis');
        isValid = false;
    }
    
    return isValid;
}

/**
 * Update form button states based on input validation
 */
function validateFormInputs(form) {
    const submitButton = form.querySelector('button[type="submit"]');
    const fileInputs = form.querySelectorAll('input[type="file"]');
    let hasValidFiles = true;
    
    fileInputs.forEach(input => {
        if (input.required && input.files.length === 0) {
            hasValidFiles = false;
        }
    });
    
    // Special check for multi-file input
    const multiFileInput = form.querySelector('#multi-files');
    if (multiFileInput && multiFileInput.files.length < 2 && multiFileInput.required) {
        hasValidFiles = false;
    }
    
    submitButton.disabled = !hasValidFiles;
    
    if (hasValidFiles) {
        submitButton.classList.remove('btn-secondary');
        submitButton.classList.add('btn-primary', 'btn-success', 'btn-warning');
    }
}

/**
 * Show loading state on button
 */
function showLoadingState(button) {
    const spinner = button.querySelector('.spinner-border');
    const icon = button.querySelector('i:not(.spinner-border)');
    
    button.disabled = true;
    button.classList.add('loading');
    
    if (spinner) {
        spinner.classList.remove('d-none');
    }
    
    if (icon) {
        icon.style.display = 'none';
    }
    
    // Update button text
    const originalText = button.textContent.trim();
    button.setAttribute('data-original-text', originalText);
    
    if (button.id === 'analyze-single' || button.textContent.includes('Analyze')) {
        button.innerHTML = button.innerHTML.replace(/Analyze.*/, 'Analyzing...');
    } else if (button.textContent.includes('Compare')) {
        button.innerHTML = button.innerHTML.replace(/Compare.*/, 'Comparing...');
    }
}

/**
 * Show analysis progress feedback
 */
function showAnalysisProgress(form) {
    const card = form.closest('.card');
    const progressDiv = document.createElement('div');
    progressDiv.className = 'analysis-progress mt-3';
    progressDiv.innerHTML = `
        <div class="alert alert-info">
            <div class="d-flex align-items-center">
                <div class="spinner-border spinner-border-sm me-3" role="status"></div>
                <div>
                    <strong>Analysis in progress...</strong><br>
                    <small>This may take 30-120 seconds depending on file size.</small>
                </div>
            </div>
        </div>
    `;
    
    form.appendChild(progressDiv);
    
    // Simulate progress updates (since we don't have real-time feedback)
    let progress = 0;
    const interval = setInterval(() => {
        progress += Math.random() * 10;
        if (progress >= 90) {
            clearInterval(interval);
        }
    }, 1000);
}

/**
 * Show multi-file list
 */
function showMultiFileList(files, listDiv, listElement) {
    listElement.innerHTML = '';
    
    files.forEach((file, index) => {
        const li = document.createElement('li');
        li.className = 'file-item';
        li.innerHTML = `
            <div class="d-flex justify-content-between align-items-center">
                <span>
                    <i class="fas fa-file-alt text-muted me-2"></i>
                    ${file.name}
                </span>
                <span class="file-size">${formatFileSize(file.size)}</span>
            </div>
        `;
        listElement.appendChild(li);
    });
    
    listDiv.classList.remove('d-none');
    listDiv.classList.add('fade-in');
}

/**
 * Hide multi-file list
 */
function hideMultiFileList(listDiv) {
    listDiv.classList.add('d-none');
}

/**
 * Update file information display
 */
function updateFileInfo(input) {
    const file = input.files[0];
    if (!file) return;
    
    // Find or create file info element
    let fileInfo = input.parentElement.querySelector('.file-info');
    if (!fileInfo) {
        fileInfo = document.createElement('div');
        fileInfo.className = 'file-info mt-2';
        input.parentElement.appendChild(fileInfo);
    }
    
    fileInfo.innerHTML = `
        <div class="small text-muted">
            <i class="fas fa-file-check text-success me-1"></i>
            Selected: <strong>${file.name}</strong> (${formatFileSize(file.size)})
        </div>
    `;
}

/**
 * Add drag and drop functionality to file input
 */
function addDragDropToInput(input) {
    const container = input.parentElement;
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, preventDefaults, false);
    });
    
    ['dragenter', 'dragover'].forEach(eventName => {
        container.addEventListener(eventName, () => container.classList.add('dragover'), false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        container.addEventListener(eventName, () => container.classList.remove('dragover'), false);
    });
    
    container.addEventListener('drop', (e) => {
        const files = e.dataTransfer.files;
        input.files = files;
        input.dispatchEvent(new Event('change'));
    }, false);
}

/**
 * Show validation errors
 */
function showValidationErrors(errors, input) {
    clearValidationErrors(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-errors mt-2';
    
    errors.forEach(error => {
        const errorItem = document.createElement('div');
        errorItem.className = 'text-danger small';
        errorItem.innerHTML = `<i class="fas fa-exclamation-triangle me-1"></i>${error}`;
        errorDiv.appendChild(errorItem);
    });
    
    input.parentElement.appendChild(errorDiv);
    input.classList.add('is-invalid');
}

/**
 * Show input-specific error
 */
function showInputError(input, message) {
    clearValidationErrors(input);
    
    const errorDiv = document.createElement('div');
    errorDiv.className = 'validation-errors mt-2';
    errorDiv.innerHTML = `
        <div class="text-danger small">
            <i class="fas fa-exclamation-triangle me-1"></i>${message}
        </div>
    `;
    
    input.parentElement.appendChild(errorDiv);
    input.classList.add('is-invalid');
}

/**
 * Clear validation errors
 */
function clearValidationErrors(input) {
    const existingErrors = input.parentElement.querySelector('.validation-errors');
    if (existingErrors) {
        existingErrors.remove();
    }
    input.classList.remove('is-invalid');
}

/**
 * Format file size for display
 */
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * Prevent default drag behaviors
 */
function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
}

/**
 * Initialize tooltips and other Bootstrap components
 */
function initializeBootstrapComponents() {
    // Initialize tooltips if Bootstrap is loaded
    if (typeof bootstrap !== 'undefined') {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

/**
 * Handle page visibility changes
 */
function handleVisibilityChange() {
    document.addEventListener('visibilitychange', function() {
        if (document.hidden) {
            // Page is hidden
            console.log('Page hidden');
        } else {
            // Page is visible
            console.log('Page visible');
        }
    });
}

/**
 * Initialize everything when DOM is ready
 */
document.addEventListener('DOMContentLoaded', function() {
    console.log('HAR-ANALYZE GUI initialized');
    
    initializeFormHandlers();
    initializeFileValidation();
    initializeMultiFileHandler();
    initializeBootstrapComponents();
    handleVisibilityChange();
    
    // Add fade-in animation to cards
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 100);
    });
});

/**
 * Export functions for external use
 */
window.HARAnalyzer = {
    validateFiles,
    formatFileSize,
    showLoadingState,
    CONFIG
};
