(function () {
    console.log('[Chatbot Widget] Script loaded.');

    // Inject Styles for FAB and Chatbot Window
    const style = document.createElement('style');
    style.innerHTML = `
        .chatbot-widget-container {
            position: fixed;
            bottom: 20px;
            right: 20px;
            z-index: 99999;
            font-family: 'Inter', sans-serif;
        }

        .chatbot-fab {
            width: 56px;
            height: 56px;
            border-radius: 50%;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            border: 1px solid rgba(59, 130, 246, 0.4);
            box-shadow: 0 8px 30px rgba(37, 99, 235, 0.4);
            color: #ffffff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
            outline: none;
            padding: 0;
        }

        .chatbot-fab:hover {
            transform: scale(1.05) translateY(-2px);
            box-shadow: 0 12px 35px rgba(37, 99, 235, 0.6);
        }

        .chatbot-fab i {
            font-size: 26px;
            transition: transform 0.3s ease;
        }

        .chatbot-fab.open i {
            transform: rotate(90deg);
        }

        .chatbot-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: 420px;
            height: 580px;
            max-height: calc(100vh - 110px);
            background: #080f1c;
            border: 1px solid rgba(31, 41, 55, 0.8);
            border-radius: 1.25rem;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
            overflow: hidden;
            transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1), transform 0.3s cubic-bezier(0.4, 0, 0.2, 1), visibility 0.3s;
            opacity: 1;
            transform: translateY(0) scale(1);
            visibility: visible;
        }

        .chatbot-window.chatbot-hidden {
            opacity: 0;
            transform: translateY(20px) scale(0.95);
            visibility: hidden;
            pointer-events: none;
        }

        /* Responsive styles */
        @media (max-width: 500px) {
            .chatbot-window {
                bottom: 0;
                right: 0;
                width: 100vw;
                height: 100vh;
                max-height: 100vh;
                border-radius: 0;
                border: none;
            }
            
            .chatbot-widget-container {
                bottom: 16px;
                right: 16px;
            }
            
            .chatbot-fab.open-mobile-hidden {
                display: none;
            }
        }
    `;
    document.head.appendChild(style);

    // Dynamically load Phosphor Icons if not present on the parent page
    if (!document.querySelector('script[src*="phosphor-icons"]')) {
        const phosphorScript = document.createElement('script');
        phosphorScript.src = "https://unpkg.com/@phosphor-icons/web";
        const targetHead = document.head || document.getElementsByTagName('head')[0] || document.documentElement;
        targetHead.appendChild(phosphorScript);
        console.log('[Chatbot Widget] Appended Phosphor Icons script.');
    }

    // Robust wrapper for localStorage to handle security exceptions under file:// protocol
    const safeStorage = {
        getItem: function (key) {
            try {
                return localStorage.getItem(key);
            } catch (e) {
                console.warn('[Chatbot Widget] localStorage.getItem failed:', e);
                return null;
            }
        },
        setItem: function (key, value) {
            try {
                localStorage.setItem(key, value);
            } catch (e) {
                console.warn('[Chatbot Widget] localStorage.setItem failed:', e);
            }
        },
        removeItem: function (key) {
            try {
                localStorage.removeItem(key);
            } catch (e) {
                console.warn('[Chatbot Widget] localStorage.removeItem failed:', e);
            }
        }
    };

    // HTML elements templates
    let container, fab, chatbotWindow, iframe;
    let isLoaded = false;

    function initWidget() {
        if (isLoaded) return;
        if (!document.body) {
            console.warn('[Chatbot Widget] document.body is not available, skipping init.');
            return;
        }

        console.log('[Chatbot Widget] Initializing UI elements...');

        // Create Widget Wrapper
        container = document.createElement('div');
        container.className = 'chatbot-widget-container';

        // Create FAB
        fab = document.createElement('button');
        fab.className = 'chatbot-fab';
        fab.setAttribute('aria-label', 'Abrir asistente virtual');
        fab.innerHTML = '<i class="ph ph-robot"></i>';

        // Create Chatbot Window
        chatbotWindow = document.createElement('div');
        chatbotWindow.className = 'chatbot-window chatbot-hidden';

        // Append components to container, then container to body
        container.appendChild(chatbotWindow);
        container.appendChild(fab);
        document.body.appendChild(container);

        // Click handlers
        fab.addEventListener('click', toggleChatbot);

        // Listen for postMessage from chatbot iframe
        window.addEventListener('message', (event) => {
            if (event.data && event.data.type === 'minimize') {
                console.log('[Chatbot Widget] Received minimize event from iframe.');
                closeChatbot();
            }
        });

        // Intercept chatbot links
        interceptChatbotLinks();

        // Restore state from localStorage (only on desktop/tablet)
        const isOpen = safeStorage.getItem('chatbot_open') === 'true';
        const isMobile = window.innerWidth <= 768;
        if (isOpen && !isMobile) {
            console.log('[Chatbot Widget] Restoring open state from storage.');
            openChatbot();
        }

        isLoaded = true;
        console.log('[Chatbot Widget] Initialization complete.');
    }

    function toggleChatbot() {
        const isMobile = window.innerWidth <= 768;
        if (isMobile) {
            const pathLower = window.location.pathname.toLowerCase();
            const isInsideCV = pathLower.includes('/cv/') || pathLower.includes('\\cv\\');
            const targetUrl = isInsideCV ? 'chatbot.html' : 'CV/chatbot.html';
            window.location.href = targetUrl;
            return;
        }

        const isCurrentlyHidden = chatbotWindow.classList.contains('chatbot-hidden');
        if (isCurrentlyHidden) {
            openChatbot();
        } else {
            closeChatbot();
        }
    }

    function openChatbot() {
        // Ensure iframe is loaded
        ensureIframeCreated();

        chatbotWindow.classList.remove('chatbot-hidden');
        fab.classList.add('open-mobile-hidden');
        
        const fabIcon = fab.querySelector('i');
        if (fabIcon) {
            fabIcon.className = 'ph ph-x';
        }
        
        safeStorage.setItem('chatbot_open', 'true');
    }

    function closeChatbot() {
        chatbotWindow.classList.add('chatbot-hidden');
        fab.classList.remove('open-mobile-hidden');

        const fabIcon = fab.querySelector('i');
        if (fabIcon) {
            fabIcon.className = 'ph ph-robot';
        }

        safeStorage.setItem('chatbot_open', 'false');
    }

    function ensureIframeCreated() {
        if (!iframe) {
            iframe = document.createElement('iframe');
            
            // Dynamically determine the path depending on parent page location
            // to support both http:// and local file:// protocols (case-insensitive).
            const pathLower = window.location.pathname.toLowerCase();
            const isInsideCV = pathLower.includes('/cv/') || pathLower.includes('\\cv\\');
            iframe.src = isInsideCV ? 'chatbot.html' : 'CV/chatbot.html';
            console.log('[Chatbot Widget] Created iframe. Path:', window.location.pathname, 'isInsideCV:', isInsideCV, 'src:', iframe.src);
            
            iframe.style.width = '100%';
            iframe.style.height = '100%';
            iframe.style.border = 'none';
            iframe.style.borderRadius = 'inherit';
            chatbotWindow.appendChild(iframe);
        }
    }

    function interceptChatbotLinks() {
        const links = document.querySelectorAll('a');
        links.forEach(link => {
            const href = link.getAttribute('href');
            if (href && (href.endsWith('chatbot.html') || href.includes('chatbot.html'))) {
                link.addEventListener('click', (e) => {
                    const isMobile = window.innerWidth <= 768;
                    if (!isMobile) {
                        e.preventDefault();
                        openChatbot();
                    }
                });
            }
        });
    }

    // Initialize safely when document.body is available
    function tryInit() {
        if (document.body) {
            initWidget();
        } else {
            document.addEventListener('DOMContentLoaded', initWidget);
            window.addEventListener('load', initWidget);
        }
    }
    tryInit();
})();
