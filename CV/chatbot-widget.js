/*
 * Widget flotante del asistente del CV. Se carga en index.html, CV/*.html y blog/.
 * - Escritorio: abre CV/chatbot.html en un panel (iframe) que se puede ampliar a casi
 *   toda la ventana. Móvil (<= 768px): navega a la página del asistente.
 * - API: window.cvChatbot.ask(texto) abre el panel y envía la pregunta;
 *   los enlaces a chatbot.html con data-ask="..." o ?q=... hacen lo mismo.
 * - La ruta del asistente se calcula desde la URL de este script, así funciona desde cualquier carpeta.
 */
(function () {
    'use strict';

    const SCRIPT_SRC = document.currentScript ? document.currentScript.src : '';

    const style = document.createElement('style');
    style.textContent = `
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
            background: linear-gradient(135deg, #2563eb 0%, #0284c7 100%);
            border: 1px solid rgba(147, 197, 253, 0.34);
            box-shadow: 0 16px 38px rgba(2, 6, 23, 0.38), 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
            color: #ffffff;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.24s ease, border-color 0.24s ease, background 0.24s ease;
            outline: none;
            padding: 0;
        }

        .chatbot-fab:hover {
            transform: translateY(-2px);
            border-color: rgba(147, 197, 253, 0.58);
            box-shadow: 0 20px 46px rgba(2, 6, 23, 0.46), 0 0 0 6px rgba(59, 130, 246, 0.12);
        }

        .chatbot-fab:focus-visible {
            outline: 2px solid var(--accent-strong, #38bdf8);
            outline-offset: 4px;
        }

        .chatbot-fab i {
            font-size: 26px;
            transition: transform 0.24s cubic-bezier(0.22, 1, 0.36, 1);
        }

        .chatbot-fab.open i {
            transform: rotate(90deg);
        }

        /* Más grande que antes (420x580): se leía pequeño y, con zoom, el alto máximo lo aplastaba. */
        .chatbot-window {
            position: fixed;
            bottom: 90px;
            right: 20px;
            width: min(460px, calc(100vw - 40px));
            height: min(720px, calc(100vh - 110px));
            background: var(--bg, #07111f);
            border: 1px solid var(--border-strong, rgba(148, 163, 184, 0.18));
            border-radius: 18px;
            box-shadow: 0 28px 80px rgba(2, 6, 23, 0.62);
            overflow: hidden;
            transition: opacity 0.24s cubic-bezier(0.22, 1, 0.36, 1), transform 0.24s cubic-bezier(0.22, 1, 0.36, 1), visibility 0.24s,
                width 0.28s cubic-bezier(0.22, 1, 0.36, 1), height 0.28s cubic-bezier(0.22, 1, 0.36, 1), bottom 0.28s cubic-bezier(0.22, 1, 0.36, 1);
            opacity: 1;
            transform: translateY(0) scale(1);
            visibility: visible;
            transform-origin: bottom right;
        }

        /* Ampliado: casi toda la ventana, para leer respuestas largas o con zoom. */
        .chatbot-window.is-expanded {
            bottom: 24px;
            right: 24px;
            width: min(1040px, calc(100vw - 48px));
            height: calc(100vh - 48px);
            /* La sombra enorme hace de fondo oscurecido sin añadir otro elemento */
            box-shadow: 0 28px 80px rgba(2, 6, 23, 0.62), 0 0 0 100vmax rgba(2, 6, 23, 0.62);
        }

        .chatbot-widget-container.is-expanded .chatbot-fab {
            display: none;
        }

        .chatbot-window.chatbot-hidden {
            opacity: 0;
            transform: translateY(16px) scale(0.97);
            visibility: hidden;
            pointer-events: none;
        }

        @media (max-width: 500px) {
            .chatbot-window,
            .chatbot-window.is-expanded {
                bottom: 0;
                right: 0;
                width: 100vw;
                height: 100dvh;
                max-height: 100dvh;
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

        @media (hover: none), (pointer: coarse) {
            .chatbot-fab {
                touch-action: manipulation;
            }

            .chatbot-fab:hover {
                transform: none;
                border-color: rgba(147, 197, 253, 0.34);
                box-shadow: 0 16px 38px rgba(2, 6, 23, 0.38), 0 0 0 1px rgba(255, 255, 255, 0.04) inset;
            }
        }

        @media (prefers-reduced-motion: reduce) {
            .chatbot-fab,
            .chatbot-fab i,
            .chatbot-window {
                transition-duration: 0.001ms !important;
            }
        }

        @media print {
            .chatbot-widget-container { display: none !important; }
        }
`;
    document.head.appendChild(style);

    // Solo el peso regular de Phosphor (el script del paquete cargaba los seis estilos)
    if (!document.querySelector('link[href*="phosphor-icons"], script[src*="phosphor-icons"]')) {
        const phosphor = document.createElement('link');
        phosphor.rel = 'stylesheet';
        phosphor.href = 'https://cdn.jsdelivr.net/npm/@phosphor-icons/web@2.1.2/src/regular/style.css';
        document.head.appendChild(phosphor);
    }

    // localStorage puede lanzar (file://, modo privado, cookies bloqueadas)
    const safeStorage = {
        getItem: function (key) {
            try {
                return localStorage.getItem(key);
            } catch (e) {
                return null;
            }
        },
        setItem: function (key, value) {
            try {
                localStorage.setItem(key, value);
            } catch (e) {
                /* sin persistencia */
            }
        }
    };

    const PAGE_CONTEXT_STORAGE_KEY = 'chatbot_page_context';
    const MOBILE_MAX_WIDTH = 768;

    function isMobile() {
        return window.innerWidth <= MOBILE_MAX_WIDTH;
    }

    // Analítica sin cookies (GoatCounter, cargada por assets/cv.js); sin ella no hace nada
    function track(name) {
        if (window.goatcounter && typeof window.goatcounter.count === 'function') {
            window.goatcounter.count({ path: name, title: name, event: true });
        }
    }

    function getPageContext() {
        return {
            path: window.location.pathname || '/',
            title: document.title || ''
        };
    }

    function savePageContext() {
        safeStorage.setItem(PAGE_CONTEXT_STORAGE_KEY, JSON.stringify(getPageContext()));
    }

    function chatbotPageUrl() {
        if (SCRIPT_SRC) {
            try {
                return new URL('chatbot.html', SCRIPT_SRC).href;
            } catch (e) {
                /* sigue con la ruta relativa */
            }
        }
        const pathLower = window.location.pathname.toLowerCase();
        return (pathLower.includes('/cv/') || pathLower.includes('\\cv\\')) ? 'chatbot.html' : 'CV/chatbot.html';
    }

    function buildChatbotUrl(extra) {
        const context = getPageContext();
        let url = chatbotPageUrl() + '?page_path=' + encodeURIComponent(context.path) +
            '&page_title=' + encodeURIComponent(context.title);
        Object.keys(extra || {}).forEach(function (key) {
            url += '&' + key + '=' + encodeURIComponent(extra[key]);
        });
        return url;
    }

    function postToIframe(message) {
        if (!iframe || !iframe.contentWindow) return;
        const origin = window.location.protocol === 'file:' ? '*' : window.location.origin;
        iframe.contentWindow.postMessage(message, origin);
    }

    let container, fab, chatbotWindow, iframe;
    let isLoaded = false;
    let iframeReady = false;
    let pendingQuestion = null;
    let expanded = safeStorage.getItem('chatbot_expanded') === 'true';

    function initWidget() {
        if (isLoaded || !document.body) return;

        container = document.createElement('div');
        container.className = 'chatbot-widget-container';

        fab = document.createElement('button');
        fab.className = 'chatbot-fab';
        fab.type = 'button';
        fab.setAttribute('aria-label', 'Abrir asistente virtual');
        fab.setAttribute('aria-expanded', 'false');
        fab.setAttribute('aria-controls', 'cv-chatbot-window');
        fab.innerHTML = '<i class="ph ph-robot" aria-hidden="true"></i>';

        chatbotWindow = document.createElement('div');
        chatbotWindow.id = 'cv-chatbot-window';
        chatbotWindow.className = 'chatbot-window chatbot-hidden';
        chatbotWindow.setAttribute('role', 'dialog');
        chatbotWindow.setAttribute('aria-label', 'Asistente virtual');

        container.appendChild(chatbotWindow);
        container.appendChild(fab);
        document.body.appendChild(container);

        fab.addEventListener('click', toggleChatbot);

        // Mensajes del iframe: minimizar y ampliar/reducir
        window.addEventListener('message', function (event) {
            if (window.location.protocol !== 'file:' && event.origin !== window.location.origin) return;
            const data = event.data || {};
            if (data.type === 'minimize') closeChatbot();
            if (data.type === 'toggle-size') setExpanded(!expanded);
        });

        // Escape en la página padre: primero reduce el panel ampliado, después lo cierra
        window.addEventListener('keydown', function (event) {
            if (event.key !== 'Escape' || chatbotWindow.classList.contains('chatbot-hidden')) return;
            if (expanded) {
                setExpanded(false);
            } else {
                closeChatbot();
            }
        });

        interceptChatbotLinks();

        // Restaurar el panel abierto solo en escritorio
        if (safeStorage.getItem('chatbot_open') === 'true' && !isMobile()) {
            openChatbot(false);
        }

        isLoaded = true;
    }

    function setExpanded(value) {
        expanded = value;
        safeStorage.setItem('chatbot_expanded', String(value));
        chatbotWindow.classList.toggle('is-expanded', value);
        container.classList.toggle('is-expanded', value);
        postToIframe({ type: 'size', expanded: value });
        if (value) track('chatbot-ampliar');
    }

    function toggleChatbot() {
        if (isMobile()) {
            savePageContext();
            track('chatbot-abrir');
            window.location.href = buildChatbotUrl();
            return;
        }
        if (chatbotWindow.classList.contains('chatbot-hidden')) {
            openChatbot();
        } else {
            closeChatbot();
        }
    }

    function openChatbot(userAction = true, question = '') {
        ensureIframeCreated(question);

        chatbotWindow.classList.remove('chatbot-hidden');
        chatbotWindow.classList.toggle('is-expanded', expanded);
        container.classList.toggle('is-expanded', expanded);
        fab.classList.add('open-mobile-hidden', 'open');
        fab.setAttribute('aria-expanded', 'true');
        fab.setAttribute('aria-label', 'Cerrar asistente virtual');

        const fabIcon = fab.querySelector('i');
        if (fabIcon) fabIcon.className = 'ph ph-x';

        // El foco va al panel solo si lo ha abierto el usuario (no al restaurar en la carga)
        if (userAction) {
            track('chatbot-abrir');
            if (iframe) iframe.focus();
        }

        safeStorage.setItem('chatbot_open', 'true');
    }

    function closeChatbot() {
        chatbotWindow.classList.add('chatbot-hidden');
        container.classList.remove('is-expanded');
        fab.classList.remove('open-mobile-hidden', 'open');
        fab.setAttribute('aria-expanded', 'false');
        fab.setAttribute('aria-label', 'Abrir asistente virtual');

        const fabIcon = fab.querySelector('i');
        if (fabIcon) fabIcon.className = 'ph ph-robot';

        fab.focus();
        safeStorage.setItem('chatbot_open', 'false');
    }

    function ensureIframeCreated(question) {
        if (iframe) return;
        iframe = document.createElement('iframe');
        iframe.title = 'Asistente virtual de Demetrio Tahoces';
        savePageContext();
        const extra = {};
        if (expanded) extra.expanded = '1';
        if (question) extra.q = question;
        iframe.src = buildChatbotUrl(extra);
        iframe.style.width = '100%';
        iframe.style.height = '100%';
        iframe.style.border = 'none';
        iframe.style.borderRadius = 'inherit';
        iframe.addEventListener('load', function () {
            iframeReady = true;
            postToIframe({ type: 'size', expanded: expanded });
            if (pendingQuestion) {
                postToIframe({ type: 'ask', text: pendingQuestion });
                pendingQuestion = null;
            }
        });
        chatbotWindow.appendChild(iframe);
    }

    // Abre el asistente y le envía una pregunta (home: "Pregúntale a mi CV")
    function ask(text) {
        const question = String(text || '').trim();
        if (!question) return;
        track('chatbot-pregunta');
        if (isMobile()) {
            savePageContext();
            window.location.href = buildChatbotUrl({ q: question });
            return;
        }
        if (!iframe) {
            openChatbot(true, question);
            return;
        }
        openChatbot(true);
        if (iframeReady) {
            postToIframe({ type: 'ask', text: question });
        } else {
            pendingQuestion = question;
        }
    }

    function questionFromLink(link) {
        if (link.dataset.ask) return link.dataset.ask;
        try {
            return new URL(link.href, window.location.href).searchParams.get('q') || '';
        } catch (e) {
            return '';
        }
    }

    function interceptChatbotLinks() {
        document.querySelectorAll('a[href*="chatbot.html"]').forEach(function (link) {
            link.addEventListener('click', function (e) {
                if (isMobile()) {
                    savePageContext();
                    return;
                }
                e.preventDefault();
                const question = questionFromLink(link);
                if (question) {
                    ask(question);
                } else {
                    openChatbot();
                }
            });
        });
    }

    window.cvChatbot = { ask: ask, open: function () { openChatbot(); } };

    if (document.body) {
        initWidget();
    } else {
        document.addEventListener('DOMContentLoaded', initWidget);
    }
})();
