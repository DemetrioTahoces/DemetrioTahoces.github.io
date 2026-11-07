/*
 * Comportamiento compartido de index.html, CV/*.html y blog/.
 * - Reveals con stagger sobre [data-reveal] / [data-reveal-group] (gate html.motion-ready).
 * - Scroll-spy del nav (solo si hay anclas internas), jump-nav ([data-section-nav]) y estado .is-scrolled.
 * - Home: duración del puesto actual, copiar email ([data-copy]), competencias con evidencia
 *   ([data-used-in]), formulario de preguntas al asistente ([data-ask-form]) y brillo de tarjetas.
 * - Blog: en cada artículo, barra de progreso, índice lateral con scroll-spy, anclas copiables y
 *   pregunta al asistente sobre el artículo; en el índice, filtros por etiqueta ([data-post-filters]).
 * - Analítica sin cookies (GoatCounter): una sola inyección aquí para todas las páginas.
 * Si este fichero no carga, el atributo onerror del <script> retira motion-ready y todo queda visible.
 */
(function () {
    'use strict';

    var GOATCOUNTER = 'https://demetriotahoces.goatcounter.com/count';
    // cv.js vive en assets/: la página del asistente se resuelve desde aquí, sea cual sea la carpeta.
    var SCRIPT_SRC = document.currentScript ? document.currentScript.src : '';

    function track(name) {
        if (window.goatcounter && typeof window.goatcounter.count === 'function') {
            window.goatcounter.count({ path: name, title: name, event: true });
        }
    }

    function slugify(text) {
        return text.toLowerCase().normalize('NFD').replace(/[̀-ͯ]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    }

    function initReveals() {
        var items = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
        if (!items.length) return;

        if (!('IntersectionObserver' in window) || !document.documentElement.classList.contains('motion-ready')) {
            items.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }

        // Stagger corto y tope bajo: en scroll rápido el contenido no debe quedarse vacío.
        var STAGGER = 45;
        var MAX_DELAY = 180;

        var observer = new IntersectionObserver(function (entries) {
            // El stagger solo se aplica entre elementos que entran en el mismo lote,
            // agrupados por su data-reveal-group más cercano: en scroll lento cada
            // elemento entra solo y se revela sin retardo.
            var byGroup = new Map();
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                var group = entry.target.closest('[data-reveal-group]') || entry.target;
                if (!byGroup.has(group)) byGroup.set(group, []);
                byGroup.get(group).push(entry.target);
            });
            byGroup.forEach(function (els) {
                els.forEach(function (el, i) {
                    el.style.setProperty('--reveal-delay', Math.min(i * STAGGER, MAX_DELAY) + 'ms');
                    reveal(el);
                });
            });
            // Un salto de scroll (ancla, tecla Fin, flick en móvil) puede dejar atrás
            // elementos que nunca llegaron a intersectar: se marcan como visibles igualmente.
            items.forEach(function (el) {
                if (!el.classList.contains('is-visible') && el.getBoundingClientRect().bottom < 0) reveal(el);
            });
        }, { threshold: 0, rootMargin: '0px 0px 35% 0px' });

        function reveal(el) {
            el.classList.add('is-visible');
            observer.unobserve(el);
        }

        items.forEach(function (el) { observer.observe(el); });

        // Imprimir o guardar como PDF no debe sacar contenido sin revelar.
        window.addEventListener('beforeprint', function () {
            items.forEach(reveal);
        });
    }

    function initJumpNav() {
        var sectionNav = document.querySelector('[data-section-nav]');
        if (!sectionNav) return;

        var headings = Array.prototype.slice.call(document.querySelectorAll('main section h2, main h2.phase-label'));
        headings.forEach(function (heading, index) {
            var section = heading.closest('section') || heading;
            if (!section.id) section.id = slugify(heading.textContent) || ('seccion-' + index);
            var link = document.createElement('a');
            link.href = '#' + section.id;
            link.textContent = heading.textContent.trim();
            sectionNav.appendChild(link);
        });
    }

    function initScrollSpy() {
        var navLinks = Array.prototype.slice.call(document.querySelectorAll('.site-nav-links a[href^="#"]'));
        if (!navLinks.length || !('IntersectionObserver' in window)) return;

        var sections = navLinks
            .map(function (link) { return document.getElementById(link.getAttribute('href').slice(1)); })
            .filter(Boolean);

        // Franja fina hacia el 40% de la pantalla: activa la sección que la cruza. Con un umbral
        // de proporción (antes 0.32) las secciones altas nunca llegaban a activarse.
        var spy = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                navLinks.forEach(function (link) {
                    link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id);
                });
            });
        }, { threshold: 0, rootMargin: '-38% 0px -60% 0px' });

        sections.forEach(function (section) { spy.observe(section); });
    }

    function initNavScrolled() {
        var nav = document.querySelector('.site-nav');
        if (!nav) return;

        function update() {
            nav.classList.toggle('is-scrolled', window.scrollY > 8);
        }

        window.addEventListener('scroll', update, { passive: true });
        update();
    }

    // "1 año y 11 meses": meses inclusivos, como LinkedIn. data-start="AAAA-MM", data-end vacío = hoy.
    function initDurations() {
        Array.prototype.forEach.call(document.querySelectorAll('.job-duration[data-start]'), function (el) {
            var start = el.dataset.start.split('-').map(Number);
            var now = new Date();
            var end = el.dataset.end ? el.dataset.end.split('-').map(Number) : [now.getFullYear(), now.getMonth() + 1];
            var months = (end[0] - start[0]) * 12 + (end[1] - start[1]) + 1;
            if (!(months > 0)) return;
            var years = Math.floor(months / 12);
            var rest = months % 12;
            var parts = [];
            if (years) parts.push(years + (years === 1 ? ' año' : ' años'));
            if (rest) parts.push(rest + (rest === 1 ? ' mes' : ' meses'));
            el.textContent = parts.join(' y ');
        });
    }

    var toastTimer = null;
    function showToast(text) {
        var toast = document.querySelector('.toast');
        if (!toast) {
            toast = document.createElement('div');
            toast.className = 'toast';
            toast.setAttribute('role', 'status');
            document.body.appendChild(toast);
        }
        toast.textContent = text;
        toast.classList.add('is-visible');
        clearTimeout(toastTimer);
        toastTimer = setTimeout(function () { toast.classList.remove('is-visible'); }, 2200);
    }

    function initCopy() {
        Array.prototype.forEach.call(document.querySelectorAll('[data-copy]'), function (button) {
            button.addEventListener('click', function () {
                var value = button.dataset.copy;
                var done = function () {
                    showToast(button.dataset.copyLabel || 'Copiado');
                    track('copiar-email');
                };
                if (navigator.clipboard && window.isSecureContext) {
                    navigator.clipboard.writeText(value).then(done, function () { window.prompt('Copia el email:', value); });
                } else {
                    window.prompt('Copia el email:', value);
                }
            });
        });
    }

    // Competencias con evidencia: cada tecnología con data-used-in="id1 id2" se vuelve un botón
    // que lista, dentro de su tarjeta, los puestos o proyectos donde se usó (enlaces a su ancla).
    function initSkillEvidence() {
        var tags = Array.prototype.slice.call(document.querySelectorAll('.skill-tag[data-used-in]'));
        if (!tags.length) return;

        var hint = document.querySelector('[data-skills-hint]');
        if (hint) hint.hidden = false;

        var panels = new Map();
        function panelFor(group) {
            if (!panels.has(group)) {
                var panel = document.createElement('div');
                panel.className = 'skills-evidence';
                panel.hidden = true;
                panel.setAttribute('aria-live', 'polite');
                group.appendChild(panel);
                panels.set(group, panel);
            }
            return panels.get(group);
        }

        function clear() {
            tags.forEach(function (tag) {
                tag.classList.remove('is-active');
                var button = tag.querySelector('button');
                if (button) button.setAttribute('aria-pressed', 'false');
            });
            panels.forEach(function (panel) { panel.hidden = true; });
        }

        tags.forEach(function (tag) {
            var targets = tag.dataset.usedIn.split(/\s+/)
                .map(function (id) { return document.getElementById(id); })
                .filter(Boolean);
            if (!targets.length) return;

            var button = document.createElement('button');
            button.type = 'button';
            button.setAttribute('aria-pressed', 'false');
            while (tag.firstChild) button.appendChild(tag.firstChild);
            tag.appendChild(button);
            tag.classList.add('is-interactive');

            button.addEventListener('click', function () {
                var wasActive = tag.classList.contains('is-active');
                clear();
                if (wasActive) return;
                tag.classList.add('is-active');
                button.setAttribute('aria-pressed', 'true');

                var panel = panelFor(tag.closest('.skill-group') || tag.parentNode);
                panel.textContent = '';
                var label = document.createElement('span');
                var name = document.createElement('strong');
                name.textContent = button.textContent.trim();
                label.appendChild(name);
                label.appendChild(document.createTextNode(' · dónde la he usado:'));
                panel.appendChild(label);
                targets.forEach(function (target) {
                    var link = document.createElement('a');
                    link.href = '#' + target.id;
                    link.textContent = target.dataset.evidence || target.id;
                    panel.appendChild(link);
                });
                panel.hidden = false;
                track('competencia-' + name.textContent.toLowerCase().normalize('NFD').replace(/[^a-z0-9]+/g, '-'));
            });
        });
    }

    // Formulario "Pregúntale algo": con el widget cargado abre el panel; sin JS va a CV/chatbot.html?q=
    function initAskForm() {
        Array.prototype.forEach.call(document.querySelectorAll('[data-ask-form]'), function (form) {
            form.addEventListener('submit', function (event) {
                var input = form.querySelector('input[name="q"]');
                var question = input ? input.value.trim() : '';
                if (!question) {
                    event.preventDefault();
                    if (input) input.focus();
                    return;
                }
                if (window.cvChatbot && window.innerWidth > 768) {
                    event.preventDefault();
                    window.cvChatbot.ask(question);
                    input.value = '';
                }
            });
        });
    }

    // Brillo que sigue al puntero en las tarjetas (solo ratón, sin reduced-motion)
    function initSpotlight() {
        if (!window.matchMedia('(hover: hover) and (pointer: fine) and (prefers-reduced-motion: no-preference)').matches) return;
        var cards = document.querySelectorAll('[data-spotlight] .card, .card[data-spotlight]');
        Array.prototype.forEach.call(cards, function (card) {
            card.classList.add('spotlight');
            card.addEventListener('pointermove', function (event) {
                var rect = card.getBoundingClientRect();
                card.style.setProperty('--mx', (event.clientX - rect.left) + 'px');
                card.style.setProperty('--my', (event.clientY - rect.top) + 'px');
            });
        });
    }

    // Texto de un h2 sin el emoji decorativo ni el ancla que se le añade.
    function headingText(heading) {
        var clone = heading.cloneNode(true);
        Array.prototype.forEach.call(clone.querySelectorAll('.emoji, .heading-anchor'), function (el) { el.remove(); });
        return clone.textContent.replace(/\s+/g, ' ').trim();
    }

    // Artículo del blog: nada de esto va en el HTML del post (lo genera la plantilla de manage-blog sin ello).
    function initArticle() {
        var prose = document.querySelector('.article-prose');
        var article = prose && prose.closest('article');
        if (!article) return;

        var bar = document.createElement('div');
        bar.className = 'reading-progress';
        bar.setAttribute('aria-hidden', 'true');
        document.body.insertBefore(bar, document.body.firstChild);

        var headings = Array.prototype.slice.call(prose.querySelectorAll(':scope > section[id] > h2'));
        var sections = headings
            .map(function (h2) { return h2.parentNode; })
            .filter(function (section) { return section.id !== 'fuentes'; });

        // Índice lateral (solo se ve en pantallas anchas) y, debajo, la pregunta al asistente.
        var toc = document.createElement('nav');
        toc.className = 'article-toc';
        toc.setAttribute('aria-label', 'En este artículo');
        var tocTitle = document.createElement('p');
        tocTitle.className = 'article-toc-title';
        tocTitle.textContent = 'En este artículo';
        var list = document.createElement('ol');
        list.className = 'article-toc-list';
        var links = new Map();
        sections.forEach(function (section) {
            var item = document.createElement('li');
            var link = document.createElement('a');
            link.href = '#' + section.id;
            link.textContent = headingText(section.querySelector(':scope > h2'));
            item.appendChild(link);
            list.appendChild(item);
            links.set(section, link);
        });
        toc.appendChild(tocTitle);
        toc.appendChild(list);

        var title = document.querySelector('.article-hero h1');
        if (title) {
            // El widget del chatbot (CV/chatbot-widget.js, cargado después) intercepta este enlace y
            // abre el panel con data-ask; en móvil o sin widget, chatbot.html lee ?q=.
            var question = 'Resúmeme en tres ideas el artículo «' + headingText(title) + '»';
            var ask = document.createElement('a');
            ask.className = 'btn btn-ai article-toc-ask';
            ask.href = new URL('../CV/chatbot.html', SCRIPT_SRC || window.location.href).pathname + '?q=' + encodeURIComponent(question);
            ask.dataset.ask = question;
            ask.appendChild(document.createTextNode('Pregunta al asistente sobre este artículo '));
            var tag = document.createElement('span');
            tag.className = 'btn-tag';
            tag.textContent = 'IA';
            ask.appendChild(tag);
            ask.addEventListener('click', function () { track('blog-preguntar-articulo'); });
            toc.appendChild(ask);
        }

        prose.parentNode.insertBefore(toc, prose.nextSibling);
        if (sections.length > 1) article.classList.add('has-toc');

        // Anclas copiables: copian la URL de la sección sin mover la página.
        headings.forEach(function (h2) {
            var id = h2.parentNode.id;
            var anchor = document.createElement('a');
            anchor.className = 'heading-anchor';
            anchor.href = '#' + id;
            anchor.textContent = '#';
            anchor.setAttribute('aria-label', 'Copiar el enlace a «' + headingText(h2) + '»');
            anchor.addEventListener('click', function (event) {
                if (!(navigator.clipboard && window.isSecureContext)) return; // sin portapapeles, navega al ancla
                event.preventDefault();
                var url = window.location.origin + window.location.pathname + window.location.search + '#' + id;
                history.replaceState(null, '', '#' + id);
                navigator.clipboard.writeText(url).then(function () {
                    showToast('Enlace a la sección copiado');
                    track('blog-copiar-ancla');
                }, function () { window.location.hash = id; });
            });
            h2.appendChild(anchor);
        });

        // Scroll-spy del índice: activa la sección que cruza una franja alta de la pantalla.
        if (!('IntersectionObserver' in window) || sections.length < 2) return;
        var visible = new Set();
        var current = null;
        var spy = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (entry.isIntersecting) visible.add(entry.target); else visible.delete(entry.target);
            });
            var active = sections.filter(function (section) { return visible.has(section); })[0];
            if (!active || active === current) return;
            if (current) {
                links.get(current).classList.remove('is-active');
                links.get(current).removeAttribute('aria-current');
            }
            current = active;
            links.get(current).classList.add('is-active');
            links.get(current).setAttribute('aria-current', 'location');
        }, { threshold: 0, rootMargin: '-15% 0px -70% 0px' });
        sections.forEach(function (section) { spy.observe(section); });
    }

    // Índice del blog: un chip por etiqueta con 2 o más artículos (más la de ?tag= si viene en la URL).
    // Con un filtro activo la rejilla pierde el destacado (.is-filtered) y se ocultan las demás tarjetas.
    function initPostFilters() {
        var box = document.querySelector('[data-post-filters]');
        var grid = document.querySelector('[data-post-grid]');
        if (!box || !grid) return;

        var cards = Array.prototype.slice.call(grid.querySelectorAll('.post-card'));
        var tagsOf = new Map();
        var counts = new Map();
        cards.forEach(function (card) {
            var tags = Array.prototype.map.call(card.querySelectorAll('.badge'), function (badge) { return badge.textContent.trim(); });
            tagsOf.set(card, tags);
            tags.forEach(function (tag) { counts.set(tag, (counts.get(tag) || 0) + 1); });
        });

        var initial = new URLSearchParams(window.location.search).get('tag');
        if (!counts.has(initial)) initial = '';
        var tags = Array.from(counts.keys())
            .filter(function (tag) { return counts.get(tag) > 1 || tag === initial; })
            .sort(function (a, b) { return counts.get(b) - counts.get(a) || a.localeCompare(b, 'es'); });
        if (!tags.length) return;

        box.setAttribute('role', 'group');
        box.setAttribute('aria-label', 'Filtrar artículos por etiqueta');
        var buttons = [];
        function chip(label, value, count) {
            var button = document.createElement('button');
            button.type = 'button';
            button.className = 'post-filter';
            button.dataset.tag = value;
            button.appendChild(document.createTextNode(label));
            var number = document.createElement('span');
            number.className = 'post-filter-count';
            number.textContent = count;
            button.appendChild(number);
            button.addEventListener('click', function () { apply(value, true); });
            box.appendChild(button);
            buttons.push(button);
        }
        chip('Todos', '', cards.length);
        tags.forEach(function (tag) { chip(tag, tag, counts.get(tag)); });

        function apply(tag, fromUser) {
            buttons.forEach(function (button) { button.setAttribute('aria-pressed', String(button.dataset.tag === tag)); });
            cards.forEach(function (card) { card.hidden = !!tag && tagsOf.get(card).indexOf(tag) === -1; });
            grid.classList.toggle('is-filtered', !!tag);
            if (!fromUser) return;
            var url = new URL(window.location.href);
            if (tag) url.searchParams.set('tag', tag); else url.searchParams.delete('tag');
            history.replaceState(null, '', url);
            if (tag) track('blog-filtro-' + slugify(tag));
        }
        apply(initial, false);
    }

    // GoatCounter: sin cookies ni datos personales. No cuenta en localhost ni dentro de iframes.
    // Los clics con data-goatcounter-click los registra solo; los eventos de JS van por track().
    function initAnalytics() {
        if (window.location.protocol === 'file:' || document.querySelector('script[data-goatcounter]')) return;
        var script = document.createElement('script');
        script.async = true;
        script.src = 'https://gc.zgo.at/count.js';
        script.dataset.goatcounter = GOATCOUNTER;
        document.head.appendChild(script);
    }

    function init() {
        initJumpNav();
        initArticle();
        initPostFilters();
        initReveals();
        initScrollSpy();
        initNavScrolled();
        initDurations();
        initCopy();
        initSkillEvidence();
        initAskForm();
        initSpotlight();
        initAnalytics();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
