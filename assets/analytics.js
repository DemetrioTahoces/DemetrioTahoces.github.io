/*
 * Vercel Web Analytics initialization
 * Tracks page views and events across the CV site
 */
(function () {
    'use strict';

    // Initialize Vercel Analytics using the global va function
    window.va = window.va || function () {
        (window.vaq = window.vaq || []).push(arguments);
    };

    // Load the Vercel Analytics script
    var script = document.createElement('script');
    script.defer = true;
    script.src = 'https://cdn.vercel-insights.com/v1/script.js';
    
    // Add error handling
    script.onerror = function () {
        console.warn('Vercel Analytics failed to load');
    };
    
    document.head.appendChild(script);
})();
