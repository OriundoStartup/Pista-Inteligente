/**
 * PISTA INTELIGENTE - Performance & UX Enhancement Module
 * Professional navigation handling with smooth transitions
 * 
 * Features:
 * - Loading overlay with animated spinner
 * - Link prefetching on hover
 * - Smooth page transitions (fade-out/fade-in)
 * - Progressive content reveal animations
 * - Intersection Observer for scroll animations
 */

(function () {
    'use strict';

    // ==================== LOADING OVERLAY ====================
    const PageLoader = {
        element: null,

        init() {
            this.element = document.getElementById('page-loader');
            // Hide loader on page fully loaded
            window.addEventListener('load', () => this.hide());
        },

        show() {
            if (this.element) {
                this.element.classList.add('active');
                document.body.classList.add('loading');
            }
        },

        hide() {
            if (this.element) {
                this.element.classList.remove('active');
                document.body.classList.remove('loading');
            }
        }
    };

    // ==================== LINK PREFETCHING ====================
    const Prefetcher = {
        prefetched: new Set(),
        hoverDelay: 200, // ms before prefetching

        init() {
            document.querySelectorAll('a[href^="/"]').forEach(link => {
                let timer = null;

                link.addEventListener('mouseenter', () => {
                    const href = link.getAttribute('href');
                    if (this.prefetched.has(href)) return;

                    timer = setTimeout(() => {
                        this.prefetch(href);
                    }, this.hoverDelay);
                });

                link.addEventListener('mouseleave', () => {
                    if (timer) clearTimeout(timer);
                });
            });
        },

        prefetch(url) {
            if (this.prefetched.has(url)) return;

            const link = document.createElement('link');
            link.rel = 'prefetch';
            link.href = url;
            link.as = 'document';
            document.head.appendChild(link);

            this.prefetched.add(url);
        }
    };

    // ==================== PAGE TRANSITIONS ====================
    const PageTransitions = {
        duration: 200, // ms for transition

        init() {
            // Add entering animation on page load
            document.body.classList.add('page-entering');

            // Remove animation class after it completes
            setTimeout(() => {
                document.body.classList.remove('page-entering');
                document.body.classList.add('page-ready');
            }, 300);

            // Intercept navigation clicks
            document.querySelectorAll('a[href^="/"]').forEach(link => {
                link.addEventListener('click', (e) => this.handleClick(e, link));
            });
        },

        handleClick(e, link) {
            const href = link.getAttribute('href');

            // Skip if modifier keys are pressed (new tab, etc)
            if (e.ctrlKey || e.metaKey || e.shiftKey) return;

            // Skip if same page
            if (href === window.location.pathname) {
                e.preventDefault();
                return;
            }

            e.preventDefault();
            this.navigateTo(href);
        },

        navigateTo(url) {
            // Show loader
            PageLoader.show();

            // Add exit animation
            document.body.classList.add('page-exiting');
            document.body.classList.remove('page-ready');

            // Navigate after animation
            setTimeout(() => {
                window.location.href = url;
            }, this.duration);
        }
    };

    // ==================== PROGRESSIVE REVEAL ====================
    const ContentReveal = {
        init() {
            // Setup Intersection Observer for scroll animations
            const observer = new IntersectionObserver((entries) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        observer.unobserve(entry.target);
                    }
                });
            }, {
                threshold: 0.1,
                rootMargin: '0px 0px -50px 0px'
            });

            // Observe all cards and sections
            document.querySelectorAll('.glass-card, .hero, .section-title').forEach(el => {
                el.classList.add('reveal-on-scroll');
                observer.observe(el);
            });
        }
    };

    // ==================== PERFORMANCE HINTS ====================
    const PerformanceHints = {
        init() {
            // Reduce motion if user prefers
            if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) {
                document.documentElement.classList.add('reduce-motion');
            }

            // Add will-change hints for animated elements
            document.querySelectorAll('.glass-card, .nav-link, .cta-button').forEach(el => {
                el.style.willChange = 'transform, opacity';
            });

            // Remove will-change after initial load to free memory
            setTimeout(() => {
                document.querySelectorAll('.glass-card, .nav-link, .cta-button').forEach(el => {
                    el.style.willChange = 'auto';
                });
            }, 1000);
        }
    };

    // ==================== INITIALIZE ====================
    function init() {
        PageLoader.init();
        Prefetcher.init();
        PageTransitions.init();
        ContentReveal.init();
        PerformanceHints.init();

        // Log initialization (dev only)
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            console.log('🚀 Pista Inteligente: Performance module loaded');
        }
    }

    // Run on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }

    // Expose for debugging
    window.PistaInteligente = {
        PageLoader,
        Prefetcher,
        PageTransitions,
        ContentReveal
    };
})();
