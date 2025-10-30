// CryptFyles Custom JavaScript

// Show loading spinner on form submit
document.addEventListener('DOMContentLoaded', function() {
    // Add loading to all forms
    const forms = document.querySelectorAll('form');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(e) {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn && !submitBtn.classList.contains('no-loading')) {
                const originalText = submitBtn.innerHTML;
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<span class="spinner"></span> Loading...';
                
                // Re-enable after 10 seconds (in case of error)
                setTimeout(function() {
                    submitBtn.disabled = false;
                    submitBtn.innerHTML = originalText;
                }, 10000);
            }
        });
    });
    
    // Confirm delete actions
    const deleteLinks = document.querySelectorAll('a[href*="delete"]');
    deleteLinks.forEach(function(link) {
        if (!link.classList.contains('no-confirm')) {
            link.addEventListener('click', function(e) {
                if (!confirm('Are you sure you want to delete this?')) {
                    e.preventDefault();
                }
            });
        }
    });
    
    // File size validation
    const fileInputs = document.querySelectorAll('input[type="file"]');
    fileInputs.forEach(function(input) {
        input.addEventListener('change', function() {
            const maxSize = 10 * 1024 * 1024 * 1024; // 10GB
            if (this.files && this.files.size > maxSize) {
                alert('File too large! Maximum size is 10GB.');
                this.value = '';
            }
        });
    });
});
