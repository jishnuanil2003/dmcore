document.addEventListener('DOMContentLoaded', () => {
    const triggerBtn = document.getElementById('trigger-btn');
    const statusContainer = document.getElementById('status-container');
    const statusMessage = document.getElementById('status-message');
    const toast = document.getElementById('toast');
    const toastMessage = document.getElementById('toast-message');
    const toastIcon = document.getElementById('toast-icon');
    const toastClose = document.getElementById('toast-close');

    let processing = false;

    // Fun facts/status messages to cycle through
    const processingMessages = [
        "Connecting to mail server...",
        "Scanning for resume attachments...",
        "Applying AI parsing algorithms...",
        "Extracting candidate metadata...",
        "Comparing with Google Forms data...",
        "Syncing results to Google Sheets...",
        "Finalizing pipeline..."
    ];

    let messageInterval;

    function showToast(message, type = 'success') {
        toast.className = `toast ${type} show`;
        toastMessage.textContent = message;
        toastIcon.textContent = type === 'success' ? '✅' : '❌';
        
        setTimeout(() => {
            toast.classList.remove('show');
        }, 5000);
    }

    toastClose.addEventListener('click', () => {
        toast.classList.remove('show');
    });

    triggerBtn.addEventListener('click', async () => {
        if (processing) return;
        
        processing = true;
        triggerBtn.disabled = true;
        triggerBtn.innerHTML = '<span class="btn-text">Processing...</span><span class="btn-icon">⏳</span>';
        
        statusContainer.classList.remove('hidden');
        
        // Cycle messages
        let msgIndex = 0;
        statusMessage.textContent = processingMessages[0];
        messageInterval = setInterval(() => {
            msgIndex = (msgIndex + 1) % processingMessages.length;
            statusMessage.textContent = processingMessages[msgIndex];
        }, 2500);

        try {
            const response = await fetch('/trigger-extraction/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                }
            });

            const data = await response.json();
            
            clearInterval(messageInterval);
            statusContainer.classList.add('hidden');
            triggerBtn.disabled = false;
            triggerBtn.innerHTML = '<span class="btn-text">Start Pipeline</span><span class="btn-icon">⚡</span>';
            processing = false;

            if (response.ok) {
                showToast(data.message || 'Processing completed successfully!', 'success');
            } else {
                showToast(data.message || 'An error occurred during processing.', 'error');
            }
            
        } catch (error) {
            clearInterval(messageInterval);
            statusContainer.classList.add('hidden');
            triggerBtn.disabled = false;
            triggerBtn.innerHTML = '<span class="btn-text">Start Pipeline</span><span class="btn-icon">⚡</span>';
            processing = false;
            
            showToast('Network error or server unreachable.', 'error');
            console.error(error);
        }
    });
});
