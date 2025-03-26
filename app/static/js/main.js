/**
 * Main JavaScript file for handling form submission and user interactions.
 */

document.addEventListener('DOMContentLoaded', () => {
    const urlForm = document.getElementById('urlForm');
    const urlInputs = document.getElementById('urlInputs');
    const addUrlBtn = document.getElementById('addUrlBtn');
    const slideCount = document.getElementById('slideCount');
    const maxUrls = 20;

    // Form validation
    urlInputs.addEventListener('input', validateUrl);
    urlInputs.addEventListener('input', updateSlideCount);

    // Add URL button
    addUrlBtn.addEventListener('click', addUrlInput);

    // Form submission
    urlForm.addEventListener('submit', handleSubmit);
});

/**
 * Validates the URL input field.
 * @param {Event} event - The input event
 */
function validateUrl(event) {
    if (event.target.matches('input[type="url"]')) {
        const url = event.target.value;
        const isValid = isValidUrl(url);
        const preview = event.target.parentElement.querySelector('.url-preview');
        
        if (!isValid && url !== '') {
            event.target.setCustomValidity('Please enter a valid URL');
            preview.classList.remove('loading');
            preview.innerHTML = '';
        } else {
            event.target.setCustomValidity('');
            if (url) {
                updatePreview(url, preview);
            } else {
                preview.classList.remove('loading');
                preview.innerHTML = '';
            }
        }
    }
}

/**
 * Updates the preview for a URL.
 * @param {string} url - The URL to preview
 * @param {HTMLElement} preview - The preview element
 */
async function updatePreview(url, preview) {
    preview.classList.add('loading');
    
    try {
        const response = await fetch(`/api/preview?url=${encodeURIComponent(url)}`);
        if (!response.ok) throw new Error('Failed to fetch preview');
        
        const blob = await response.blob();
        const imageUrl = URL.createObjectURL(blob);
        
        preview.classList.remove('loading');
        preview.innerHTML = `
            <div class="preview-image-container">
                <img src="${imageUrl}" alt="Preview">
                <div class="preview-overlay">
                    <button type="button" class="edit-preview" title="Edit screenshot">
                        <i class="fas fa-pencil-alt"></i>
                    </button>
                </div>
            </div>
        `;

        // Add click handler for edit button
        const editBtn = preview.querySelector('.edit-preview');
        editBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            initializeCropper(imageUrl, preview);
            return false; // Prevent any other handlers from executing
        });
    } catch (error) {
        console.error('Error fetching preview:', error);
        preview.classList.remove('loading');
        preview.innerHTML = '<span class="error">Failed to load preview</span>';
    }
}

/**
 * Checks if a string is a valid URL.
 * @param {string} url - The URL to validate
 * @returns {boolean} - Whether the URL is valid
 */
function isValidUrl(url) {
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * Adds a new URL input field.
 */
function addUrlInput() {
    const urlInputs = document.getElementById('urlInputs');
    const currentCount = urlInputs.children.length;
    
    if (currentCount >= 20) {
        alert('Maximum number of URLs reached (20)');
        return;
    }
    
    const newGroup = document.createElement('div');
    newGroup.className = 'url-input-group';
    newGroup.innerHTML = `
        <div class="form-group">
            <label for="url-${currentCount + 1}">URL ${currentCount + 1}:</label>
            <div class="url-input-container">
                <input 
                    type="url" 
                    id="url-${currentCount + 1}"
                    name="urls[]" 
                    placeholder="https://example.com"
                    required
                    class="form-input"
                >
                <div class="url-preview" id="preview-${currentCount + 1}"></div>
            </div>
        </div>
        <button type="button" class="remove-url" aria-label="Remove URL">×</button>
    `;
    
    urlInputs.appendChild(newGroup);
    
    // Add remove button handler
    const removeBtn = newGroup.querySelector('.remove-url');
    removeBtn.addEventListener('click', () => {
        newGroup.remove();
        updateSlideCount();
    });
}

/**
 * Updates the slide count display.
 */
function updateSlideCount() {
    const slideCount = document.getElementById('slideCount');
    const urlCount = document.querySelectorAll('.url-input-group').length;
    slideCount.textContent = urlCount;
}

/**
 * Handles the form submission.
 * @param {Event} event - The submit event
 */
async function handleSubmit(event) {
    event.preventDefault();
    
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Disable submit button and show loading state
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Generating...';
    
    try {
        // Get all URL inputs and their associated previews
        const urlGroups = form.querySelectorAll('.url-input-group');
        const formData = new FormData();
        
        // Add each URL and its cropped image (if any) to the form data
        urlGroups.forEach((group, index) => {
            const input = group.querySelector('input[type="url"]');
            const preview = group.querySelector('.url-preview');
            
            if (input.value) {
                formData.append('urls', input.value);
                
                // If there's a cropped image, add it to form data
                if (preview.dataset.croppedImage) {
                    // Convert base64 to blob
                    const imageData = preview.dataset.croppedImage.split(',')[1];
                    const blob = base64ToBlob(imageData, 'image/png');
                    formData.append(`cropped_images`, blob, `screenshot_${index}.png`);
                }
            }
        });
        
        const response = await fetch('/api/generate', {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Failed to generate presentation');
        }
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'presentation.pptx';
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
        
        // Show success message
        showNotification('Presentation generated successfully!', 'success');
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to generate presentation. Please try again.', 'error');
    } finally {
        // Reset submit button
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-file-powerpoint"></i> Generate Presentation';
    }
}

/**
 * Converts a base64 string to a Blob object.
 * @param {string} base64 - The base64 string
 * @param {string} type - The mime type
 * @returns {Blob} - The blob object
 */
function base64ToBlob(base64, type) {
    const binaryString = window.atob(base64);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
        bytes[i] = binaryString.charCodeAt(i);
    }
    return new Blob([bytes], { type: type });
}

/**
 * Shows a notification message to the user.
 * @param {string} message - The message to display
 * @param {string} type - The type of notification ('success' or 'error')
 */
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Trigger reflow
    notification.offsetHeight;
    
    // Add show class for animation
    notification.classList.add('show');
    
    // Remove notification after 3 seconds
    setTimeout(() => {
        notification.classList.remove('show');
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

let currentCropper = null;
let activePreviewElement = null;

function initializeCropper(imageUrl, previewElement) {
    const modal = document.getElementById('cropperModal');
    const cropperImage = document.getElementById('cropperImage');
    const closeBtn = document.querySelector('.close-modal');
    const cropDoneBtn = document.getElementById('cropDone');
    const rotateLeftBtn = document.getElementById('rotateLeft');
    const rotateRightBtn = document.getElementById('rotateRight');

    // Only prevent form submission events on the modal
    modal.addEventListener('submit', (e) => {
        e.preventDefault();
        e.stopPropagation();
        return false;
    }, true);

    // Set the image source and show modal
    cropperImage.src = imageUrl;
    modal.classList.add('show');
    activePreviewElement = previewElement;

    // Initialize Cropper.js
    cropperImage.onload = function() {
        if (currentCropper) {
            currentCropper.destroy();
        }
        currentCropper = new Cropper(cropperImage, {
            aspectRatio: NaN,
            viewMode: 2,
            background: false,
            autoCropArea: 1,
            movable: true,
            scalable: true,
            zoomable: true,
            rotatable: true,
            responsive: true,
            guides: true,
            center: true,
            highlight: true,
            cropBoxMovable: true,
            cropBoxResizable: true,
            toggleDragModeOnDblclick: true
        });
    };

    // Handle rotation
    rotateLeftBtn.onclick = (e) => {
        e.preventDefault();
        currentCropper.rotate(-90);
    };

    rotateRightBtn.onclick = (e) => {
        e.preventDefault();
        currentCropper.rotate(90);
    };

    // Handle crop completion
    cropDoneBtn.onclick = (e) => {
        e.preventDefault();
        
        const canvas = currentCropper.getCroppedCanvas({
            maxWidth: 4096,
            maxHeight: 4096,
            fillColor: '#fff',
            imageSmoothingEnabled: true,
            imageSmoothingQuality: 'high'
        });
        
        const croppedImageUrl = canvas.toDataURL('image/png');
        
        // Update the preview image
        const previewImg = activePreviewElement.querySelector('img');
        previewImg.src = croppedImageUrl;
        
        // Store the cropped image data for form submission
        activePreviewElement.dataset.croppedImage = croppedImageUrl;
        
        // Close modal
        closeModal();
    };

    // Handle modal close
    closeBtn.onclick = (e) => {
        e.preventDefault();
        closeModal();
    };
    
    // Handle clicking outside the modal
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            e.preventDefault();
            closeModal();
        }
    });
}

function closeModal(e) {
    if (e) {
        e.preventDefault();
    }
    const modal = document.getElementById('cropperModal');
    modal.classList.remove('show');
    if (currentCropper) {
        currentCropper.destroy();
        currentCropper = null;
    }
} 