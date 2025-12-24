/**
 * Lydian Agent - Responsive Manager & PWA Support
 * Advanced responsive utilities and Progressive Web App features
 *
 * Features:
 * - Viewport detection and management
 * - Orientation change handling
 * - Network status monitoring
 * - Device capability detection
 * - PWA install prompt
 * - Offline support
 * - Service Worker registration
 */

(function() {
    'use strict';

    // ============================================
    // 1. RESPONSIVE VIEWPORT MANAGER
    // ============================================

    class ResponsiveManager {
        constructor() {
            this.breakpoints = {
                xs: 0,
                sm: 384,
                md: 640,
                lg: 768,
                xl: 1024,
                '2xl': 1280,
                '3xl': 1536
            };

            this.currentBreakpoint = this.getCurrentBreakpoint();
            this.orientation = this.getOrientation();
            this.callbacks = {
                breakpoint: [],
                orientation: []
            };

            this.init();
        }

        init() {
            // Monitor resize with debounce
            let resizeTimer;
            window.addEventListener('resize', () => {
                clearTimeout(resizeTimer);
                resizeTimer = setTimeout(() => {
                    this.handleResize();
                }, 150);
            });

            // Monitor orientation changes
            window.addEventListener('orientationchange', () => {
                setTimeout(() => {
                    this.handleOrientationChange();
                }, 100);
            });

            // Initial check
            this.updateViewportInfo();
        }

        getCurrentBreakpoint() {
            const width = window.innerWidth;
            let current = 'xs';

            Object.entries(this.breakpoints).forEach(([name, value]) => {
                if (width >= value) {
                    current = name;
                }
            });

            return current;
        }

        getOrientation() {
            return window.innerHeight > window.innerWidth ? 'portrait' : 'landscape';
        }

        handleResize() {
            const newBreakpoint = this.getCurrentBreakpoint();

            if (newBreakpoint !== this.currentBreakpoint) {
                const oldBreakpoint = this.currentBreakpoint;
                this.currentBreakpoint = newBreakpoint;

                this.callbacks.breakpoint.forEach(callback => {
                    callback({
                        from: oldBreakpoint,
                        to: newBreakpoint,
                        width: window.innerWidth
                    });
                });

                // Dispatch custom event
                window.dispatchEvent(new CustomEvent('breakpoint:change', {
                    detail: {
                        from: oldBreakpoint,
                        to: newBreakpoint,
                        width: window.innerWidth
                    }
                }));
            }

            this.updateViewportInfo();
        }

        handleOrientationChange() {
            const newOrientation = this.getOrientation();

            if (newOrientation !== this.orientation) {
                const oldOrientation = this.orientation;
                this.orientation = newOrientation;

                this.callbacks.orientation.forEach(callback => {
                    callback({
                        from: oldOrientation,
                        to: newOrientation
                    });
                });

                // Dispatch custom event
                window.dispatchEvent(new CustomEvent('orientation:change', {
                    detail: {
                        from: oldOrientation,
                        to: newOrientation
                    }
                }));
            }

            this.updateViewportInfo();
        }

        updateViewportInfo() {
            // Update CSS custom properties
            document.documentElement.style.setProperty('--viewport-width', `${window.innerWidth}px`);
            document.documentElement.style.setProperty('--viewport-height', `${window.innerHeight}px`);

            // Update data attributes
            document.documentElement.setAttribute('data-breakpoint', this.currentBreakpoint);
            document.documentElement.setAttribute('data-orientation', this.orientation);
        }

        onBreakpointChange(callback) {
            this.callbacks.breakpoint.push(callback);
        }

        onOrientationChange(callback) {
            this.callbacks.orientation.push(callback);
        }

        isMobile() {
            return this.currentBreakpoint === 'xs' || this.currentBreakpoint === 'sm';
        }

        isTablet() {
            return this.currentBreakpoint === 'md' || this.currentBreakpoint === 'lg';
        }

        isDesktop() {
            return this.currentBreakpoint === 'xl' ||
                   this.currentBreakpoint === '2xl' ||
                   this.currentBreakpoint === '3xl';
        }
    }

    // ============================================
    // 2. DEVICE CAPABILITY DETECTOR
    // ============================================

    class DeviceDetector {
        static getCapabilities() {
            return {
                // Touch support
                touch: 'ontouchstart' in window || navigator.maxTouchPoints > 0,

                // Pointer type
                pointer: this.getPointerType(),

                // Display
                retina: window.devicePixelRatio > 1,
                pixelRatio: window.devicePixelRatio,

                // Network
                online: navigator.onLine,
                connection: this.getConnectionInfo(),

                // Features
                serviceWorker: 'serviceWorker' in navigator,
                localStorage: this.hasLocalStorage(),
                sessionStorage: this.hasSessionStorage(),
                indexedDB: 'indexedDB' in window,

                // Sensors
                geolocation: 'geolocation' in navigator,
                deviceOrientation: 'DeviceOrientationEvent' in window,
                deviceMotion: 'DeviceMotionEvent' in window,

                // Media
                getUserMedia: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
                webRTC: !!(window.RTCPeerConnection || window.webkitRTCPeerConnection),

                // Graphics
                webGL: this.hasWebGL(),
                webGL2: this.hasWebGL2(),

                // Performance
                performanceAPI: 'performance' in window,
                intersectionObserver: 'IntersectionObserver' in window,

                // Platform
                platform: navigator.platform,
                userAgent: navigator.userAgent,
                vendor: navigator.vendor,

                // OS Detection
                os: this.getOS(),
                browser: this.getBrowser()
            };
        }

        static getPointerType() {
            if (window.matchMedia('(pointer: coarse)').matches) {
                return 'touch';
            } else if (window.matchMedia('(pointer: fine)').matches) {
                return 'mouse';
            }
            return 'unknown';
        }

        static getConnectionInfo() {
            const connection = navigator.connection ||
                             navigator.mozConnection ||
                             navigator.webkitConnection;

            if (connection) {
                return {
                    effectiveType: connection.effectiveType,
                    downlink: connection.downlink,
                    rtt: connection.rtt,
                    saveData: connection.saveData
                };
            }

            return null;
        }

        static hasLocalStorage() {
            try {
                localStorage.setItem('test', 'test');
                localStorage.removeItem('test');
                return true;
            } catch (e) {
                return false;
            }
        }

        static hasSessionStorage() {
            try {
                sessionStorage.setItem('test', 'test');
                sessionStorage.removeItem('test');
                return true;
            } catch (e) {
                return false;
            }
        }

        static hasWebGL() {
            try {
                const canvas = document.createElement('canvas');
                return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
            } catch (e) {
                return false;
            }
        }

        static hasWebGL2() {
            try {
                const canvas = document.createElement('canvas');
                return !!canvas.getContext('webgl2');
            } catch (e) {
                return false;
            }
        }

        static getOS() {
            const ua = navigator.userAgent;
            if (/android/i.test(ua)) return 'Android';
            if (/iPad|iPhone|iPod/.test(ua)) return 'iOS';
            if (/Win/.test(ua)) return 'Windows';
            if (/Mac/.test(ua)) return 'macOS';
            if (/Linux/.test(ua)) return 'Linux';
            return 'Unknown';
        }

        static getBrowser() {
            const ua = navigator.userAgent;
            if (/Chrome/.test(ua) && !/Edge/.test(ua)) return 'Chrome';
            if (/Safari/.test(ua) && !/Chrome/.test(ua)) return 'Safari';
            if (/Firefox/.test(ua)) return 'Firefox';
            if (/Edge/.test(ua)) return 'Edge';
            if (/Trident/.test(ua)) return 'IE';
            return 'Unknown';
        }

        static isMobileDevice() {
            return /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        }

        static isIOS() {
            return /iPad|iPhone|iPod/.test(navigator.userAgent);
        }

        static isAndroid() {
            return /Android/i.test(navigator.userAgent);
        }
    }

    // ============================================
    // 3. NETWORK STATUS MONITOR
    // ============================================

    class NetworkMonitor {
        constructor() {
            this.online = navigator.onLine;
            this.callbacks = [];
            this.init();
        }

        init() {
            window.addEventListener('online', () => {
                this.handleStatusChange(true);
            });

            window.addEventListener('offline', () => {
                this.handleStatusChange(false);
            });

            // Monitor connection quality
            if ('connection' in navigator) {
                navigator.connection.addEventListener('change', () => {
                    this.handleConnectionChange();
                });
            }
        }

        handleStatusChange(online) {
            this.online = online;

            // Update UI
            document.documentElement.setAttribute('data-online', online);

            // Show notification
            this.showNotification(online ?
                '🟢 Back online' :
                '🔴 You are offline'
            );

            // Trigger callbacks
            this.callbacks.forEach(callback => callback(online));

            // Dispatch event
            window.dispatchEvent(new CustomEvent('network:status', {
                detail: { online }
            }));
        }

        handleConnectionChange() {
            const connection = navigator.connection;

            window.dispatchEvent(new CustomEvent('network:connection', {
                detail: {
                    effectiveType: connection.effectiveType,
                    downlink: connection.downlink,
                    rtt: connection.rtt,
                    saveData: connection.saveData
                }
            }));
        }

        showNotification(message) {
            // Create toast notification
            const toast = document.createElement('div');
            toast.className = 'network-toast';
            toast.textContent = message;
            toast.style.cssText = `
                position: fixed;
                bottom: 20px;
                left: 50%;
                transform: translateX(-50%) translateY(100px);
                background: rgba(19, 19, 24, 0.95);
                color: white;
                padding: 12px 24px;
                border-radius: 8px;
                border: 1px solid ${this.online ? 'rgba(0, 255, 0, 0.3)' : 'rgba(255, 0, 0, 0.3)'};
                font-size: 14px;
                z-index: 10000;
                transition: transform 0.3s ease;
            `;

            document.body.appendChild(toast);

            // Animate in
            setTimeout(() => {
                toast.style.transform = 'translateX(-50%) translateY(0)';
            }, 10);

            // Remove after 3 seconds
            setTimeout(() => {
                toast.style.transform = 'translateX(-50%) translateY(100px)';
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }

        onChange(callback) {
            this.callbacks.push(callback);
        }

        isOnline() {
            return this.online;
        }
    }

    // ============================================
    // 4. PWA INSTALL PROMPT
    // ============================================

    class PWAInstaller {
        constructor() {
            this.deferredPrompt = null;
            this.init();
        }

        init() {
            // Capture install prompt
            window.addEventListener('beforeinstallprompt', (e) => {
                e.preventDefault();
                this.deferredPrompt = e;
                this.showInstallButton();
            });

            // Track installation
            window.addEventListener('appinstalled', () => {
                console.log('✅ PWA installed successfully');
                this.deferredPrompt = null;
            });
        }

        showInstallButton() {
            // Create install button
            const installBtn = document.createElement('button');
            installBtn.className = 'pwa-install-btn';
            installBtn.innerHTML = '📱 Install App';
            installBtn.style.cssText = `
                position: fixed;
                bottom: 20px;
                right: 20px;
                padding: 12px 24px;
                background: var(--gradient-lydian);
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: 600;
                cursor: pointer;
                z-index: 9999;
                box-shadow: 0 4px 20px rgba(255, 0, 51, 0.3);
                transition: transform 0.2s;
            `;

            installBtn.addEventListener('click', () => {
                this.install();
            });

            document.body.appendChild(installBtn);

            // Auto-hide after 10 seconds
            setTimeout(() => {
                installBtn.style.transform = 'translateY(100px)';
                setTimeout(() => installBtn.remove(), 300);
            }, 10000);
        }

        async install() {
            if (!this.deferredPrompt) return;

            this.deferredPrompt.prompt();

            const { outcome } = await this.deferredPrompt.userChoice;

            if (outcome === 'accepted') {
                console.log('✅ User accepted PWA install');
            } else {
                console.log('❌ User dismissed PWA install');
            }

            this.deferredPrompt = null;
        }

        isInstalled() {
            return window.matchMedia('(display-mode: standalone)').matches ||
                   window.navigator.standalone === true;
        }
    }

    // ============================================
    // 5. RESPONSIVE IMAGES OPTIMIZER
    // ============================================

    class ImageOptimizer {
        static optimizeAll() {
            // Add srcset to images
            document.querySelectorAll('img[data-src-base]').forEach(img => {
                const base = img.dataset.srcBase;
                img.srcset = `
                    ${base}-320w.webp 320w,
                    ${base}-640w.webp 640w,
                    ${base}-1024w.webp 1024w,
                    ${base}-1920w.webp 1920w
                `;
                img.sizes = '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw';
            });
        }

        static preloadCritical() {
            // Preload hero images
            const heroImages = document.querySelectorAll('[data-preload="true"]');
            heroImages.forEach(img => {
                const link = document.createElement('link');
                link.rel = 'preload';
                link.as = 'image';
                link.href = img.src || img.dataset.src;
                document.head.appendChild(link);
            });
        }
    }

    // ============================================
    // 6. AUTO-INITIALIZATION
    // ============================================

    window.LydianResponsive = {
        ResponsiveManager,
        DeviceDetector,
        NetworkMonitor,
        PWAInstaller,
        ImageOptimizer
    };

    // Initialize on DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initAll);
    } else {
        initAll();
    }

    function initAll() {
        console.log('📱 Lydian Responsive: Initializing...');

        // Initialize responsive manager
        const responsiveManager = new ResponsiveManager();
        window.responsiveManager = responsiveManager;

        // Log device capabilities
        const capabilities = DeviceDetector.getCapabilities();
        console.log('🔍 Device Capabilities:', capabilities);

        // Add classes to body
        document.body.classList.add(
            `os-${capabilities.os.toLowerCase()}`,
            `browser-${capabilities.browser.toLowerCase()}`,
            capabilities.touch ? 'has-touch' : 'no-touch',
            capabilities.retina ? 'is-retina' : 'no-retina'
        );

        // Initialize network monitor
        const networkMonitor = new NetworkMonitor();
        window.networkMonitor = networkMonitor;

        // Initialize PWA installer
        const pwaInstaller = new PWAInstaller();
        window.pwaInstaller = pwaInstaller;

        // Optimize images
        ImageOptimizer.preloadCritical();

        // Log breakpoint changes
        responsiveManager.onBreakpointChange((data) => {
            console.log(`📐 Breakpoint changed: ${data.from} → ${data.to}`);
        });

        // Log orientation changes
        responsiveManager.onOrientationChange((data) => {
            console.log(`🔄 Orientation changed: ${data.from} → ${data.to}`);
        });

        console.log('✅ Lydian Responsive: Ready');
        console.log(`📱 Current: ${responsiveManager.currentBreakpoint} (${responsiveManager.orientation})`);
    }

})();
