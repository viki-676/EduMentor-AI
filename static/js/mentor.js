// EduMentor AI - Advanced Interactive AI Mentor Client
document.addEventListener('DOMContentLoaded', function () {
    const chatForm = document.getElementById('mentorChatForm');
    const chatInput = document.getElementById('mentorChatInput');
    const chatWindow = document.getElementById('mentorChatWindow');
    const sendBtn = document.getElementById('sendBtn');
    const promptPills = document.querySelectorAll('.prompt-pill');
    const activeConvIdInput = document.getElementById('activeConvId');
    const newChatTopBtn = document.getElementById('newChatTopBtn');
    const newChatSidebarBtn = document.getElementById('newChatSidebarBtn');
    const clearChatBtn = document.getElementById('clearActiveChatBtn');
    const levelRadios = document.querySelectorAll('input[name="explanationLevel"]');
    const levelHelp = document.getElementById('levelHelpText');
    const charCountElem = document.getElementById('charCount');

    if (!chatForm || !chatInput || !chatWindow) return;

    // Helper: explanation level description text
    const levelDescriptions = {
        'beginner': 'Beginner: Simple mental models, intuitive analogies & clear code.',
        'intermediate': 'Intermediate: Standard technical depth, edge cases & algorithmic complexity.',
        'advanced': 'Advanced: In-depth system tradeoffs, architectural choices & formal proofs.'
    };

    levelRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (levelHelp && levelDescriptions[this.value]) {
                levelHelp.textContent = levelDescriptions[this.value];
            }
        });
    });

    function getSelectedLevel() {
        const checked = document.querySelector('input[name="explanationLevel"]:checked');
        return checked ? checked.value : 'beginner';
    }

    // Auto-resize multiline textarea
    function adjustTextareaHeight() {
        chatInput.style.height = 'auto';
        const newHeight = Math.min(chatInput.scrollHeight, 160);
        chatInput.style.height = (newHeight > 46 ? newHeight : 46) + 'px';
        if (charCountElem) {
            const len = chatInput.value.length;
            charCountElem.textContent = len > 0 ? `${len} chars` : '';
        }
    }

    chatInput.addEventListener('input', adjustTextareaHeight);

    // Keyboard navigation: Enter submits, Shift+Enter adds new line
    chatInput.addEventListener('keydown', function (e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (!sendBtn || !sendBtn.disabled) {
                chatForm.dispatchEvent(new Event('submit', { cancelable: true }));
            }
        }
    });

    let userScrolledUp = false;

    // Detect when the user manually scrolls up to read older messages
    chatWindow.addEventListener('scroll', function () {
        const distanceFromBottom = chatWindow.scrollHeight - chatWindow.scrollTop - chatWindow.clientHeight;
        userScrolledUp = distanceFromBottom > 80;
    });

    function scrollToBottom(force = false) {
        if (!chatWindow) return;
        // Preserve scroll position if user is reading older messages
        if (!force && userScrolledUp) return;

        const performScroll = () => {
            if (!force && userScrolledUp) return;
            const target = chatWindow.scrollHeight;
            if (typeof chatWindow.scrollTo === 'function') {
                chatWindow.scrollTo({ top: target, behavior: 'smooth' });
            } else {
                chatWindow.scrollTop = target;
            }
        };

        performScroll();

        // Ensure complete scroll after long content, headings, lists, and code blocks reflow
        if (window.requestAnimationFrame) {
            requestAnimationFrame(() => {
                performScroll();
                setTimeout(performScroll, 60);
                setTimeout(performScroll, 180);
            });
        } else {
            setTimeout(performScroll, 60);
            setTimeout(performScroll, 180);
        }
    }

    // Copy to clipboard helper
    window.copyCodeBlock = function (btn) {
        const pre = btn.closest('.code-container').querySelector('code');
        if (pre) {
            navigator.clipboard.writeText(pre.innerText).then(() => {
                const original = btn.innerHTML;
                btn.innerHTML = '<i class="bi bi-check2"></i> Copied!';
                setTimeout(() => { btn.innerHTML = original; }, 2000);
            });
        }
    };

    // Open Save to Note modal helper
    window.openSaveNoteModal = function (snippetText) {
        const titleField = document.getElementById('saveNoteTitle');
        const contentField = document.getElementById('saveNoteContent');
        if (contentField) {
            contentField.value = snippetText;
        }
        const modalElem = document.getElementById('saveMentorNoteModal');
        if (modalElem) {
            const modal = new bootstrap.Modal(modalElem);
            modal.show();
        }
    };

    function parseMarkdown(text) {
        if (!text) return '';

        // Protect code blocks before replacing newlines
        const codeBlocks = [];
        let placeholderText = text.replace(/```([a-zA-Z0-9_+-]+)?\s*([\s\S]*?)```/g, function (match, lang, code) {
            const index = codeBlocks.length;
            const displayLang = (lang || 'code').toUpperCase();
            const cleanCode = code.trim()
                .replace(/&/g, '&amp;')
                .replace(/</g, '&lt;')
                .replace(/>/g, '&gt;');
            const html = `
                <div class="code-container my-3 rounded-3 overflow-hidden border border-secondary shadow-sm">
                    <div class="d-flex justify-content-between align-items-center bg-dark text-light px-3 py-1.5 font-monospace small" style="background-color: #0f172a !important;">
                        <span class="badge bg-secondary-subtle text-light small">${displayLang}</span>
                        <button type="button" class="btn btn-sm btn-outline-light py-0 px-2" style="font-size: 0.75rem;" onclick="copyCodeBlock(this)">
                            <i class="bi bi-clipboard"></i> Copy
                        </button>
                    </div>
                    <pre class="bg-dark text-light p-3 m-0 overflow-x-auto"><code class="language-${lang || 'plaintext'}">${cleanCode}</code></pre>
                </div>
            `;
            codeBlocks.push(html);
            return `@@CODE_BLOCK_${index}@@`;
        });

        // Headers
        let formatted = placeholderText
            .replace(/^### (.*$)/gim, '<h6 class="fw-bold mentor-heading-3 mb-2 mt-2">$1</h6>')
            .replace(/^## (.*$)/gim, '<h5 class="fw-bold mentor-heading-2 mb-2 mt-2">$1</h5>')
            .replace(/^# (.*$)/gim, '<h4 class="fw-bold mentor-heading-1 mb-2 mt-2">$1</h4>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/\[(.*?)\]\((https?:\/\/.*?)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer" class="text-teal text-decoration-underline fw-semibold">$1 <i class="bi bi-box-arrow-up-right small"></i></a>');

        // Inline code
        formatted = formatted.replace(/`([^`]+)`/g, '<code class="mentor-inline-code px-2 py-0.5 rounded fw-semibold">$1</code>');

        // Lists
        formatted = formatted.replace(/^- (.*$)/gim, '<div class="d-flex align-items-start gap-2 mb-1"><i class="bi bi-check2 text-teal mt-1"></i><span>$1</span></div>');

        // Line breaks
        formatted = formatted.replace(/\n\n/g, '<br><br>').replace(/\n/g, '<br>');

        // Restore code blocks
        codeBlocks.forEach((html, i) => {
            formatted = formatted.replace(`@@CODE_BLOCK_${i}@@`, html);
        });

        return formatted;
    }

    function appendMessage(text, sender, isRawHtml = false) {
        const bubble = document.createElement('div');
        bubble.className = `chat-bubble ${sender === 'user' ? 'bubble-user mb-3 align-self-end' : 'bubble-mentor mb-3 align-self-start'}`;

        if (sender === 'user') {
            bubble.textContent = text;
        } else {
            const bodyDiv = document.createElement('div');
            bodyDiv.className = 'message-content';
            bodyDiv.innerHTML = isRawHtml ? text : parseMarkdown(text);
            bubble.appendChild(bodyDiv);

            // Action footer for mentor message
            const footer = document.createElement('div');
            footer.className = 'd-flex justify-content-end align-items-center gap-2 mt-2 pt-2 mentor-bubble-footer small';
            footer.innerHTML = `
                <button type="button" class="btn btn-link p-0 text-decoration-none small save-note-trigger">
                    <i class="bi bi-journal-plus me-1 text-teal"></i> Save to Notes
                </button>
            `;
            const cleanSnippet = text.replace(/<[^>]*>?/gm, '').substring(0, 300);
            footer.querySelector('.save-note-trigger').addEventListener('click', function () {
                window.openSaveNoteModal(cleanSnippet);
            });
            bubble.appendChild(footer);
        }

        chatWindow.appendChild(bubble);
        scrollToBottom(sender === 'user');
        return bubble;
    }

    // Render markdown for server-rendered mentor messages from chat history
    document.querySelectorAll('.bubble-mentor .message-content').forEach(elem => {
        if (!elem.dataset.rendered) {
            const raw = elem.textContent || elem.innerText || '';
            if (raw.trim()) {
                elem.innerHTML = parseMarkdown(raw);
                elem.dataset.rendered = "true";
            }
        }
    });

    // Attach listener to any server-rendered save-to-notebook buttons
    document.querySelectorAll('.save-to-notebook-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            const text = this.dataset.text || '';
            window.openSaveNoteModal(text);
        });
    });

    async function sendMessage(messageText) {
        if (!messageText || !messageText.trim()) return;

        // Reset scroll lock since user explicitly submitted a new message
        userScrolledUp = false;
        appendMessage(messageText.trim(), 'user');
        chatInput.value = '';
        adjustTextareaHeight();

        if (sendBtn) {
            sendBtn.disabled = true;
            sendBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1" role="status" aria-hidden="true"></span><span>Thinking...</span>';
        }
        chatInput.disabled = true;

        // Add animated loading placeholder
        const loadingBubble = document.createElement('div');
        loadingBubble.className = 'chat-bubble bubble-mentor mb-3 align-self-start d-flex align-items-center gap-2 shadow-sm border border-light';
        loadingBubble.innerHTML = `
            <span class="spinner-grow spinner-grow-sm text-teal" role="status" aria-hidden="true"></span>
            <span class="text-secondary small fw-medium">EduMentor is synthesizing explanation &amp; verified code...</span>
        `;
        chatWindow.appendChild(loadingBubble);
        scrollToBottom(true);

        const currentConvId = activeConvIdInput ? activeConvIdInput.value : null;
        const currentLevel = getSelectedLevel();

        try {
            const response = await fetch('/api/mentor/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify({
                    message: messageText.trim(),
                    level: currentLevel,
                    conversation_id: currentConvId ? parseInt(currentConvId) : null
                })
            });

            if (chatWindow.contains(loadingBubble)) {
                chatWindow.removeChild(loadingBubble);
            }

            if (response.status === 401) {
                appendMessage("🔒 Please log in to chat with AI Mentor. <a href='/login' class='text-teal fw-bold'>Log in here</a>.", 'mentor', true);
                return;
            }

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            if (data.conversation_id && activeConvIdInput && !activeConvIdInput.value) {
                activeConvIdInput.value = data.conversation_id;
            }

            appendMessage(data.response || "I could not retrieve an answer at this time. Please try another query.", 'mentor');
        } catch (err) {
            if (chatWindow.contains(loadingBubble)) {
                chatWindow.removeChild(loadingBubble);
            }
            appendMessage("⚠️ Connection error with AI Mentor service. Please check your network connection or ensure Ollama is running.", 'mentor');
        } finally {
            if (sendBtn) {
                sendBtn.disabled = false;
                sendBtn.innerHTML = '<i class="bi bi-send-fill me-1"></i> <span>Send</span>';
            }
            chatInput.disabled = false;
            adjustTextareaHeight();
            chatInput.focus({ preventScroll: true });
            if (!userScrolledUp) {
                scrollToBottom(false);
            }
        }
    }

    chatForm.addEventListener('submit', function (e) {
        e.preventDefault();
        sendMessage(chatInput.value);
    });

    promptPills.forEach(pill => {
        pill.addEventListener('click', function () {
            const prompt = this.dataset.prompt || this.textContent.trim();
            sendMessage(prompt);
        });
    });

    // New Chat handler
    async function handleNewChat() {
        try {
            const res = await fetch('/api/mentor/new', { method: 'POST' });
            const data = await res.json();
            if (data.conversation_id) {
                window.location.href = `/mentor?c=${data.conversation_id}`;
            }
        } catch (e) {
            window.location.href = '/mentor';
        }
    }

    if (newChatTopBtn) newChatTopBtn.addEventListener('click', handleNewChat);
    if (newChatSidebarBtn) newChatSidebarBtn.addEventListener('click', handleNewChat);

    // Clear Chat handler
    if (clearChatBtn) {
        clearChatBtn.addEventListener('click', async function () {
            const convId = this.dataset.convId;
            if (!convId || !confirm('Are you sure you want to clear this conversation history?')) return;
            try {
                const res = await fetch(`/api/mentor/clear/${convId}`, { method: 'POST' });
                const data = await res.json();
                if (data.success) {
                    window.location.reload();
                }
            } catch (e) {
                console.error(e);
            }
        });
    }

    // Dynamic sync of provider status
    async function syncProviderStatus() {
        const badge = document.getElementById('aiProviderBadge');
        if (!badge) return;
        try {
            const res = await fetch('/api/mentor/status');
            if (res.ok) {
                const data = await res.json();
                if (data.is_live) {
                    badge.className = 'badge bg-success text-white px-3 py-1.5 rounded-pill shadow-sm';
                    badge.innerHTML = `<i class="bi bi-broadcast me-1"></i> Connected: ${data.status_badge || data.model}`;
                } else if (data.provider === 'ollama') {
                    badge.className = 'badge bg-warning text-dark px-3 py-1.5 rounded-pill shadow-sm';
                    badge.innerHTML = `<i class="bi bi-exclamation-triangle-fill me-1"></i> Offline: Ollama Unavailable`;
                } else {
                    badge.className = 'badge bg-dark bg-opacity-50 text-white border border-light border-opacity-25 px-3 py-1.5 rounded-pill';
                    badge.innerHTML = `<i class="bi bi-check-circle-fill text-success me-1"></i> ${data.status_badge || 'Local Knowledge Engine'}`;
                }
            }
        } catch (err) {
            // Keep existing static badge
        }
    }
    syncProviderStatus();

    scrollToBottom(true);
});
