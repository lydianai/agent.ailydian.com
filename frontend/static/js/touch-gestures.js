/**
 * Lydian Agent - Advanced Touch Gestures & Mobile Interactions
 * Ultra-Premium Touch Support with Modern APIs
 *
 * Features:
 * - Swipe gestures (left, right, up, down)
 * - Pinch to zoom
 * - Long press
 * - Double tap
 * - Pull to refresh
 * - Smooth scrolling
 * - Haptic feedback (iOS/Android)
 * - Touch ripple effects
 * - Passive event listeners for performance
 */

(function() {
    'use strict';

    // ============================================
    // 1. TOUCH GESTURE DETECTOR
    // ============================================

    class TouchGestureDetector {
        constructor(element, options = {}) {
            this.element = element;
            this.options = {
                swipeThreshold: options.swipeThreshold || 50,
                swipeTimeout: options.swipeTimeout || 300,
                longPressDelay: options.longPressDelay || 500,
                doubleTapDelay: options.doubleTapDelay || 300,
                pinchThreshold: options.pinchThreshold || 0.1,
                ...options
            };

            this.touchStartX = 0;
            this.touchStartY = 0;
            this.touchEndX = 0;
            this.touchEndY = 0;
            this.touchStartTime = 0;
            this.lastTapTime = 0;
            this.longPressTimer = null;
            this.initialDistance = 0;

            this.init();
        }

        init() {
            // Use passive event listeners for better scroll performance
            this.element.addEventListener('touchstart', this.handleTouchStart.bind(this), { passive: true });
            this.element.addEventListener('touchmove', this.handleTouchMove.bind(this), { passive: false });
            this.element.addEventListener('touchend', this.handleTouchEnd.bind(this), { passive: true });
        }

        handleTouchStart(e) {
            this.touchStartTime = Date.now();

            if (e.touches.length === 1) {
                // Single touch
                this.touchStartX = e.touches[0].clientX;
                this.touchStartY = e.touches[0].clientY;

                // Start long press timer
                this.longPressTimer = setTimeout(() => {
                    this.triggerEvent('longpress', {
                        x: this.touchStartX,
                        y: this.touchStartY
                    });
                }, this.options.longPressDelay);

            } else if (e.touches.length === 2) {
                // Pinch gesture
                this.initialDistance = this.getDistance(
                    e.touches[0],
                    e.touches[1]
                );
            }
        }

        handleTouchMove(e) {
            // Cancel long press on move
            clearTimeout(this.longPressTimer);

            if (e.touches.length === 2) {
                e.preventDefault(); // Prevent default pinch zoom

                const currentDistance = this.getDistance(
                    e.touches[0],
                    e.touches[1]
                );

                const scale = currentDistance / this.initialDistance;

                if (Math.abs(scale - 1) > this.options.pinchThreshold) {
                    this.triggerEvent('pinch', {
                        scale: scale,
                        delta: currentDistance - this.initialDistance
                    });
                }
            }
        }

        handleTouchEnd(e) {
            // Cancel long press
            clearTimeout(this.longPressTimer);

            if (e.changedTouches.length === 1) {
                this.touchEndX = e.changedTouches[0].clientX;
                this.touchEndY = e.changedTouches[0].clientY;

                const touchDuration = Date.now() - this.touchStartTime;
                const deltaX = this.touchEndX - this.touchStartX;
                const deltaY = this.touchEndY - this.touchStartY;

                // Check for tap
                if (Math.abs(deltaX) < 10 && Math.abs(deltaY) < 10 && touchDuration < 200) {
                    const now = Date.now();
                    const timeSinceLastTap = now - this.lastTapTime;

                    if (timeSinceLastTap < this.options.doubleTapDelay) {
                        // Double tap
                        this.triggerEvent('doubletap', {
                            x: this.touchEndX,
                            y: this.touchEndY
                        });
                    } else {
                        // Single tap
                        this.triggerEvent('tap', {
                            x: this.touchEndX,
                            y: this.touchEndY
                        });
                    }

                    this.lastTapTime = now;
                }

                // Check for swipe
                if (touchDuration < this.options.swipeTimeout) {
                    if (Math.abs(deltaX) > this.options.swipeThreshold ||
                        Math.abs(deltaY) > this.options.swipeThreshold) {

                        const direction = this.getSwipeDirection(deltaX, deltaY);

                        this.triggerEvent('swipe', {
                            direction: direction,
                            deltaX: deltaX,
                            deltaY: deltaY,
                            distance: Math.sqrt(deltaX * deltaX + deltaY * deltaY)
                        });

                        this.triggerEvent(`swipe${direction}`, {
                            deltaX: deltaX,
                            deltaY: deltaY
                        });
                    }
                }
            }
        }

        getDistance(touch1, touch2) {
            const dx = touch2.clientX - touch1.clientX;
            const dy = touch2.clientY - touch1.clientY;
            return Math.sqrt(dx * dx + dy * dy);
        }

        getSwipeDirection(deltaX, deltaY) {
            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                return deltaX > 0 ? 'right' : 'left';
            } else {
                return deltaY > 0 ? 'down' : 'up';
            }
        }

        triggerEvent(eventName, detail) {
            const event = new CustomEvent(`gesture:${eventName}`, {
                bubbles: true,
                cancelable: true,
                detail: detail
            });
            this.element.dispatchEvent(event);
        }
    }

    // ============================================
    // 2. HAPTIC FEEDBACK
    // ============================================

    class HapticFeedback {
        static vibrate(pattern = 10) {
            if ('vibrate' in navigator) {
                navigator.vibrate(pattern);
            }
        }

        static light() {
            this.vibrate(10);
        }

        static medium() {
            this.vibrate(20);
        }

        static heavy() {
            this.vibrate(50);
        }

        static success() {
            this.vibrate([10, 50, 10]);
        }

        static error() {
            this.vibrate([50, 50, 50]);
        }

        static selection() {
            this.vibrate(5);
        }
    }

    // ============================================
    // 3. TOUCH RIPPLE EFFECT
    // ============================================

    class TouchRipple {
        static create(element, x, y) {
            const ripple = document.createElement('span');
            const rect = element.getBoundingClientRect();

            const size = Math.max(rect.width, rect.height);
            const offsetX = x - rect.left - size / 2;
            const offsetY = y - rect.top - size / 2;

            ripple.style.cssText = `
                position: absolute;
                width: ${size}px;
                height: ${size}px;
                left: ${offsetX}px;
                top: ${offsetY}px;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple-animation 0.6s ease-out;
                pointer-events: none;
            `;

            ripple.className = 'touch-ripple';
            element.style.position = 'relative';
            element.style.overflow = 'hidden';
            element.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        }

        static init() {
            // Add CSS animation
            if (!document.getElementById('ripple-styles')) {
                const style = document.createElement('style');
                style.id = 'ripple-styles';
                style.textContent = `
                    @keyframes ripple-animation {
                        to {
                            transform: scale(2);
                            opacity: 0;
                        }
                    }
                `;
                document.head.appendChild(style);
            }

            // Auto-apply to buttons
            document.addEventListener('touchstart', (e) => {
                const button = e.target.closest('button, [role="button"], .btn, .card');
                if (button && e.touches.length === 1) {
                    TouchRipple.create(
                        button,
                        e.touches[0].clientX,
                        e.touches[0].clientY
                    );
                }
            }, { passive: true });
        }
    }

    // ============================================
    // 4. SMOOTH SCROLL WITH MOMENTUM
    // ============================================

    class SmoothScroll {
        static scrollTo(target, options = {}) {
            const element = typeof target === 'string' ?
                document.querySelector(target) : target;

            if (!element) return;

            const offset = options.offset || 0;
            const behavior = options.behavior || 'smooth';

            const elementPosition = element.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - offset;

            window.scrollTo({
                top: offsetPosition,
                behavior: behavior
            });
        }

        static init() {
            // Smooth scroll for anchor links
            document.addEventListener('click', (e) => {
                const anchor = e.target.closest('a[href^="#"]');
                if (anchor && anchor.hash) {
                    e.preventDefault();
                    SmoothScroll.scrollTo(anchor.hash, {
                        offset: 80 // Account for fixed header
                    });
                }
            });
        }
    }

    // ============================================
    // 5. MOBILE MENU HANDLER
    // ============================================

    class MobileMenu {
        constructor() {
            this.menuToggle = document.querySelector('.mobile-menu-toggle');
            this.menuClose = document.querySelector('.mobile-menu-close');
            this.navLinks = document.querySelector('.nav-links');
            this.body = document.body;
            this.isOpen = false;

            this.init();
        }

        init() {
            if (!this.menuToggle || !this.navLinks) return;

            // Toggle button
            this.menuToggle.addEventListener('click', () => {
                this.toggle();
            });

            // Close button (inside mobile menu)
            if (this.menuClose) {
                this.menuClose.addEventListener('click', () => {
                    this.close();
                });
            }

            // Close on link click
            this.navLinks.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', () => {
                    this.close();
                });
            });

            // Close on outside click
            document.addEventListener('click', (e) => {
                if (this.isOpen &&
                    !this.navLinks.contains(e.target) &&
                    !this.menuToggle.contains(e.target)) {
                    this.close();
                }
            });

            // Close on escape key
            document.addEventListener('keydown', (e) => {
                if (e.key === 'Escape' && this.isOpen) {
                    this.close();
                }
            });

            // Swipe to close
            const detector = new TouchGestureDetector(this.navLinks);
            this.navLinks.addEventListener('gesture:swipeleft', () => {
                this.close();
            });
        }

        toggle() {
            if (this.isOpen) {
                this.close();
            } else {
                this.open();
            }
        }

        open() {
            this.navLinks.classList.add('active');
            this.menuToggle.classList.add('active');
            this.body.style.overflow = 'hidden';
            this.isOpen = true;
            HapticFeedback.light();
        }

        close() {
            this.navLinks.classList.remove('active');
            this.menuToggle.classList.remove('active');
            this.body.style.overflow = '';
            this.isOpen = false;
            HapticFeedback.light();
        }
    }

    // ============================================
    // 6. VIEWPORT HEIGHT FIX (iOS Safari)
    // ============================================

    class ViewportFix {
        static init() {
            // Fix for iOS Safari address bar height changes
            const setVH = () => {
                const vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            };

            setVH();
            window.addEventListener('resize', setVH);
            window.addEventListener('orientationchange', () => {
                setTimeout(setVH, 100);
            });
        }
    }

    // ============================================
    // 7. LAZY LOADING IMAGES
    // ============================================

    class LazyLoader {
        static init() {
            if ('loading' in HTMLImageElement.prototype) {
                // Native lazy loading
                const images = document.querySelectorAll('img[loading="lazy"]');
                images.forEach(img => {
                    if (img.dataset.src) {
                        img.src = img.dataset.src;
                    }
                });
            } else {
                // Intersection Observer fallback
                const imageObserver = new IntersectionObserver((entries) => {
                    entries.forEach(entry => {
                        if (entry.isIntersecting) {
                            const img = entry.target;
                            if (img.dataset.src) {
                                img.src = img.dataset.src;
                                imageObserver.unobserve(img);
                            }
                        }
                    });
                });

                document.querySelectorAll('img[loading="lazy"]').forEach(img => {
                    imageObserver.observe(img);
                });
            }
        }
    }

    // ============================================
    // 8. PERFORMANCE MONITORING
    // ============================================

    class PerformanceMonitor {
        static init() {
            if ('PerformanceObserver' in window) {
                // Monitor long tasks
                const observer = new PerformanceObserver((list) => {
                    for (const entry of list.getEntries()) {
                        if (entry.duration > 50) {
                            console.warn('Long task detected:', entry.duration, 'ms');
                        }
                    }
                });

                try {
                    observer.observe({ entryTypes: ['longtask'] });
                } catch (e) {
                    // Browser doesn't support longtask
                }
            }

            // Log page load metrics
            window.addEventListener('load', () => {
                setTimeout(() => {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    console.log('📊 Performance Metrics:', {
                        'Page Load': `${perfData.loadEventEnd - perfData.fetchStart}ms`,
                        'DOM Interactive': `${perfData.domInteractive - perfData.fetchStart}ms`,
                        'First Paint': `${performance.getEntriesByType('paint')[0]?.startTime}ms`
                    });
                }, 0);
            });
        }
    }

    // ============================================
    // 9. AUTO-INITIALIZATION
    // ============================================

    window.LydianTouch = {
        TouchGestureDetector,
        HapticFeedback,
        TouchRipple,
        SmoothScroll,
        MobileMenu,
        ViewportFix,
        LazyLoader,
        PerformanceMonitor
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }

    function initAll() {
        console.log('🎯 Lydian Touch Gestures: Initializing...');

        // Initialize all modules
        TouchRipple.init();
        SmoothScroll.init();
        ViewportFix.init();
        LazyLoader.init();
        PerformanceMonitor.init();

        // Initialize mobile menu
        new MobileMenu();

        // Add gesture support to interactive elements
        document.querySelectorAll('.card, .feature-card, .agent-card').forEach(element => {
            new TouchGestureDetector(element);
        });

        // Haptic feedback on buttons
        document.addEventListener('click', (e) => {
            const button = e.target.closest('button, [role="button"], .btn');
            if (button) {
                HapticFeedback.light();
            }
        }, { passive: true });

        console.log('✅ Lydian Touch Gestures: Ready');
    }

    // ============================================
    // 10. EXPORT FOR USE IN OTHER MODULES
    // ============================================

    // Make available globally
    window.addEventListener('gesture:swipeleft', (e) => {
        console.log('Swipe left detected', e.detail);
    });

    window.addEventListener('gesture:swiperight', (e) => {
        console.log('Swipe right detected', e.detail);
    });

    window.addEventListener('gesture:doubletap', (e) => {
        console.log('Double tap detected', e.detail);
    });

})();
