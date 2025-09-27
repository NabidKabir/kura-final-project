// Minimal Service Worker - only cache GET requests
const CACHE_NAME = 'kura-recycling-v1';

self.addEventListener('install', (event) => {
  console.log('Service Worker: Installed');
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activated');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log('Service Worker: Clearing Old Cache');
            return caches.delete(cache);
          }
        })
      );
    })
  );
});

self.addEventListener('fetch', (event) => {
  // Only handle GET requests - don't cache POST requests
  if (event.request.method !== 'GET') {
    return; // Let the browser handle POST requests normally
  }

  // Only cache static resources
  if (event.request.url.includes('/chat') ||
      event.request.url.includes('/api/')) {
    return; // Don't cache API endpoints
  }

  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request).then((fetchResponse) => {
        const responseClone = fetchResponse.clone();

        caches.open(CACHE_NAME).then((cache) => {
          cache.put(event.request, responseClone);
        });

        return fetchResponse;
      });
    }).catch(() => {
      // Fallback for offline
      if (event.request.destination === 'document') {
        return caches.match('/');
      }
    })
  );
});