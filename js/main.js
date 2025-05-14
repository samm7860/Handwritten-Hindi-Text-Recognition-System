// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Add animations to elements
    animateElements();
    
    // Preview image before upload
    const imageInput = document.getElementById('image');
    if (imageInput) {
        imageInput.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                // Check file type
                const fileType = file.type;
                if (!fileType.match('image/jpeg') && !fileType.match('image/png')) {
                    showAlert('Please select a valid image file (JPEG or PNG).', 'danger');
                    this.value = '';
                    return;
                }
                
                // Check file size (max 5MB)
                if (file.size > 5 * 1024 * 1024) {
                    showAlert('File size exceeds 5MB. Please choose a smaller image.', 'danger');
                    this.value = '';
                    return;
                }
                
                // Show preview of the image
                const reader = new FileReader();
                reader.onload = function(e) {
                    let previewDiv = document.getElementById('imagePreview');
                    
                    // Create preview div if it doesn't exist
                    if (!previewDiv) {
                        previewDiv = document.createElement('div');
                        previewDiv.id = 'imagePreview';
                        previewDiv.className = 'mt-3 text-center';
                        imageInput.parentNode.appendChild(previewDiv);
                    }
                    
                    // Clear previous preview
                    previewDiv.innerHTML = '';
                    
                    // Add new preview
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'img-fluid preview-image mb-2';
                    img.style.maxHeight = '200px';
                    img.alt = 'Image preview';
                    
                    const caption = document.createElement('p');
                    caption.className = 'text-muted';
                    caption.textContent = 'Preview: ' + file.name;
                    
                    previewDiv.appendChild(img);
                    previewDiv.appendChild(caption);
                };
                reader.readAsDataURL(file);
            }
        });
    }
    
    // Toggle handwritten mode settings
    const handwrittenSwitch = document.getElementById('handwritten');
    if (handwrittenSwitch) {
        handwrittenSwitch.addEventListener('change', function() {
            updateHandwrittenModeSettings(this.checked);
        });
        
        // Initialize settings based on the current state
        updateHandwrittenModeSettings(handwrittenSwitch.checked);
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-info)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation for image upload
    const recognizeForm = document.querySelector('form');
    if (recognizeForm) {
        recognizeForm.addEventListener('submit', function(event) {
            if (!imageInput.files.length) {
                event.preventDefault();
                showAlert('Please select an image to upload', 'danger');
            }
        });
    }
});

// Helper function to show alerts
function showAlert(message, type = 'info') {
    const alertsContainer = document.createElement('div');
    alertsContainer.className = 'alert-container';
    alertsContainer.style.position = 'fixed';
    alertsContainer.style.top = '20px';
    alertsContainer.style.right = '20px';
    alertsContainer.style.zIndex = '9999';
    
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    alertsContainer.appendChild(alert);
    document.body.appendChild(alertsContainer);
    
    // Auto-dismiss after 5 seconds
    setTimeout(() => {
        alert.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(alertsContainer);
        }, 300);
    }, 5000);
}

// Update settings based on handwritten mode
function updateHandwrittenModeSettings(isHandwritten) {
    // Get elements
    const threshAdaptive = document.getElementById('threshAdaptive');
    const threshNone = document.getElementById('threshNone');
    const denoise = document.getElementById('denoise');
    const contrast = document.getElementById('contrast');
    const morphology = document.getElementById('morphology');
    
    if (isHandwritten) {
        // Set recommended settings for handwritten text
        if (threshAdaptive) threshAdaptive.checked = true;
        if (denoise) denoise.checked = true;
        if (contrast) contrast.checked = true;
        if (morphology) morphology.value = 'dilate';
        
        // Show handwritten mode tips
        showHandwrittenTips(true);
    } else {
        // Set recommended settings for printed text
        if (threshNone) threshNone.checked = true;
        if (denoise) denoise.checked = false;
        if (contrast) contrast.checked = false;
        if (morphology) morphology.value = 'none';
        
        // Hide handwritten mode tips
        showHandwrittenTips(false);
    }
}

// Show/hide handwritten tips
function showHandwrittenTips(show) {
    const tipsDiv = document.getElementById('handwrittenTips');
    if (!tipsDiv) return;
    
    if (show) {
        tipsDiv.style.display = 'block';
    } else {
        tipsDiv.style.display = 'none';
    }
}

// Add entrance animations to elements
function animateElements() {
    const elements = document.querySelectorAll('.card, .alert, .btn-primary');
    
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        
        setTimeout(() => {
            element.style.transition = 'opacity 0.8s ease-out, transform 0.8s ease-out';
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, 100 * index);
    });
}