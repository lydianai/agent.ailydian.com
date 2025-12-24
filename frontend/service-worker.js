/**
 * Lydian Agent - Service Worker
 * Progressive Web App with Offline Support
 *
 * Features:
 * - Cache-first strategy for static assets
 * - Network-first for API calls
 * - Offline fallback
 * - Background sync
 * - Push notifications (ready)
 */

const CACHE_VERSION = 'lydian-agent-v1.0.0';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const API_CACHE = `${CACHE_VERSION}-api`;

// Static assets to cache immediately
const STATIC_ASSETS = [
    '/',
    '/index.html',
    '/demo.html',
    '/features.html',
    '/static/css/responsive-mobile-first.css',
    '/static/css/global-styles.css',
    '/static/css/neon-effects.css',
    '/static/js/enhanced-lang-switcher.js',
    '/static/js/touch-gestures.js',
    '/static/js/responsive-manager.js',
    '/static/js/main.js',
    '/manifest.json',
    'https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700;800&display=swap',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css'
];

// ============================================
// INSTALL EVENT - Cache static assets
// ============================================

self.addEventListener('install', (event) => {
    console.log('🔧 Service Worker: Installing...', CACHE_VERSION);

    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then((cache) => {
                console.log('📦 Service Worker: Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => {
                console.log('✅ Service Worker: Installation complete');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('❌ Service Worker: Installation failed', error);
            })
    );
});

// ============================================
// ACTIVATE EVENT - Clean old caches
// ============================================

self.addEventListener('activate', (event) => {
    console.log('✨ Service Worker: Activating...', CACHE_VERSION);

    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        // Delete old caches
                        if (cacheName.startsWith('lydian-agent-') &&
                            cacheName !== STATIC_CACHE &&
                            cacheName !== DYNAMIC_CACHE &&
                            cacheName !== API_CACHE) {
                            console.log('🗑️  Service Worker: Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('✅ Service Worker: Activation complete');
                return self.clients.claim();
            })
    );
});

// ============================================
// FETCH EVENT - Handle requests
// ============================================

self.addEventListener('fetch', (event) => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip non-GET requests
    if (request.method !== 'GET') {
        return;
    }

    // API requests - Network first, cache fallback
    if (url.pathname.startsWith('/api/')) {
        event.respondWith(networkFirstStrategy(request, API_CACHE));
        return;
    }

    // Health check - Always network
    if (url.pathname === '/health') {
        event.respondWith(fetch(request));
        return;
    }

    // Static assets - Cache first, network fallback
    if (STATIC_ASSETS.some(asset => url.pathname === asset ||
                                    url.pathname.startsWith('/static/'))) {
        event.respondWith(cacheFirstStrategy(request, STATIC_CACHE));
        return;
    }

    // HTML pages - Network first, cache fallback
    if (request.headers.get('accept').includes('text/html')) {
        event.respondWith(networkFirstStrategy(request, DYNAMIC_CACHE));
        return;
    }

    // Everything else - Cache first
    event.respondWith(cacheFirstStrategy(request, DYNAMIC_CACHE));
});

// ============================================
// CACHING STRATEGIES
// ============================================

/**
 * Cache First Strategy
 * Try cache first, fallback to network
 */
async function cacheFirstStrategy(request, cacheName) {
    try {
        // Try cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        // Fallback to network
        const networkResponse = await fetch(request);

        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;

    } catch (error) {
        console.error('Cache first strategy failed:', error);

        // Return offline fallback
        return getOfflineFallback(request);
    }
}

/**
 * Network First Strategy
 * Try network first, fallback to cache
 */
async function networkFirstStrategy(request, cacheName) {
    try {
        // Try network
        const networkResponse = await fetch(request);

        // Cache successful responses
        if (networkResponse.ok) {
            const cache = await caches.open(cacheName);
            cache.put(request, networkResponse.clone());
        }

        return networkResponse;

    } catch (error) {
        console.log('Network failed, trying cache:', request.url);

        // Fallback to cache
        const cachedResponse = await caches.match(request);
        if (cachedResponse) {
            return cachedResponse;
        }

        // Return offline fallback
        return getOfflineFallback(request);
    }
}

/**
 * Offline Fallback
 */
function getOfflineFallback(request) {
    const url = new URL(request.url);

    // HTML fallback
    if (request.headers.get('accept').includes('text/html')) {
        return new Response(`
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Offline - Lydian Agent</title>
                <style>
                    body {
                        margin: 0;
                        padding: 0;
                        font-family: 'Inter', sans-serif;
                        background: #0a0a0f;
                        color: #ffffff;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        text-align: center;
                    }
                    .offline-container {
                        max-width: 500px;
                        padding: 2rem;
                    }
                    h1 {
                        font-size: 3rem;
                        margin-bottom: 1rem;
                    }
                    p {
                        font-size: 1.125rem;
                        color: #a0a0b8;
                        margin-bottom: 2rem;
                    }
                    button {
                        background: linear-gradient(135deg, #ff0033 0%, #ff3366 100%);
                        color: white;
                        border: none;
                        padding: 1rem 2rem;
                        border-radius: 8px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                    }
                    button:hover {
                        transform: translateY(-2px);
                    }
                </style>
            </head>
            <body>
                <div class="offline-container">
                    <h1>🔴</h1>
                    <h2>You're Offline</h2>
                    <p>It looks like you've lost your internet connection. Some features may not be available.</p>
                    <button onclick="location.reload()">Try Again</button>
                </div>
            </body>
            </html>
        `, {
            status: 503,
            statusText: 'Service Unavailable',
            headers: {
                'Content-Type': 'text/html; charset=utf-8',
                'Cache-Control': 'no-store'
            }
        });
    }

    // API fallback
    if (url.pathname.startsWith('/api/')) {
        return new Response(JSON.stringify({
            error: 'offline',
            message: 'You are currently offline. Please check your internet connection.'
        }), {
            status: 503,
            headers: {
                'Content-Type': 'application/json'
            }
        });
    }

    // Default fallback
    return new Response('Offline', {
        status: 503,
        statusText: 'Service Unavailable'
    });
}

// ============================================
// BACKGROUND SYNC (for future use)
// ============================================

self.addEventListener('sync', (event) => {
    console.log('🔄 Service Worker: Background sync', event.tag);

    if (event.tag === 'sync-data') {
        event.waitUntil(syncData());
    }
});

async function syncData() {
    // Placeholder for background sync logic
    console.log('📡 Service Worker: Syncing data...');
}

// ============================================
// PUSH NOTIFICATIONS (ready for future use)
// ============================================

self.addEventListener('push', (event) => {
    console.log('🔔 Service Worker: Push notification received');

    const options = {
        body: event.data ? event.data.text() : 'New notification from Lydian Agent',
        icon: '/static/icons/icon-192x192.png',
        badge: '/static/icons/badge-72x72.png',
        vibrate: [200, 100, 200],
        tag: 'lydian-notification',
        requireInteraction: false
    };

    event.waitUntil(
        self.registration.showNotification('Lydian Agent', options)
    );
});

self.addEventListener('notificationclick', (event) => {
    console.log('🔔 Service Worker: Notification clicked');

    event.notification.close();

    event.waitUntil(
        clients.openWindow('/')
    );
});

// ============================================
// MESSAGE HANDLER
// ============================================

self.addEventListener('message', (event) => {
    console.log('💬 Service Worker: Message received', event.data);

    if (event.data && event.data.type === 'SKIP_WAITING') {
        self.skipWaiting();
    }

    if (event.data && event.data.type === 'CACHE_URLS') {
        event.waitUntil(
            caches.open(DYNAMIC_CACHE)
                .then(cache => cache.addAll(event.data.urls))
        );
    }
});

console.log('✅ Service Worker: Loaded', CACHE_VERSION);
