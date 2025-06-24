// Image Processing Service - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
});

function initializeApp() {
    // Initialize all components
    initializeFileUpload();
    initializeImageGallery();
    initializeTransformControls();
    initializeFormValidation();
    initializeNotifications();
    initializeProgressBars();
    
    // Add fade-in animation to main content
    document.body.classList.add('fade-in');
}

// CSRF Token for AJAX requests
function getCSRFToken() {
    return document.querySelector('meta[name=csrf-token]')?.getAttribute('content') || window.csrfToken;
}

// File Upload Functionality
function initializeFileUpload() {
    const uploadZone = document.getElementById('uploadZone');
    const fileInput = document.getElementById('fileInput');
    const uploadForm = document.getElementById('uploadForm');
    
    if (!uploadZone || !fileInput) return;
    
    // Drag and drop functionality
    uploadZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        uploadZone.classList.add('dragover');
    });
    
    uploadZone.addEventListener('dragleave', function() {
        uploadZone.classList.remove('dragover');
    });
    
    uploadZone.addEventListener('drop', function(e) {
        e.preventDefault();
        uploadZone.classList.remove('dragover');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFileSelect(files[0]);
        }
    });
    
    // Click to upload
    uploadZone.addEventListener('click', function() {
        fileInput.click();
    });
    
    fileInput.addEventListener('change', function() {
        if (this.files.length > 0) {
            handleFileSelect(this.files[0]);
        }
    });
    
    // Form submission
    if (uploadForm) {
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            uploadFile();
        });
    }
}

function handleFileSelect(file) {
    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showNotification('Please select a valid image file (JPEG, PNG, GIF, WebP)', 'error');
        return;
    }
    
    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        showNotification('File size must be less than 16MB', 'error');
        return;
    }
    
    // Update UI
    const fileInput = document.getElementById('fileInput');
    const uploadZone = document.getElementById('uploadZone');
    const fileName = document.getElementById('fileName');
    const fileSize = document.getElementById('fileSize');
    
    if (fileInput) fileInput.files = createFileList(file);
    if (fileName) fileName.textContent = file.name;
    if (fileSize) fileSize.textContent = formatFileSize(file.size);
    
    // Show preview if possible
    showImagePreview(file);
    
    // Enable upload button
    const uploadBtn = document.getElementById('uploadBtn');
    if (uploadBtn) {
        uploadBtn.disabled = false;
        uploadBtn.classList.remove('d-none');
    }
}

function createFileList(file) {
    const dt = new DataTransfer();
    dt.items.add(file);
    return dt.files;
}

function showImagePreview(file) {
    const preview = document.getElementById('imagePreview');
    if (!preview) return;
    
    const reader = new FileReader();
    reader.onload = function(e) {
        preview.innerHTML = `
            <img src="${e.target.result}" class="img-fluid rounded" 
                 style="max-height: 200px; max-width: 100%;" alt="Preview">
        `;
        preview.classList.remove('d-none');
    };
    reader.readAsDataURL(file);
}

function uploadFile() {
    const form = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const progressContainer = document.getElementById('uploadProgress');
    const progressBar = document.getElementById('progressBar');
    
    if (!form) return;
    
    const formData = new FormData(form);
    
    // Show progress
    if (progressContainer) progressContainer.classList.remove('d-none');
    if (uploadBtn) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Uploading...';
    }
    
    // Upload with progress tracking
    const xhr = new XMLHttpRequest();
    
    xhr.upload.addEventListener('progress', function(e) {
        if (e.lengthComputable && progressBar) {
            const percentComplete = (e.loaded / e.total) * 100;
            progressBar.style.width = percentComplete + '%';
            progressBar.textContent = Math.round(percentComplete) + '%';
        }
    });
    
    xhr.addEventListener('load', function() {
        if (xhr.status === 200 || xhr.status === 201) {
            showNotification('Image uploaded successfully!', 'success');
            setTimeout(() => {
                window.location.href = '/dashboard';
            }, 1000);
        } else {
            const response = JSON.parse(xhr.responseText);
            showNotification(response.error || 'Upload failed', 'error');
        }
    });
    
    xhr.addEventListener('error', function() {
        showNotification('Upload failed. Please try again.', 'error');
    });
    
    xhr.addEventListener('loadend', function() {
        if (uploadBtn) {
            uploadBtn.disabled = false;
            uploadBtn.innerHTML = '<i class="fas fa-upload me-2"></i>Upload Image';
        }
        if (progressContainer) {
            setTimeout(() => {
                progressContainer.classList.add('d-none');
                if (progressBar) {
                    progressBar.style.width = '0%';
                    progressBar.textContent = '';
                }
            }, 2000);
        }
    });
    
    xhr.open('POST', '/api/images/upload');
    xhr.setRequestHeader('X-CSRF-Token', getCSRFToken());
    xhr.send(formData);
}

// Image Gallery
function initializeImageGallery() {
    const gallery = document.getElementById('imageGallery');
    if (!gallery) return;
    
    // Add click handlers for image actions
    gallery.addEventListener('click', function(e) {
        if (e.target.classList.contains('btn-transform')) {
            const imageId = e.target.dataset.imageId;
            window.location.href = `/transform/${imageId}`;
        } else if (e.target.classList.contains('btn-delete')) {
            const imageId = e.target.dataset.imageId;
            deleteImage(imageId);
        } else if (e.target.classList.contains('btn-download')) {
            const imageUrl = e.target.dataset.imageUrl;
            downloadImage(imageUrl);
        }
    });
}

function deleteImage(imageId) {
    if (!confirm('Are you sure you want to delete this image? This action cannot be undone.')) {
        return;
    }
    
    showLoadingOverlay();
    
    fetch(`/api/images/${imageId}`, {
        method: 'DELETE',
        headers: {
            'X-CSRF-Token': getCSRFToken(),
            'Content-Type': 'application/json'
        }
    })
    .then(response => response.json())
    .then(data => {
        hideLoadingOverlay();
        if (data.message) {
            showNotification(data.message, 'success');
            // Remove image from gallery
            const imageCard = document.querySelector(`[data-image-id="${imageId}"]`).closest('.col-md-4');
            if (imageCard) {
                imageCard.remove();
            }
        } else {
            showNotification(data.error || 'Failed to delete image', 'error');
        }
    })
    .catch(error => {
        hideLoadingOverlay();
        showNotification('Failed to delete image', 'error');
    });
}

function downloadImage(imageUrl) {
    const link = document.createElement('a');
    link.href = imageUrl;
    link.download = '';
    link.target = '_blank';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Transform Controls
function initializeTransformControls() {
    // Range sliders
    const rangeInputs = document.querySelectorAll('input[type="range"]');
    rangeInputs.forEach(input => {
        const output = input.nextElementSibling;
        if (output && output.classList.contains('range-output')) {
            input.addEventListener('input', function() {
                output.textContent = this.value;
            });
        }
    });
    
    // Transform form
    const transformForm = document.getElementById('transformForm');
    if (transformForm) {
        transformForm.addEventListener('submit', function(e) {
            e.preventDefault();
            submitTransformation();
        });
    }
    
    // Real-time preview updates
    const previewControls = document.querySelectorAll('.preview-control');
    previewControls.forEach(control => {
        control.addEventListener('input', updatePreview);
    });
}

function submitTransformation() {
    const form = document.getElementById('transformForm');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    if (!form) return;
    
    // Show loading state
    if (submitBtn) {
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Processing...';
    }
    
    showLoadingOverlay();
    
    // Submit form normally for now (can be enhanced with AJAX later)
    form.submit();
}

function updatePreview() {
    // This would implement real-time preview updates
    // For now, we'll keep it simple and just show visual feedback
    const preview = document.getElementById('imagePreview');
    if (preview) {
        preview.style.filter = getFilterString();
    }
}

function getFilterString() {
    const grayscale = document.getElementById('grayscale')?.checked;
    const sepia = document.getElementById('sepia')?.checked;
    
    let filters = [];
    if (grayscale) filters.push('grayscale(100%)');
    if (sepia) filters.push('sepia(100%)');
    
    return filters.join(' ');
}

// Form Validation
function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
    
    // Real-time validation
    const inputs = document.querySelectorAll('input, select, textarea');
    inputs.forEach(input => {
        input.addEventListener('blur', function() {
            if (this.checkValidity()) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
            } else {
                this.classList.remove('is-valid');
                this.classList.add('is-invalid');
            }
        });
    });
}

// Notifications
function initializeNotifications() {
    // Auto-hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
}

function showNotification(message, type = 'info') {
    const alertHtml = `
        <div class="alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show" role="alert">
            <i class="fas fa-${getIconForType(type)} me-2"></i>
            ${escapeHtml(message)}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        </div>
    `;
    
    const container = document.querySelector('.container');
    if (container) {
        const alertDiv = document.createElement('div');
        alertDiv.innerHTML = alertHtml;
        container.insertBefore(alertDiv.firstElementChild, container.firstChild);
        
        // Auto-hide after 5 seconds
        setTimeout(() => {
            const alert = container.querySelector('.alert');
            if (alert) {
                const bsAlert = new bootstrap.Alert(alert);
                bsAlert.close();
            }
        }, 5000);
    }
}

function getIconForType(type) {
    const icons = {
        success: 'check-circle',
        error: 'exclamation-triangle',
        warning: 'exclamation-circle',
        info: 'info-circle'
    };
    return icons[type] || 'info-circle';
}

// Progress Bars
function initializeProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    progressBars.forEach(bar => {
        const targetWidth = bar.getAttribute('aria-valuenow');
        bar.style.width = '0%';
        setTimeout(() => {
            bar.style.width = targetWidth + '%';
        }, 500);
    });
}

// Loading Overlay
function showLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.remove('d-none');
    } else {
        // Create loading overlay
        const overlayHtml = `
            <div id="loadingOverlay" class="position-fixed top-0 start-0 w-100 h-100 d-flex align-items-center justify-content-center" 
                 style="background: rgba(0,0,0,0.5); z-index: 9999;">
                <div class="text-center text-white">
                    <div class="spinner-border mb-3" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <div>Processing...</div>
                </div>
            </div>
        `;
        document.body.insertAdjacentHTML('beforeend', overlayHtml);
    }
}

function hideLoadingOverlay() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) {
        overlay.classList.add('d-none');
    }
}

// Utility Functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + U for upload page
    if ((e.ctrlKey || e.metaKey) && e.key === 'u') {
        e.preventDefault();
        if (window.location.pathname !== '/upload') {
            window.location.href = '/upload';
        }
    }
    
    // Escape to close modals/overlays
    if (e.key === 'Escape') {
        hideLoadingOverlay();
    }
});

// Smooth scrolling for anchor links
document.addEventListener('click', function(e) {
    if (e.target.matches('a[href^="#"]')) {
        e.preventDefault();
        const target = document.querySelector(e.target.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    }
});

// Service Worker Registration (for PWA capabilities)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', function() {
        navigator.serviceWorker.register('/sw.js')
            .then(function(registration) {
                console.log('ServiceWorker registration successful');
            })
            .catch(function(error) {
                console.log('ServiceWorker registration failed');
            });
    });
}