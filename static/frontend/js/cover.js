/**
 * cover.js - Cover Letter Generator JavaScript
 * Place this in static/frontend/js/cover.js
 */

// Get CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

// Chat form submission
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('coverChatForm');
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const input = chatForm.querySelector('input[name="chat_input"]');
            const userMessage = input.value.trim();
            
            if (!userMessage) return;
            
            // Get user initials
            const userAvatar = document.querySelector('.dash-user .avatar');
            const userInitials = userAvatar ? userAvatar.textContent : 'YOU';
            
            // Add user message to chat
            appendMessage(userInitials, userMessage, true);
            
            // Clear input
            input.value = '';
            
            // Disable input while processing
            input.disabled = true;
            const submitBtn = chatForm.querySelector('button[type="submit"]');
            const originalHTML = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split"></i>';
            submitBtn.disabled = true;
            
            // Show typing indicator
            showTypingIndicator();
            
            // Send to backend
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `chat_input=${encodeURIComponent(userMessage)}`
            })
            .then(response => response.json())
            .then(data => {
                hideTypingIndicator();
                if (data.success) {
                    appendMessage('AI', data.response, false);
                    
                    // Update progress if provided
                    if (data.progress) {
                        updateProgress(data.progress);
                    }
                } else {
                    appendMessage('AI', data.error || 'Sorry, something went wrong.', false);
                }
            })
            .catch(error => {
                console.error('Error:', error);
                hideTypingIndicator();
                appendMessage('AI', 'Sorry, I encountered an error. Please try again.', false);
            })
            .finally(() => {
                input.disabled = false;
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalHTML;
                input.focus();
            });
        });
    }
    
    // Export form
    const exportForm = document.getElementById('exportForm');
    if (exportForm) {
        exportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(exportForm);
            const exportType = formData.get('export');
            
            const submitBtn = exportForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.innerHTML;
            submitBtn.innerHTML = '<i class="bi bi-hourglass-split me-2"></i>Exporting...';
            submitBtn.disabled = true;
            
            fetch(window.location.href, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': csrftoken,
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: `export=${exportType}`
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert(`Your cover letter is ready for download as ${exportType.toUpperCase()}!`);
                } else {
                    alert('Export failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Export error:', error);
                alert('Export failed. Please try again.');
            })
            .finally(() => {
                submitBtn.innerHTML = originalText;
                submitBtn.disabled = false;
            });
        });
    }
    
    // File upload handler
    const fileInput = document.getElementById('resumeUpload');
    if (fileInput) {
        fileInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                // Handle file upload
                uploadResume(file);
            }
        });
    }
    
    // Sidebar toggle
    const sidebarToggle = document.getElementById('sidebar-toggle');
    const sidebar = document.getElementById('sidebar');
    
    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('collapsed');
        });
    }
    
    // Reset conversation button
    const resetBtn = document.getElementById('resetCoverChat');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            if (confirm('Are you sure you want to reset the conversation? All progress will be lost.')) {
                const originalText = resetBtn.innerHTML;
                resetBtn.innerHTML = '<i class="bi bi-hourglass-split me-1"></i>Resetting...';
                resetBtn.disabled = true;
                
                fetch(window.location.href + '?reset=true', {
                    method: 'GET',
                    headers: {
                        'X-Requested-With': 'XMLHttpRequest'
                    }
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        // Reload page to show fresh conversation
                        window.location.reload();
                    } else {
                        alert('Failed to reset. Please try again.');
                        resetBtn.innerHTML = originalText;
                        resetBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Reset error:', error);
                    alert('Failed to reset. Please try again.');
                    resetBtn.innerHTML = originalText;
                    resetBtn.disabled = false;
                });
            }
        });
    }
});

// Append message to chat
function appendMessage(avatar, text, isUser) {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${isUser ? 'user-msg' : 'ai-msg'}`;
    
    const avatarClass = isUser ? 'user-avatar' : 'ai-avatar';
    const bubbleClass = isUser ? 'user-bubble' : 'ai-bubble';
    const displayAvatar = isUser ? avatar : 'AI';
    
    messageDiv.innerHTML = `
        <div class="msg-avatar ${avatarClass}">${displayAvatar}</div>
        <div class="msg-bubble ${bubbleClass}">
            <p class="mb-0">${escapeHtml(text)}</p>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Escape HTML
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Show typing indicator
function showTypingIndicator() {
    const chatMessages = document.getElementById('chatMessages');
    if (!chatMessages) return;
    
    const indicator = document.createElement('div');
    indicator.className = 'chat-message ai-msg';
    indicator.id = 'typing-indicator';
    indicator.innerHTML = `
        <div class="msg-avatar ai-avatar">AI</div>
        <div class="msg-bubble ai-bubble">
            <div class="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;
    chatMessages.appendChild(indicator);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Hide typing indicator
function hideTypingIndicator() {
    const indicator = document.getElementById('typing-indicator');
    if (indicator) {
        indicator.remove();
    }
}

// Update progress indicators
function updateProgress(progress) {
    // Update progress items
    Object.keys(progress).forEach(key => {
        if (key !== 'percentage') {
            const item = document.querySelector(`.progress-item.${key}`);
            if (item && progress[key]) {
                item.classList.add('completed');
                const icon = item.querySelector('i');
                if (icon) {
                    icon.className = 'bi bi-check-circle-fill';
                }
            }
        }
    });
    
    // Update progress bar
    if (progress.percentage !== undefined) {
        const progressBar = document.querySelector('.progress-bar');
        const progressText = document.querySelector('.completion-progress .text-primary');
        
        if (progressBar) {
            progressBar.style.width = `${progress.percentage}%`;
            progressBar.setAttribute('aria-valuenow', progress.percentage);
        }
        
        if (progressText) {
            progressText.textContent = `${progress.percentage}%`;
        }
    }
}

// Upload resume file
function uploadResume(file) {
    const formData = new FormData();
    formData.append('resume_file', file);
    formData.append('csrfmiddlewaretoken', csrftoken);
    
    // Show uploading message
    appendMessage('AI', 'Analyzing your resume...', false);
    
    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            appendMessage('AI', data.message || 'Resume uploaded successfully! Let me help you create a cover letter.', false);
        } else {
            appendMessage('AI', data.error || 'Failed to upload resume. Please try again.', false);
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        appendMessage('AI', 'Failed to upload resume. Please try again.', false);
    });
}