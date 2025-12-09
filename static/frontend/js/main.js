// === Desktop Sidebar collapse ===
document.getElementById('sidebar-toggle').onclick = function () {
  document.getElementById('sidebar').classList.toggle('collapsed');
};

// === Responsive Hamburger/Menu Logic ===
function toggleMenu(showMenu) {
  const layout = document.querySelector('.dashboard-layout');
  if (showMenu) {
    layout.classList.add('show-menu');
    layout.classList.remove('show-content');
  } else {
    layout.classList.remove('show-menu');
    layout.classList.add('show-content');
  }
}

function addMobileMenuBtn() {
  // Remove all previous buttons to avoid duplication on resize
  document.querySelectorAll('.mobile-menu-btn').forEach(btn => btn.remove());
  // Create a floating menu icon (bootstrap icon)
  let btn = document.createElement('button');
  btn.innerHTML = `<i class="bi bi-list"></i>`;
  btn.className = 'mobile-menu-btn';
  btn.type = 'button';
  btn.setAttribute('aria-label', 'Open menu');
  btn.style = `
    position: fixed;
    top: 22px; left: 22px;
    z-index: 3000;
    background: var(--primary-blue);
    color: #fff;
    border-radius: 7px;
    border: none;
    padding: 7px 12px;
    font-size: 1.55rem;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 8px #1547bb22;
    transition: background .13s;
  `;
  btn.onclick = function () {
    // Toggle: if menu visible, switch to content; otherwise show menu
    const layout = document.querySelector('.dashboard-layout');
    if (layout.classList.contains('show-menu')) {
      toggleMenu(false);
    } else {
      toggleMenu(true);
    }
  };
  document.body.appendChild(btn);
}

function mobileInit() {
  if (window.innerWidth < 900) {
    // Start showing just the sidebar (menu view)
    toggleMenu(true);

    addMobileMenuBtn();

    // Clicking any sidebar link shows ONLY main content (hides sidebar)
    document.querySelectorAll('.sidebar-link').forEach(function(link){
      link.addEventListener('click', function(e){
        e.preventDefault();
        toggleMenu(false);
      });
    });
  } else {
    // On desktop: always show everything
    document.querySelector('.dashboard-layout').classList.remove('show-menu', 'show-content');
    document.querySelectorAll('.mobile-menu-btn').forEach(btn => btn.remove());
  }
}

// Run once, and on resize
window.addEventListener('DOMContentLoaded', mobileInit);
window.addEventListener('resize', function() { setTimeout(mobileInit, 110); });

// === Template click => AI chat open (grid-to-chat swap) ===
document.querySelectorAll('.cv-template-img').forEach(function(img){
  img.addEventListener('click', function(){
    document.getElementById('template-picker').classList.add('d-none');
    document.getElementById('ai-chat').classList.remove('d-none');
    document.getElementById('ai-msg-img').src = img.src;
    document.getElementById('ai-msg-img').alt = img.alt;
  });
});


// Sidebar collapse (desktop)
document.getElementById('sidebar-toggle').onclick = function () {
  document.getElementById('sidebar').classList.toggle('collapsed');
};

// Shows AI chat when template clicked
document.querySelectorAll('.cv-template-img').forEach(function(img){
  img.addEventListener('click', function(){
    document.getElementById('template-picker').classList.add('d-none');
    document.getElementById('ai-chat').classList.remove('d-none');
    document.getElementById('ai-msg-img').src = img.src;
    document.getElementById('ai-msg-img').alt = img.alt;
  });
});

// Responsive helper to set sidebar always collapsed, no extra menu button
function mobileSidebarInit() {
  const sidebar = document.getElementById('sidebar');
  const layout = document.querySelector('.dashboard-layout');
  if (window.innerWidth < 900) {
    sidebar.classList.add('collapsed');
    document.querySelector('.progress-nav').style.display = 'none';
    sidebar.style.display = 'flex';
    document.querySelector('.dash-main').style.width = "calc(100vw - 66px)";
    document.querySelector('.dash-main').style.marginLeft = "66px";
  } else {
    sidebar.classList.remove('collapsed');
    document.querySelector('.progress-nav').style.display = '';
    sidebar.style.display = '';
    document.querySelector('.dash-main').style.width = "";
    document.querySelector('.dash-main').style.marginLeft = "";
  }
}

window.addEventListener('DOMContentLoaded', mobileSidebarInit);
window.addEventListener('resize', function() { setTimeout(mobileSidebarInit, 100); });



/**
 * main.js - Complete Frontend JavaScript for AI Resume Builder
 * Place this in your static/frontend/js/ directory
 */

// Get CSRF token for Django POST requests
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

// Template selection handler
function selectTemplate(templateId) {
    console.log('Template selected:', templateId);
    
    // Send template selection to backend
    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `template_id=${templateId}`
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            // Hide template picker, show chat
            document.getElementById('template-picker').classList.add('d-none');
            document.getElementById('ai-chat').classList.remove('d-none');
            
            console.log('Template selected successfully');
        }
    })
    .catch(error => {
        console.error('Error selecting template:', error);
        // Still show the chat even if backend fails
        document.getElementById('template-picker').classList.add('d-none');
        document.getElementById('ai-chat').classList.remove('d-none');
    });
}

// Action button handler (Improve Resume / Start Fresh)
function chooseAction(action) {
    console.log('Action chosen:', action);
    
    // Disable action buttons
    const actionButtons = document.querySelectorAll('.msg-actions button');
    actionButtons.forEach(btn => btn.disabled = true);
    
    // Show typing indicator
    showTypingIndicator();
    
    // Send action to backend
    fetch(window.location.href, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-CSRFToken': csrftoken,
            'X-Requested-With': 'XMLHttpRequest'
        },
        body: `action=${action}`
    })
    .then(response => response.json())
    .then(data => {
        hideTypingIndicator();
        
        if (data.success) {
            // Add AI response to chat
            appendMessage(data.avatar, data.response, false);
            
            // Remove the action buttons after use
            actionButtons.forEach(btn => btn.closest('.msg-actions').remove());
        } else {
            alert(data.error || 'Something went wrong. Please try again.');
            actionButtons.forEach(btn => btn.disabled = false);
        }
    })
    .catch(error => {
        console.error('Error:', error);
        hideTypingIndicator();
        alert('Failed to process your choice. Please try again.');
        actionButtons.forEach(btn => btn.disabled = false);
    });
}

// Chat form submission handler
document.addEventListener('DOMContentLoaded', function() {
    const chatForm = document.getElementById('chatForm');
    
    if (chatForm) {
        chatForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const input = chatForm.querySelector('input[name="chat_input"]');
            const userMessage = input.value.trim();
            
            if (!userMessage) return;
            
            // Get user initials from avatar
            const userAvatar = document.querySelector('.dash-user .avatar');
            const userInitials = userAvatar ? userAvatar.textContent : 'YOU';
            
            // Add user message to chat immediately
            appendMessage(userInitials, userMessage, true);
            
            // Clear input
            input.value = '';
            
            // Disable input while processing
            input.disabled = true;
            const submitBtn = chatForm.querySelector('button[type="submit"]');
            const originalSubmitHTML = submitBtn.innerHTML;
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
                    // Add AI response
                    appendMessage(data.avatar, data.response, false);
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
                // Re-enable input
                input.disabled = false;
                submitBtn.disabled = false;
                submitBtn.innerHTML = originalSubmitHTML;
                input.focus();
            });
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
});

// Helper function to append messages to chat
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
    
    // Scroll to bottom
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

// Helper function to escape HTML
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

// Export functionality
document.addEventListener('DOMContentLoaded', function() {
    const exportForm = document.querySelector('.export-section form');
    
    if (exportForm) {
        exportForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const formData = new FormData(exportForm);
            const exportType = formData.get('export');
            
            const submitBtn = exportForm.querySelector('button[type="submit"]');
            const originalText = submitBtn.textContent;
            submitBtn.textContent = 'Exporting...';
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
                    alert(`Your resume is being exported as ${exportType.toUpperCase()}!`);
                    // TODO: Handle actual file download
                } else {
                    alert('Export failed. Please try again.');
                }
            })
            .catch(error => {
                console.error('Export error:', error);
                alert('Export failed. Please try again.');
            })
            .finally(() => {
                submitBtn.textContent = originalText;
                submitBtn.disabled = false;
            });
        });
    }
});



// Add to your existing script or create new function
function resetConversation() {
    if (confirm("Are you sure you want to start over? All progress will be lost.")) {
        fetch("{% url 'resumecreate:reset_conversation' %}", {
            method: "POST",
            headers: {
                "X-CSRFToken": getCookie("csrftoken"),
                "Content-Type": "application/json",
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        });
    }
}

function exportResume() {
    const format = document.querySelector('input[name="export-format"]:checked').id;
    alert(`Exporting as ${format.toUpperCase()}... This feature will be implemented soon!`);
}

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

// Auto-scroll to latest message
function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    if (chatMessages) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

// Call on page load and after message submission
document.addEventListener('DOMContentLoaded', scrollToBottom);