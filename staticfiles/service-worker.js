const CACHE_NAME = 'v1';
const CACHE_ASSETS = [
    '/',
    '/static/logo.png',
    '/static/service-worker.js',
    // Add other assets to cache as needed
];

// Install event
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('Caching assets');
                // Cache assets individually to handle failures gracefully
                return Promise.allSettled(
                    CACHE_ASSETS.map(url => 
                        fetch(url)
                            .then(response => {
                                if (response.ok) {
                                    return cache.put(url, response);
                                } else {
                                    console.warn(`Failed to cache ${url}: ${response.status}`);
                                }
                            })
                            .catch(error => {
                                console.warn(`Failed to cache ${url}:`, error);
                            })
                    )
                );
            })
            .then(() => {
                // Force activation of new service worker
                return self.skipWaiting();
            })
    );
});

// Activate event
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((name) => {
                    if (name !== CACHE_NAME) {
                        console.log('Removing old cache:', name);
                        return caches.delete(name);
                    }
                })
            );
        })
    );
});

// Fetch event
self.addEventListener('fetch', (event) => {
    event.respondWith(
        caches.match(event.request)
            .then((response) => {
                return response || fetch(event.request);
            })
    );
});
