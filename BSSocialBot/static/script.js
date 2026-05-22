// Chat functionality
document.addEventListener('DOMContentLoaded', function() {
    const chatContainer = document.getElementById('chatContainer');
    const userInput = document.getElementById('userInput');
    const sendBtn = document.getElementById('sendBtn');
    const resetBtn = document.getElementById('resetBtn');

    // Create typing indicator
    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.innerHTML = `
        <div class="d-flex align-items-start">
            <div class="avatar bg-primary rounded-circle me-3 flex-shrink-0">
                <i class="fas fa-robot text-white"></i>
            </div>
            <div class="typing-dots">
                <span></span>
                <span></span>
                <span></span>
            </div>
        </div>
    `;

    // Send message function
    function sendMessage() {
        const message = userInput.value.trim();
        if (!message) return;

        // Add user message to chat
        addMessage(message, 'user');
        userInput.value = '';
        userInput.disabled = true;
        sendBtn.disabled = true;

        // Show typing indicator
        showTypingIndicator();

        // Send to backend
        fetch('/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ message: message })
        })
        .then(response => response.json())
        .then(data => {
            hideTypingIndicator();
            addMessage(data.reply, 'bot');
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        })
        .catch(error => {
            hideTypingIndicator();
            console.error('Error:', error);
            addMessage('Sorry, there was an error processing your request. Please try again.', 'bot');
            userInput.disabled = false;
            sendBtn.disabled = false;
            userInput.focus();
        });
    }

    // Add message to chat
    function addMessage(text, sender) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${sender}-message`;
        
        if (sender === 'user') {
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="d-flex align-items-start">
                        <div class="message-text">${escapeHtml(text)}</div>
                        <div class="avatar bg-success rounded-circle ms-3 flex-shrink-0">
                            <i class="fas fa-user text-white"></i>
                        </div>
                    </div>
                </div>
            `;
        } else {
            // Format bot message with proper styling
            const formattedText = formatBotMessage(text);
            messageDiv.innerHTML = `
                <div class="message-content">
                    <div class="d-flex align-items-start">
                        <div class="avatar bg-primary rounded-circle me-3 flex-shrink-0">
                            <i class="fas fa-robot text-white"></i>
                        </div>
                        <div class="message-text">${formattedText}</div>
                    </div>
                </div>
            `;
        }

        chatContainer.appendChild(messageDiv);
        scrollToBottom();
    }

    // Format bot messages with proper styling
    function formatBotMessage(text) {
        // Escape HTML first
        text = escapeHtml(text);
        
        // Convert markdown-style formatting
        text = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        // Style status indicators
        text = text.replace(/✅/g, '<span class="status-success">✅</span>');
        text = text.replace(/❌/g, '<span class="status-error">❌</span>');
        text = text.replace(/⚠️/g, '<span class="status-warning">⚠️</span>');
        text = text.replace(/⏳/g, '<span class="text-info">⏳</span>');
        text = text.replace(/🎓|🔬|🌍|📋|📚|📝|ℹ️|🔄|🎉/g, '<span class="text-primary">$&</span>');
        
        // Style course codes (CMSC, MATH, STAT, AMSC followed by numbers)
        text = text.replace(/\b(CMSC|MATH|STAT|AMSC)\d{3}[A-Z]*\b/g, '<span class="course-code">$&</span>');
        
        // Convert newlines to HTML breaks
        text = text.replace(/\n/g, '<br>');
        
        return text;
    }

    // Show typing indicator
    function showTypingIndicator() {
        typingIndicator.style.display = 'block';
        chatContainer.appendChild(typingIndicator);
        scrollToBottom();
    }

    // Hide typing indicator
    function hideTypingIndicator() {
        typingIndicator.style.display = 'none';
        if (typingIndicator.parentNode) {
            typingIndicator.parentNode.removeChild(typingIndicator);
        }
    }

    // Scroll to bottom of chat
    function scrollToBottom() {
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    // Escape HTML to prevent XSS
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    // Reset conversation
    function resetConversation() {
        fetch('/reset', {
            method: 'POST'
        })
        .then(() => {
            // Clear chat and reload page
            location.reload();
        })
        .catch(error => {
            console.error('Reset error:', error);
            location.reload(); // Fallback to page reload
        });
    }

    // Event listeners
    sendBtn.addEventListener('click', sendMessage);
    resetBtn.addEventListener('click', resetConversation);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });

    // Focus input on load
    userInput.focus();
});
