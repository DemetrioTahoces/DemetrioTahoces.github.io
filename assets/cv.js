/*
 * Comportamiento compartido de index.html, CV/*.html y blog/.
 * - Reveals con stagger sobre [data-reveal] / [data-reveal-group] (gate html.motion-ready).
 * - Scroll-spy del nav (solo si hay anclas internas), jump-nav ([data-section-nav]) y estado .is-scrolled.
 * Si este fichero no carga, el atributo onerror del <script> retira motion-ready y todo queda visible.
 */
(function () {
    'use strict';

    function initReveals() {
        var items = Array.prototype.slice.call(document.querySelectorAll('[data-reveal]'));
        if (!items.length) return;

        if (!('IntersectionObserver' in window) || !document.documentElement.classList.contains('motion-ready')) {
            items.forEach(function (el) { el.classList.add('is-visible'); });
            return;
        }

        var STAGGER = 70;
        var MAX_DELAY = 420;

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
                    el.classList.add('is-visible');
                    observer.unobserve(el);
                });
            });
        }, { threshold: 0.01, rootMargin: '0px 0px 15% 0px' });

        items.forEach(function (el) { observer.observe(el); });
    }

    function initJumpNav() {
        var sectionNav = document.querySelector('[data-section-nav]');
        if (!sectionNav) return;

        function slugify(text) {
            return text.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
        }

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

        var spy = new IntersectionObserver(function (entries) {
            entries.forEach(function (entry) {
                if (!entry.isIntersecting) return;
                navLinks.forEach(function (link) {
                    link.classList.toggle('active', link.getAttribute('href') === '#' + entry.target.id);
                });
            });
        }, { threshold: 0.32, rootMargin: '-20% 0px -55% 0px' });

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

    function init() {
        initReveals();
        initJumpNav();
        initScrollSpy();
        initNavScrolled();
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
