/**
 * Service Worker for PIMS_AlgoHCP Recognizer Web App (v2.1)
 * Network-First strategy for all requests to ensure fresh code is always served.
 */

const CACHE_NAME = "pims-algo-hcp-v2.1";

// Install Event - Skip waiting immediately
self.addEventListener("install", (event) => {
  self.skipWaiting();
});

// Activate Event - Purge ALL old caches
self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cache) => {
          if (cache !== CACHE_NAME) {
            console.log("[Service Worker] Purging old cache:", cache);
            return caches.delete(cache);
          }
        })
      );
    }).then(() => self.clients.claim())
  );
});

// Fetch Event - ALWAYS Network-First for everything
self.addEventListener("fetch", (event) => {
  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // Cache successful GET responses for offline fallback
        if (networkResponse && networkResponse.status === 200 && event.request.method === "GET") {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Offline fallback: try cache
        return caches.match(event.request).then((cachedResponse) => {
          return cachedResponse || new Response("Offline", { status: 503 });
        });
      })
  );
});
